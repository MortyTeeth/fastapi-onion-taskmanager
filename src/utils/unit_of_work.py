from sqlalchemy.ext.asyncio import AsyncSession
from src.database.db import AsyncSessionLocal
from src.repositories.user_repository import UserRepository
from src.repositories.task_repository import TaskRepository


class UnitOfWork:
    def __init__(self):
        self.session = AsyncSessionLocal()
        self.user = UserRepository(self.session)
        self.task = TaskRepository(self.session)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is None:
            await self.session.commit()
        else:
            await self.session.rollback()
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


async def get_uow() -> UnitOfWork:
    """Зависимость для FastAPI"""
    async with UnitOfWork() as uow:
        yield uow