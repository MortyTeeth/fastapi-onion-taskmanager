from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from task_service.src.core.config import settings
from task_service.src.models.base import Base

engine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session


