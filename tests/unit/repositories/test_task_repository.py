from __future__ import annotations

import pytest

from src.repositories.task_repository import TaskRepository
from src.models.task import Task
from src.models.enums import TaskStatus
from tests.fixtures.testing_cases import fake_uow


@pytest.fixture
def task_repo(fake_uow) -> TaskRepository:
    return TaskRepository(fake_uow.session)


@pytest.mark.asyncio
async def test_add(task_repo: TaskRepository, fake_uow):
    task = Task(
        title="Новая задача",
        author_id=999,
        board_id=999,
        status=TaskStatus.TODO,
    )

    await task_repo.add(task)
    await fake_uow.commit()

    saved = await fake_uow.task.get_by_id(task.id)
    assert saved is not None
    assert saved.title == "Новая задача"
    assert saved.author_id == 999
    assert saved.id is not None


@pytest.mark.asyncio
async def test_get_by_id_found(task_repo: TaskRepository, fake_uow):
    original = Task(title="Найдётся", author_id=1, board_id=1)
    await fake_uow.task.add(original)
    await fake_uow.commit()

    found = await task_repo.get_by_id(original.id)
    assert found == original
    assert found.title == "Найдётся"


@pytest.mark.asyncio
async def test_get_by_id_not_found(task_repo: TaskRepository):
    result = await task_repo.get_by_id(999)
    assert result is None


@pytest.mark.asyncio
async def test_list_no_filters(task_repo: TaskRepository, fake_uow):
    tasks = [
        Task(title="A", author_id=1, board_id=1, status=TaskStatus.TODO),
        Task(title="B", author_id=1, board_id=1, status=TaskStatus.DONE),
        Task(title="C", author_id=2, board_id=1, status=TaskStatus.IN_PROGRESS),
    ]
    for t in tasks:
        await fake_uow.task.add(t)
    await fake_uow.commit()

    result = await task_repo.list()
    assert len(result) == 3
    assert {t.title for t in result} == {"A", "B", "C"}


@pytest.mark.asyncio
async def test_delete(task_repo: TaskRepository, fake_uow):
    task = Task(title="Удалить", author_id=1, board_id=1)
    await fake_uow.task.add(task)
    await fake_uow.commit()

    await task_repo.delete(task)
    await fake_uow.commit()

    deleted = await fake_uow.task.get_by_id(task.id)
    assert deleted is None