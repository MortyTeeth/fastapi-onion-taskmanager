from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.task import Task, task_watchers


class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, task: Task) -> None:
        self.session.add(task)
        await self.session.flush([task])

    async def get_by_id(self, task_id: int) -> Optional[Task]:
        result = await self.session.execute(
            select(Task)
            .options(
                selectinload(Task.board),
                selectinload(Task.sprint),
            )
            .where(Task.id == task_id)
        )
        return result.scalars().one_or_none()

    async def list(
        self,
        author_id: Optional[int] = None,
        status: Optional[str] = None,
        assignee_id: Optional[int] = None,
    ) -> List[Task]:
        query = (
            select(Task)
            .options(
                selectinload(Task.board),
                selectinload(Task.sprint),
            )
        )

        if author_id is not None:
            query = query.where(Task.author_id == author_id)
        if status is not None:
            query = query.where(Task.status == status)
        if assignee_id is not None:
            query = query.where(Task.assignee_id == assignee_id)

        result = await self.session.execute(query)
        return result.scalars().unique().all()

    async def delete(self, task: Task) -> None:
        await self.session.delete(task)

    async def count_by_assignee(self, user_id: int) -> int:
        stmt = select(func.count(Task.id)).where(Task.assignee_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar() or 0

    async def count_watcher_tasks(self, user_id: int) -> int:
        stmt = (
            select(func.count())
            .select_from(task_watchers)
            .where(task_watchers.c.user_id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0