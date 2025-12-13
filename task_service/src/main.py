from fastapi import FastAPI
import logging

from task_service.src.api.v1 import api_router
from task_service.src.database import engine
from task_service.src.models.base import Base
from task_service.src.broker.rpc_server import start_rpc_server

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Task Service", version="1.0.0", docs_url="/docs")
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    logger.info("Создаём таблицы...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Таблицы созданы")

    logger.info("Запускаем RabbitMQ RPC-сервер...")
    try:
        await start_rpc_server()
        logger.info("RPC-сервер успешно запущен")
    except Exception as e:
        logger.error(f"Не удалось подключиться к RabbitMQ: {e}")

@app.get("/")
async def root():
    return {"service": "task-service", "status": "alive"}