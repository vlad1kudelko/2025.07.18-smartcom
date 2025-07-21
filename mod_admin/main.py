from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Импортируем модели
import importlib.util
spec = importlib.util.spec_from_file_location("models", "base_models.py")
models = importlib.util.module_from_spec(spec)
spec.loader.exec_module(models)
Server = models.Server
File = models.File

app = FastAPI(title="Admin Panel", version="1.0.0")

# Настройки базы данных
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@db:5432/database")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Настройки шаблонов
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def admin_panel(request: Request):
    """Главная страница админки с таблицами серверов и файлов"""
    db = SessionLocal()

    try:
        # Получаем данные из базы
        servers = db.query(Server).all()
        files = db.query(File).all()

        return templates.TemplateResponse("admin.html", {
            "request": request,
            "servers": servers,
            "files": files
        })
    finally:
        db.close()

@app.get("/api/data")
async def get_data():
    """API endpoint для получения данных в формате JSON"""
    db = SessionLocal()

    try:
        # Получаем данные из базы
        servers = db.query(Server).all()
        files = db.query(File).all()

        # Преобразуем в JSON-совместимый формат
        servers_data = []
        for server in servers:
            servers_data.append({
                "id": server.id,
                "hostname": server.hostname,
                "port": server.port,
                "username": server.username
            })

        files_data = []
        for file in files:
            files_data.append({
                "id": file.id,
                "servers_id": file.servers_id,
                "filename": file.filename,
                "status": file.status,
                "timestamp": file.timestamp.strftime('%Y-%m-%d %H:%M:%S') if file.timestamp else 'N/A'
            })

        return JSONResponse({
            "servers": servers_data,
            "files": files_data
        })
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
