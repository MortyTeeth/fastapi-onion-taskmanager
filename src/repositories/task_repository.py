from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.task import Task


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
                joinedload(Task.author),
                joinedload(Task.assignee),
                joinedload(Task.watchers),
                joinedload(Task.board),
                joinedload(Task.sprint),
            )
            .where(Task.id == task_id)
        )
        return result.scalars().unique().one_or_none()

    async def list(
        self,
        author_id: Optional[int] = None,
        status: Optional[str] = None,
        assignee_id: Optional[int] = None,
    ) -> List[Task]:
        query = (
            select(Task)
            .options(
                joinedload(Task.author),
                joinedload(Task.assignee),
                joinedload(Task.watchers),
                joinedload(Task.board),
                joinedload(Task.sprint),
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