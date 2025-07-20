FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости для paramiko
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY . .

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 watchdog && chown -R watchdog:watchdog /app
USER watchdog

# Запускаем приложение
CMD ["python", "main.py"] 