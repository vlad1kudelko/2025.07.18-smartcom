# MinIO Storage Service

Микросервис для хранения файлов, загруженных с SFTP серверов.

## Описание

MinIO - это совместимое с S3 хранилище объектов для хранения файлов. В данном проекте используется для:
- Хранения файлов, скачанных с SFTP серверов
- Предоставления доступа к файлам через веб-интерфейс
- API для загрузки и скачивания файлов

## Запуск

```bash
cd minio
docker compose up -d
```

## Доступ

### MinIO API
- **URL**: http://localhost:9000
- **Access Key**: minioadmin
- **Secret Key**: minioadmin

### MinIO Console (веб-интерфейс)
- **URL**: http://localhost:9001
- **Логин**: minioadmin
- **Пароль**: minioadmin

## Структура

### Бакет `sftp-files`
Автоматически создается при запуске и содержит:
- Файлы, загруженные с SFTP серверов
- Организованные по датам и серверам

### Настройки
- **Порт API**: 9000
- **Порт Console**: 9001
- **Данные**: сохраняются в Docker volume `minio_data`

## Использование в проекте

### Python клиент
```python
from minio import Minio

client = Minio(
    "localhost:9000",
    access_key="minioadmin",
    secret_key="minioadmin",
    secure=False
)

# Загрузка файла
client.fput_object("sftp-files", "filename.txt", "/path/to/file.txt")

# Скачивание файла
client.fget_object("sftp-files", "filename.txt", "/local/path/file.txt")
```

### URL для прямого доступа
Файлы доступны по URL:
```
http://localhost:9000/sftp-files/filename.txt
```

## Переменные окружения

- `MINIO_ROOT_USER` - имя пользователя (по умолчанию: minioadmin)
- `MINIO_ROOT_PASSWORD` - пароль (по умолчанию: minioadmin)

## Мониторинг

MinIO предоставляет встроенные метрики и мониторинг через веб-консоль на порту 9001. 