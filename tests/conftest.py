import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.utils.unit_of_work import get_uow, UnitOfWork
from src.models.base import Base
from src.models.user import User
from src.models.task import Board


DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        user = User(id=1, username="testuser", email="test@example.com", hashed_password="fake")
        board = Board(id=1, name="Test Board", owner_id=1)
        session.add_all([user, board])
        await session.commit()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(autouse=True)
async def client():
    connection = await engine.connect()
    transaction = await connection.begin()
    session = TestingSessionLocal(bind=connection)

    async def override_get_uow():
        uow = UnitOfWork()
        uow.session = session
        uow.user.session = session
        uow.task.session = session
        yield uow

    app.dependency_overrides[get_uow] = override_get_uow

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

    await transaction.rollback()
    await connection.close()
    app.dependency_overrides.clear()