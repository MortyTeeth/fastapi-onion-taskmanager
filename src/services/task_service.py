from fastapi import HTTPException
from typing import List, Optional

from src.models.task import Task, Board
from src.models.user import User
from src.models.enums import TaskStatus
from src.schemas.task.task import TaskCreateRequest, TaskUpdateRequest


class TaskService:
    async def create_task(self, uow, data: TaskCreateRequest, current_user: User) -> Task:
        """
        Создаёт задачу. Автор — всегда текущий авторизованный пользователь.
        """
        if data.assignee_id:
            assignee = await uow.session.get(User, data.assignee_id)
            if not assignee:
                raise HTTPException(404, "Исполнитель не найден")

        if data.board_id is None:
            raise HTTPException(400, "board_id обязателен")

        board = await uow.session.get(Board, data.board_id)
        if not board:
            raise HTTPException(404, "Доска не найдена")

        task = Task(
            title=data.title,
            description=data.description,
            status=data.status or TaskStatus.TODO,
            column=data.column,
            group=data.group,
            author_id=current_user.id,
            assignee_id=data.assignee_id,
            board_id=data.board_id,
            sprint_id=data.sprint_id,
        )

        await uow.task.add(task)
        await uow.commit()

        created_task = await uow.task.get_by_id(task.id)
        if not created_task:
            raise HTTPException(500, "Задача создана, но не удалось её прочитать")

        return created_task

    async def get_task(self, task_id: int, uow) -> Optional[Task]:
        return await uow.task.get_by_id(task_id)

    async def list_tasks(
            self,
            author_id: Optional[int],
            status: Optional[TaskStatus],
            assignee_id: Optional[int],
            uow,
    ) -> List[Task]:
        return await uow.task.list(
            author_id=author_id,
            status=status,
            assignee_id=assignee_id,
        )

    async def update_task(self, task_id: int, data: TaskUpdateRequest, uow) -> Optional[Task]:
        task = await uow.task.get_by_id(task_id)
        if not task:
            return None

        update_data = data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        await uow.commit()

        return await uow.task.get_by_id(task_id)

    async def delete_task(self, task_id: int, uow) -> bool:
        task = await uow.task.get_by_id(task_id)
        if not task:
            return False

        await uow.task.delete(task)
        await uow.commit()
        return True
