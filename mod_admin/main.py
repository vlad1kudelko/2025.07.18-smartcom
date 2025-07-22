from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse
from fastapi import status
from fastapi import HTTPException
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

@app.post("/api/servers")
async def add_server(hostname: str = Form(...), port: int = Form(...), username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        new_server = Server(hostname=hostname, port=port, username=username, password=password)
        db.add(new_server)
        db.commit()
        db.refresh(new_server)
        return {"success": True, "server": {"id": new_server.id, "hostname": new_server.hostname, "port": new_server.port, "username": new_server.username}}
    finally:
        db.close()

@app.put("/api/servers/{server_id}")
async def update_server(server_id: int, hostname: str = Form(...), port: int = Form(...), username: str = Form(...), password: str = Form(...)):
    db = SessionLocal()
    try:
        server = db.query(Server).filter(Server.id == server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        server.hostname = hostname
        server.port = port
        server.username = username
        server.password = password
        db.commit()
        return {"success": True}
    finally:
        db.close()

@app.delete("/api/servers/{server_id}")
async def delete_server(server_id: int):
    db = SessionLocal()
    try:
        server = db.query(Server).filter(Server.id == server_id).first()
        if not server:
            raise HTTPException(status_code=404, detail="Server not found")
        db.delete(server)
        db.commit()
        return {"success": True}
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
