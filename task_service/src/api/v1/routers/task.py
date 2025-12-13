from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from task_service.src.services.task import TaskService
from task_service.src.schemas.task.task import TaskCreateRequest, TaskUpdateRequest, TaskResponse
from task_service.src.models.enums import TaskStatus
from task_service.src.utils.unit_of_work import UnitOfWork, get_uow
from task_service.src.api.v1.dependencies import get_current_user_id

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateRequest,
    current_user_id: int = Depends(get_current_user_id),
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):

    task_data.author_id = current_user_id
    return await service.create_task(uow, task_data)


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    author_id: Optional[int] = Query(None),
    assignee_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    status_enum: Optional[TaskStatus] = None
    if status:
        try:
            status_enum = TaskStatus(status.strip().upper())
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Неверный статус. Допустимые: TODO, IN_PROGRESS, DONE"
            )

    return await service.list_tasks(
        author_id=author_id,
        assignee_id=assignee_id,
        status=status_enum,
        uow=uow,
    )


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdateRequest,
    current_user_id: int = Depends(get_current_user_id),
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):

    task = await service.update_task(task_id, task_update, uow, updater_id=current_user_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    current_user_id: int = Depends(get_current_user_id),
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    success = await service.delete_task(task_id, uow, deleter_id=current_user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return