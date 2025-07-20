from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class Server(Base):
    """Модель для хранения информации о SFTP серверах"""
    __tablename__ = "servers"

    id       = Column(Integer, primary_key=True, index=True)
    hostname = Column(String(100), nullable=False, comment="Адрес сервера")
    port     = Column(Integer, nullable=False, default=22, comment="Порт для SFTP")
    username = Column(String(100), nullable=False, comment="Имя пользователя для SFTP")
    password = Column(String(100), nullable=False, comment="Пароль для SFTP")

    # Связь с файлами (один ко многим)
    files = relationship("File", back_populates="server")

    def __repr__(self):
        return f"<Server(id={self.id}, hostname='{self.hostname}', port={self.port})>"

class File(Base):
    """Модель для хранения информации о файлах"""
    __tablename__ = "files"

    id         = Column(Integer, primary_key=True, index=True)
    servers_id = Column(Integer, ForeignKey("servers.id"), nullable=False, comment="Внешний ключ на таблицу servers")
    filename   = Column(String(500), nullable=False, comment="Имя файла")
    status     = Column(String(50), nullable=False, default="новый", comment="Статус обработки")
    timestamp  = Column(DateTime, nullable=False, default=datetime.now(timezone.utc), comment="Время создания файла")

    # Связь с сервером (многие к одному)
    server = relationship("Server", back_populates="files")

    def __repr__(self):
        return f"<File(id={self.id}, filename='{self.filename}', status='{self.status}')>"
