
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth_service.src.api.v1.dependencies import oauth2_scheme
from auth_service.src.core.security import decode_access_token
from auth_service.src.utils.unit_of_work import UnitOfWork
from auth_service.src.broker.rpc_client import get_user_task_stats

router = APIRouter(prefix="/user", tags=["user"])


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    payload = decode_access_token(token)
    return int(payload["sub"])


@router.get("/info/")
async def user_info(user_id: int = Depends(get_current_user_id)):
    async with UnitOfWork() as uow:
        user = await uow.user.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

    try:
        stats = await get_user_task_stats(user_id)
    except Exception as e:
        stats = {"executor_tasks_count": 0, "watcher_tasks_count": 0}

    return {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "tasks_as_executor": stats.get("executor_tasks_count", 0),
        "tasks_as_watcher": stats.get("watcher_tasks_count", 0),
    }
