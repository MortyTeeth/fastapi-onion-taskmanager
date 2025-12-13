from fastapi import FastAPI
import logging

from auth_service.src.api.v1 import api_router
from auth_service.src.database import engine
from auth_service.src.models.base import Base

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Auth Service", docs_url="/docs")

app.include_router(api_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    logger.info("Создаём таблицы auth_db...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Auth Service готов!")


@app.get("/")
async def root():
    return {"service": "auth-service", "status": "running"}