from datetime import timedelta

from fastapi import HTTPException, status

from auth_service.src.schemas.user import UserCreateRequest, UserResponse
from auth_service.src.models.user import User
from auth_service.src.core.security import get_password_hash, create_access_token, verify_password
from auth_service.src.core.config import settings


class AuthService:
    async def register_user(self, uow, data: UserCreateRequest) -> UserResponse:
        existing = await uow.user.get_by_username_or_email(data.username, data.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already registered"
            )

        hashed_password = get_password_hash(data.password)
        user = User(
            username=data.username,
            email=data.email,
            hashed_password=hashed_password
        )
        await uow.user.add(user)
        await uow.commit()
        await uow.refresh(user)

        return UserResponse.model_validate(user)

    async def authenticate_user(self, uow, username: str, password: str):
        user = await uow.user.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    def create_tokens(self, user_id: int):
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user_id)},
            expires_delta=access_token_expires
        )
        return {"access_token": access_token, "token_type": "bearer"}
