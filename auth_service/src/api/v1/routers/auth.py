from fastapi import APIRouter, Depends, HTTPException, status
from auth_service.src.schemas.user import UserCreateRequest, UserResponse
from auth_service.src.schemas.token import Token
from auth_service.src.services.auth import AuthService
from auth_service.src.utils.unit_of_work import get_uow
from auth_service.src.broker.event_publisher import publish_user_registered

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreateRequest, uow=Depends(get_uow)):
    auth_service = AuthService()
    user = await auth_service.register_user(uow, user_data)


    await publish_user_registered(user.id, user.email)

    return user


@router.post("/login", response_model=Token)
async def login(username: str, password: str, uow=Depends(get_uow)):
    auth_service = AuthService()
    user = await auth_service.authenticate_user(uow, username, password)
    tokens = auth_service.create_tokens(user.id)
    return tokens
