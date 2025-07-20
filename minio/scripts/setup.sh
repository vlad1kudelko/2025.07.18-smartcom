#!/bin/bash

# Скрипт для настройки MinIO
# Выполняется автоматически при запуске контейнера

echo "Setting up MinIO..."

# Ждем запуска MinIO
sleep 10

# Настраиваем клиент
mc alias set myminio http://minio:9000 minioadmin minioadmin

# Создаем бакет для файлов SFTP
mc mb myminio/sftp-files --ignore-existing

# Устанавливаем публичный доступ к бакету (для чтения)
mc policy set public myminio/sftp-files

# Создаем дополнительные бакеты если нужно
mc mb myminio/backups --ignore-existing
mc mb myminio/temp --ignore-existing

echo "MinIO setup completed successfully!"
echo "Access MinIO Console at: http://localhost:9001"
echo "Access MinIO API at: http://localhost:9000" 