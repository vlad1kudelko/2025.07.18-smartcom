# Тестовый SFTP Сервер

Тестовый SFTP сервер для разработки и тестирования микросервисов мониторинга.

## Описание

Используется образ `atmoz/sftp` для создания простого SFTP сервера с тестовыми файлами.

## Запуск

```bash
cd sftp_servers
docker compose up -d
```

## Доступ

### SFTP Подключение
- **Хост**: localhost
- **Порт**: 2222
- **Пользователь**: testuser
- **Пароль**: password
- **UID**: 1001

### Команда подключения
```bash
sftp -P 2222 testuser@localhost
```

### Python подключение
```python
import paramiko

transport = paramiko.Transport(('localhost', 2222))
transport.connect(username='testuser', password='password')
sftp = paramiko.SFTPClient.from_transport(transport)

# Список файлов
files = sftp.listdir('/home/testuser/upload')
print(files)

# Скачивание файла
sftp.get('/home/testuser/upload/large_file1.bin', 'local_large_file1.bin')

sftp.close()
transport.close()
```

## Структура

### Папки
- `/home/testuser/upload/` - основная папка для загрузки
- `/home/testuser/upload/test_files/` - тестовые файлы

### Тестовые файлы
Автоматически создаются при запуске:
- `large_file1.bin` - ~1GB случайных данных
- `large_file2.bin` - ~1GB случайных данных
- `large_file3.bin` - ~1GB случайных данных

**Примечание**: Создание файлов может занять несколько минут из-за большого размера.

## Настройка для микросервисов

### В базе данных
```sql
INSERT INTO servers (hostname, port, username, password) 
VALUES ('localhost', 2222, 'testuser', 'password');
```

### В конфигурации
```yaml
sftp:
  host: localhost
  port: 2222
  username: testuser
  password: password
  remote_path: /home/testuser/upload
```

## Мониторинг

### Логи сервера
```bash
docker compose logs sftp-server
```

### Проверка состояния
```bash
docker compose ps
```

### Подключение к контейнеру
```bash
docker compose exec sftp-server sh
```

## Безопасность

⚠️ **ВНИМАНИЕ**: Это тестовый сервер с простыми учетными данными!
- Используйте только для разработки
- Не используйте в продакшене
- Пароль хранится в открытом виде

## Добавление новых файлов

Для добавления новых тестовых файлов отредактируйте команду в `sftp-client`:

```yaml
command: >
  sh -c "
    apk add --no-cache openssh-client &&
    sleep 5 &&
    echo 'Creating test files...' &&
    dd if=/dev/urandom of=/test_files/large_file1.bin bs=1M count=1024 &&
    dd if=/dev/urandom of=/test_files/large_file2.bin bs=1M count=1024 &&
    dd if=/dev/urandom of=/test_files/large_file3.bin bs=1M count=1024 &&
    echo 'Large test files created successfully!' &&
    tail -f /dev/null
  "
``` 