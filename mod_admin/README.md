# Admin Panel - SFTP Monitor

Микросервис админки для мониторинга SFTP серверов и файлов.

## Функциональность

- Просмотр списка SFTP серверов
- Просмотр списка файлов с их статусами
- Современный веб-интерфейс

## Запуск

### Через Docker Compose (рекомендуется)

```bash
cd mod_admin
docker-compose up -d
```

Админка будет доступна по адресу: http://localhost:8000

### Локальный запуск

```bash
cd mod_admin
pip install -r requirements.txt
python main.py
```

## Структура проекта

```
mod_admin/
├── main.py              # FastAPI приложение
├── requirements.txt     # Зависимости Python
├── Dockerfile          # Docker образ
├── docker-compose.yml  # Docker Compose конфигурация
├── templates/          # HTML шаблоны
│   └── admin.html      # Главная страница админки
└── static/             # Статические файлы (CSS, JS)
```

## API Endpoints

- `GET /` - Главная страница админки с таблицами серверов и файлов

## База данных

Админка подключается к PostgreSQL базе данных и использует модели из `../base/models.py`.

## Переменные окружения

- `DATABASE_URL` - URL подключения к базе данных (по умолчанию: postgresql://user:password@db:5432/database) 