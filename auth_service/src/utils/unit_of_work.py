from sqlalchemy.ext.asyncio import AsyncSession
from auth_service.src.database import AsyncSessionLocal
from auth_service.src.repositories.user import UserRepository


class UnitOfWork:
    def __init__(self):
        self.session: AsyncSession = AsyncSessionLocal()
        self.user = UserRepository(self.session)

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


async def get_uow():
    async with UnitOfWork() as uow:
        yield uow