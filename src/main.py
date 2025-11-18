from fastapi import FastAPI
from src.api.v1 import api_router
from src.database import async_engine as engine
from src.models.base import Base

app = FastAPI(
    title="TaskManager API",
    description="Асинхронный таск-менеджер на FastAPI + Onion Architecture + UoW",
    version="1.0.0"
)

app.include_router(api_router)

@app.on_event("startup")
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "API работает! Документация: /docs"}