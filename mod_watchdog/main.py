import os
import sys
import time
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from typing import List, Set
import paramiko
import stat

# Импортируем модели
import importlib.util
spec = importlib.util.spec_from_file_location("models", "base_models.py")
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/database")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

SFTP_PATH = os.getenv("SFTP_PATH", "/upload/test_files")

class SFTPWatchdog:
    def __init__(self):
        self.db = SessionLocal()
        self.scan_interval = 5  # секунд
        
    def get_all_servers(self) -> List[models.Server]:
        """Получить все серверы из базы данных"""
        try:
            return self.db.query(models.Server).all()
        except Exception as e:
            logger.error(f"Ошибка при получении серверов: {e}")
            return []
    
    def get_existing_files(self, server_id: int) -> Set[str]:
        """Получить список файлов, которые уже есть в базе для данного сервера"""
        try:
            files = self.db.query(models.File).filter(models.File.servers_id == server_id).all()
            return {file.filename for file in files}
        except Exception as e:
            logger.error(f"Ошибка при получении файлов для сервера {server_id}: {e}")
            return set()
    
    def connect_to_sftp(self, server: models.Server) -> paramiko.SFTPClient:
        """Подключиться к SFTP серверу"""
        try:
            transport = paramiko.Transport((server.hostname, server.port))
            transport.connect(username=server.username, password=server.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            logger.info(f"Успешно подключился к серверу {server.hostname}:{server.port}")
            return sftp, transport
        except Exception as e:
            logger.error(f"Ошибка подключения к серверу {server.hostname}:{server.port}: {e}")
            return None, None
    
    def scan_sftp_directory(self, sftp: paramiko.SFTPClient, path: str = None) -> List[str]:
        """Сканировать директорию SFTP и получить список файлов"""
        if path is None:
            path = SFTP_PATH
        try:
            files = []
            for item in sftp.listdir_attr(path):
                if not stat.S_ISDIR(item.st_mode):  # Проверяем, что это не директория (например, файл)
                    files.append(item.filename)
            logger.info(f"Найдено {len(files)} файлов в {path}")
            return files
        except Exception as e:
            logger.error(f"Ошибка при сканировании директории {path}: {e}")
            return []
    
    def add_file_to_database(self, server_id: int, filename: str) -> bool:
        """Добавить файл в базу данных"""
        try:
            new_file = models.File(
                servers_id=server_id,
                filename=filename,
                status="новый",
                timestamp=datetime.now()
            )
            self.db.add(new_file)
            self.db.commit()
            logger.info(f"Добавлен файл {filename} для сервера {server_id}")
            return True
        except Exception as e:
            logger.error(f"Ошибка при добавлении файла {filename} в базу: {e}")
            self.db.rollback()
            return False
    
    def scan_server(self, server: models.Server):
        """Сканировать один сервер"""
        logger.info(f"Сканирую сервер {server.hostname}:{server.port}")
        # Подключаемся к SFTP
        sftp, transport = self.connect_to_sftp(server)
        if not sftp:
            return
        try:
            # Получаем список файлов на сервере
            remote_files = self.scan_sftp_directory(sftp)
            # Получаем список файлов, которые уже есть в базе
            existing_files = self.get_existing_files(server.id)
            # Находим новые файлы
            new_files = set(remote_files) - existing_files
            if new_files:
                logger.info(f"Найдено {len(new_files)} новых файлов на сервере {server.hostname}")
                # Добавляем новые файлы в базу
                for filename in new_files:
                    self.add_file_to_database(server.id, filename)
            else:
                logger.info(f"Новых файлов на сервере {server.hostname} не найдено")
        finally:
            # Закрываем соединение
            if transport:
                transport.close()
    
    def scan_all_servers(self):
        """Сканировать все серверы"""
        logger.info("Начинаю сканирование всех серверов")
        
        servers = self.get_all_servers()
        if not servers:
            logger.warning("Серверы не найдены в базе данных")
            return False
        logger.info(f"Найдено {len(servers)} серверов для сканирования")
        for server in servers:
            self.scan_server(server)
        return True
    
    def run(self):
        """Основной цикл работы watchdog"""
        logger.info("Запуск SFTP Watchdog")
        while True:
            try:
                has_servers = self.scan_all_servers()
                if not has_servers:
                    logger.info(f"Нет серверов для мониторинга. Ожидание {self.scan_interval} секунд...")
                    time.sleep(self.scan_interval)
                    continue
                logger.info(f"Сканирование завершено. Ожидание {self.scan_interval} секунд...")
                time.sleep(self.scan_interval)
            except KeyboardInterrupt:
                logger.info("Получен сигнал остановки")
                break
            except Exception as e:
                logger.error(f"Ошибка в основном цикле: {e}")
                time.sleep(self.scan_interval)
        self.db.close()
        logger.info("SFTP Watchdog остановлен")

if __name__ == "__main__":
    watchdog = SFTPWatchdog()
    watchdog.run()