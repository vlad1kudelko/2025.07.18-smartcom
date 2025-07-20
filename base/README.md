# Базовая структура проекта

Этот модуль содержит общие компоненты для всех микросервисов:
- Модели данных (SQLAlchemy)
- Настройки базы данных
- Миграции (Alembic)

## Структура файлов

```
base/
├── models.py              # Все модели данных
├── alembic/               # Миграции базы данных
│   ├── env.py             # Настройки окружения
│   ├── script.py.mako     # Шаблон миграций
│   └── versions/          # Файлы миграций
├── database.py            # Настройки подключения к БД
├── alembic.ini            # Конфигурация Alembic
├── requirements.txt       # Зависимости
└── docker-compose.yml     # Docker конфигурация
```

## Модели данных

### Server (Сервер)
- `id` - уникальный идентификатор
- `hostname` - адрес сервера
- `port` - порт для SFTP (по умолчанию 22)
- `username` - имя пользователя для SFTP
- `password` - пароль для SFTP

### File (Файл)
- `id` - уникальный идентификатор
- `servers_id` - внешний ключ на таблицу servers
- `filename` - имя файла
- `status` - статус обработки ("новый", "в процессе", "обработан", "ошибка")
- `timestamp` - время создания файла

## Установка и настройка

1. Установите зависимости:
```bash
pip install -r requirements.txt
```

2. Запустите PostgreSQL:
```bash
docker-compose up -d
```

3. Создайте первую миграцию:
```bash
alembic revision --autogenerate -m "Initial migration"
```

4. Примените миграции:
```bash
alembic upgrade head
```

## Команды Alembic

- `alembic current` - показать текущую версию
- `alembic history` - показать историю миграций
- `alembic upgrade head` - применить все миграции
- `alembic downgrade -1` - откатить последнюю миграцию
- `alembic revision --autogenerate -m "Описание"` - создать новую миграцию

## Использование в микросервисах

Для использования моделей в других модулях:

```python
from base.models import Server, File
from base.database import get_db

# Получение сессии БД
db = next(get_db())

# Работа с моделями
servers = db.query(Server).all()
files = db.query(File).filter(File.status == "новый").all()
``` 