from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.user.user import UserCreateRequest, UserResponse
from src.services.user_service import UserService
from src.utils.unit_of_work import get_uow

router = APIRouter()

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
        user_data: UserCreateRequest,
        uow=Depends(get_uow)
):
    user = await UserService().create_user(uow, user_data)
    return user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, uow=Depends(get_uow)):
    user = await UserService().get_by_id(uow, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user