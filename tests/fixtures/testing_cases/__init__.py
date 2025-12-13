from __future__ import annotations

from typing import AsyncIterator, Any, List, Optional

import pytest
from pydantic_settings import BaseSettings
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from src.models.base import Base
from src.models.enums import TaskStatus
from src.utils.unit_of_work import UnitOfWork


class TestSettings(BaseSettings):
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


test_settings = TestSettings()


class FakeRepository:
    def __init__(self) -> None:
        self._items: dict[int, Any] = {}
        self._next_id: int = 1

    async def add(self, item: Any) -> None:
        if getattr(item, "id", None) is None:
            item.id = self._next_id
            self._next_id += 1
        self._items[item.id] = item

    async def get_by_id(self, item_id: int) -> Optional[Any]:
        return self._items.get(item_id)

    async def delete(self, item: Any) -> None:
        if getattr(item, "id", None) in self._items:
            del self._items[item.id]

    async def list(self, **filters) -> list[Any]:
        result = list(self._items.values())
        for key, value in filters.items():
            if value is not None:
                result = [item for item in result if getattr(item, key, None) == value]
        return result

    def clear(self) -> None:
        self._items.clear()
        self._next_id = 1


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        from src.models.task import Task, Board, Sprint
        from src.models.user import User

        self.task = FakeRepository()
        self.board = FakeRepository()
        self.user = FakeRepository()
        self.sprint = FakeRepository()

        self.committed = False
        self.rolled_back = False

        class FakeSession:
            def __init__(self, uow):
                self.uow = uow

            async def add(self, instance):
                repo_map = {Task: self.uow.task, Board: self.uow.board, User: self.uow.user, Sprint: self.uow.sprint}
                repo = repo_map.get(type(instance))
                if repo:
                    await repo.add(instance)

            async def delete(self, instance):
                repo_map = {Task: self.uow.task, Board: self.uow.board, User: self.uow.user, Sprint: self.uow.sprint}
                repo = repo_map.get(type(instance))
                if repo:
                    await repo.delete(instance)

            async def flush(self, objects=None):
                if objects:
                    for obj in objects:
                        if hasattr(obj, "id") and obj.id is None:
                            repo_map = {Task: self.uow.task, Board: self.uow.board, User: self.uow.user, Sprint: self.uow.sprint}
                            repo = repo_map.get(type(obj))
                            if repo:
                                await repo.add(obj)

            async def get(self, model, item_id):
                repo_map = {Task: self.uow.task, Board: self.uow.board, User: self.uow.user, Sprint: self.uow.sprint}
                repo = repo_map.get(model)
                if repo:
                    return await repo.get_by_id(item_id)
                return None

            async def execute(self, stmt):

                from src.models.task import Task


                filters = {}
                if hasattr(stmt, "_where_criteria") and stmt._where_criteria:
                    for cond in stmt._where_criteria:
                        if hasattr(cond, "left") and hasattr(cond, "right"):
                            col_name = getattr(cond.left, "name", None)
                            val = getattr(cond.right, "value", None)
                            if col_name == "status" and isinstance(val, str):
                                from src.models.enums import TaskStatus
                                val = TaskStatus[val]
                            if col_name:
                                filters[col_name] = val

                items = await self.uow.task.list(**filters) if filters else list(self.uow.task._items.values())

                class FakeResult:
                    def __init__(self, items): self._items = items
                    def scalars(self): return self
                    def unique(self): return self
                    def all(self): return self._items
                    def one_or_none(self): return self._items[0] if self._items else None
                    def first(self): return self._items[0] if self._items else None

                return FakeResult(items)

        self.session = FakeSession(self)

    async def __aenter__(self): return self
    async def __aexit__(self, *args): pass
    async def commit(self): self.committed = True
    async def rollback(self): self.rolled_back = True


@pytest.fixture
def fake_uow() -> AsyncIterator[FakeUnitOfWork]:
    uow = FakeUnitOfWork()
    yield uow
    uow.task.clear()
    uow.board.clear()
    uow.user.clear()
    uow.sprint.clear()
    uow.committed = uow.rolled_back = False

