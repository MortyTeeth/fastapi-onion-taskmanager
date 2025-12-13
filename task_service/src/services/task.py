from fastapi import HTTPException
from typing import List, Optional, Any
import inspect

from task_service.src.models.task import Task, Board
from task_service.src.models.enums import TaskStatus
from task_service.src.schemas.task.task import TaskCreateRequest, TaskUpdateRequest


class TaskService:
    async def create_task(self, uow, data: TaskCreateRequest, current_user_id: int) -> Task:
        """
        Создаёт задачу. current_user_id — это ID из JWT.
        """

        if not data.board_id:
            raise HTTPException(status_code=400, detail="board_id обязателен")

        board = await uow.session.get(Board, data.board_id)
        if not board:
            raise HTTPException(status_code=404, detail="Доска не найдена")

        # Создаём задачу
        task = Task(
            title=data.title,
            description=data.description,
            status=data.status or TaskStatus.TODO,
            column=data.column,
            group=data.group,
            author_id=current_user_id,
            assignee_id=data.assignee_id,
            board_id=data.board_id,
            sprint_id=data.sprint_id,
        )

        await uow.task.add(task)
        await self._commit(uow)
        return await uow.task.get_by_id(task.id)

    async def list_tasks(
        self,
        author_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[int] = None,
        uow=None,
    ) -> List[Task]:
        status_str = status.value if status else None
        return await uow.task.list(
            author_id=author_id,
            status=status_str,
            assignee_id=assignee_id,
        )

    async def update_task(
        self,
        task_id: int,
        data: TaskUpdateRequest,
        uow,
        updater_id: Optional[int] = None,
    ) -> Task | None:
        task = await uow.task.get_by_id(task_id)
        if not task:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await self._commit(uow)
        return await uow.task.get_by_id(task_id)

    async def delete_task(
        self,
        task_id: int,
        uow,
        deleter_id: Optional[int] = None,
    ) -> bool:
        task = await uow.task.get_by_id(task_id)
        if not task:
            return False

        await uow.task.delete(task)
        await self._commit(uow)
        return True

    async def _commit(self, uow: Any) -> None:
        commit_func = uow.commit
        if inspect.iscoroutinefunction(commit_func):
            await commit_func()
        else:
            commit_func()