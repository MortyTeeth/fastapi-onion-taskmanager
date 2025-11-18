from fastapi import APIRouter

from .routers.tasks import router as task_router
from .routers.users import router as user_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(task_router, prefix="/tasks", tags=["tasks"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])