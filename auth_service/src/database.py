from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession

from auth_service.src.core.config import settings


engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)


AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session