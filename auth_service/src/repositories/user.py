from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.src.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_username_or_email(self, username: str, email: str) -> User | None:
        result = await self.session.execute(
            select(User).where(or_(User.username == username, User.email == email))
        )
        return result.scalar_one_or_none()

    async def add(self, user: User):
        self.session.add(user)