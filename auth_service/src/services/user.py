from passlib.context import CryptContext
from auth_service.src.models.user import User
from auth_service.src.schemas.user import UserCreateRequest, UserResponse

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    async def create_user(self, uow, data: UserCreateRequest):
        hashed_password = pwd_context.hash(data.password[:72])
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password
        )
        await uow.user.add(user)
        await uow.commit()
        await uow.refresh(user)
        return UserResponse.from_orm(user)

    async def get_by_id(self, uow, user_id: int):
        return await uow.user.get_by_id(user_id)
