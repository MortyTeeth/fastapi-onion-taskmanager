from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from src.services.task_service import TaskService
from src.schemas.task.task import TaskCreateRequest, TaskUpdateRequest, TaskResponse
from src.models.enums import TaskStatus
from src.utils.unit_of_work import UnitOfWork, get_uow


router = APIRouter(tags=["tasks"])



def get_fake_current_user():
    class FakeUser:
        id = 1
    return FakeUser()


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateRequest,
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
    current_user = Depends(get_fake_current_user),
):
    return await service.create_task(uow, task_data, current_user)


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    author_id: Optional[int] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    assignee_id: Optional[int] = Query(None),
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    tasks = await service.list_tasks(
        author_id=author_id,
        assignee_id=assignee_id,
        status=status.value if status else None,
        uow=uow,
    )
    return tasks


@router.get("/", response_model=List[TaskResponse])
async def get_tasks(
    author_id: Optional[int] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    assignee_id: Optional[int] = Query(None),
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    return await service.list_tasks(author_id, assignee_id, status, uow)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: int,
    task_update: TaskUpdateRequest,
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    task = await service.update_task(task_id, task_update, uow)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    uow: UnitOfWork = Depends(get_uow),
    service: TaskService = Depends(),
):
    success = await service.delete_task(task_id, uow)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")