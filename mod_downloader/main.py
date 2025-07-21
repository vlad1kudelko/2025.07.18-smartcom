import os
import sys
import logging
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List
import paramiko
from minio import Minio
from celery import Celery
import pika
import importlib.util

# Импорт моделей
spec = importlib.util.spec_from_file_location("models", "base_models.py")
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

# Логирование
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Настройки
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/database")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "sftp-files")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672//")
SFTP_PATH = os.getenv("SFTP_PATH", "/upload/test_files")

# SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Celery
celery_app = Celery('downloader', broker=RABBITMQ_URL, backend='rpc://')

# MinIO
minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# RabbitMQ (для уведомлений)
def send_amqp_message(message: dict):
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        channel = connection.channel()
        channel.queue_declare(queue='file_events', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='file_events',
            body=str(message).encode('utf-8'),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        logger.info(f"AMQP сообщение отправлено: {message}")
    except Exception as e:
        logger.error(f"Ошибка отправки AMQP сообщения: {e}")

# Celery задача
@celery_app.task(name="main.process_file", bind=True, max_retries=3)
def process_file(self, file_id: int):
    db = SessionLocal()
    try:
        file = db.query(models.File).filter(models.File.id == file_id).first()
        if not file:
            logger.error(f"Файл с id={file_id} не найден в базе")
            return
        server = db.query(models.Server).filter(models.Server.id == file.servers_id).first()
        if not server:
            logger.error(f"Сервер с id={file.servers_id} не найден в базе")
            return
        logger.info(f"Начинаю скачивание файла {file.filename} с сервера {server.hostname}:{server.port}")
        # Скачиваем файл по SFTP
        transport = paramiko.Transport((server.hostname, server.port))
        transport.connect(username=server.username, password=server.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        local_path = f"/tmp/{file.filename}"
        sftp.get(os.path.join(SFTP_PATH, file.filename), local_path)
        sftp.close()
        transport.close()
        logger.info(f"Файл {file.filename} скачан во временную папку")
        # Загружаем файл в MinIO
        minio_client.fput_object(MINIO_BUCKET, file.filename, local_path)
        logger.info(f"Файл {file.filename} загружен в MinIO бакет {MINIO_BUCKET}")
        # Меняем статус файла в базе
        file.status = "обработан"
        file.timestamp = datetime.now()
        db.commit()
        logger.info(f"Статус файла {file.filename} обновлен на 'обработан'")
        # Отправляем уведомление в RabbitMQ
        send_amqp_message({
            "event": "file_processed",
            "file_id": file.id,
            "filename": file.filename,
            "timestamp": file.timestamp.isoformat()
        })
        # Удаляем временный файл
        os.remove(local_path)
    except Exception as e:
        logger.error(f"Ошибка обработки файла id={file_id}: {e}")
        # Меняем статус на 'ошибка'
        file = db.query(models.File).filter(models.File.id == file_id).first()
        if file:
            file.status = "ошибка"
            db.commit()
        self.retry(exc=e, countdown=10)
    finally:
        db.close()

# Основной цикл: ищет новые файлы и ставит задачи в Celery
def main_loop():
    logger.info("Запуск downloader...")
    while True:
        db = SessionLocal()
        try:
            new_files: List[models.File] = db.query(models.File).filter(models.File.status == "новый").all()
            for file in new_files:
                logger.info(f"Добавляю задачу на обработку файла {file.filename} (id={file.id}) в Celery")
                file.status = "в процессе"
                db.commit()
                process_file.delay(file.id)
            time.sleep(5)
        except Exception as e:
            logger.error(f"Ошибка в основном цикле: {e}")
            time.sleep(5)
        finally:
            db.close()

if __name__ == "__main__":
    main_loop() 