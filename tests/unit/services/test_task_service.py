import pytest
from src.services.task_service import TaskService
from src.schemas.task.task import TaskCreateRequest, TaskUpdateRequest
from src.models.task import Task, Board
from src.models.user import User
from src.models.enums import TaskStatus
from tests.fixtures.testing_cases import fake_uow
from fastapi import HTTPException


@pytest.fixture
def service() -> TaskService:
    return TaskService()


@pytest.mark.asyncio
async def test_create_task_success(service: TaskService, fake_uow):
    board = Board(id=1, name="Main Board", owner_id=1)
    author = User(id=1, username="andrew", email="a@example.com", hashed_password="xxx")
    await fake_uow.board.add(board)
    await fake_uow.user.add(author)

    data = TaskCreateRequest(
        title="Новая задача",
        board_id=1,
        column="todo",
        group="backend",
        author_id=1,
    )

    task = await service.create_task(fake_uow, data, author)

    assert task.id == 1
    assert task.title == "Новая задача"
    assert task.board_id == 1
    assert task.author_id == 1
    assert task.column == "todo"
    assert fake_uow.committed is True


@pytest.mark.asyncio
async def test_create_task_board_not_found(service: TaskService, fake_uow):
    author = User(id=1, username="andrew", email="a@example.com", hashed_password="xxx")
    await fake_uow.user.add(author)

    data = TaskCreateRequest(title="Нет доски", board_id=999, author_id=1)

    with pytest.raises(HTTPException) as exc:
        await service.create_task(fake_uow, data, author)

    assert exc.value.status_code == 404
    assert "Доска не найдена" in exc.value.detail
    assert fake_uow.committed is False


@pytest.mark.asyncio
async def test_create_task_assignee_not_found(service: TaskService, fake_uow):
    board = Board(id=1, name="Board", owner_id=1)
    author = User(id=1, username="author", email="a@example.com", hashed_password="xxx")
    await fake_uow.board.add(board)
    await fake_uow.user.add(author)

    data = TaskCreateRequest(
        title="Нет исполнителя",
        board_id=1,
        assignee_id=999,
        author_id=1,
    )

    with pytest.raises(HTTPException) as exc:
        await service.create_task(fake_uow, data, author)

    assert exc.value.status_code == 404
    assert "Исполнитель не найден" in exc.value.detail
    assert fake_uow.committed is False


@pytest.mark.asyncio
async def test_update_task_not_found_and_updated(service: TaskService, fake_uow):
    task = Task(
        id=1,
        title="Старая",
        description="было",
        status=TaskStatus.TODO,
        board_id=1,
        author_id=1,
        column="todo",
    )
    await fake_uow.task.add(task)

    update_data = TaskUpdateRequest(
        title="Новая",
        description="стало",
        status=TaskStatus.DONE,
        column="done",
    )

    updated_task = await service.update_task(task_id=1, data=update_data, uow=fake_uow)

    assert updated_task is not None
    assert updated_task.title == "Новая"
    assert updated_task.description == "стало"
    assert updated_task.status == TaskStatus.DONE
    assert updated_task.column == "done"
    assert fake_uow.committed is True

    from_repo = await fake_uow.task.get_by_id(1)
    assert from_repo.title == "Новая"


@pytest.mark.asyncio
async def test_update_task_not_found_returns_none(service: TaskService, fake_uow):
    update_data = TaskUpdateRequest(title="Не найдёт")
    result = await service.update_task(task_id=999, data=update_data, uow=fake_uow)
    assert result is None
    assert fake_uow.committed is False


@pytest.mark.asyncio
async def test_delete_task_success(service: TaskService, fake_uow):
    task = Task(id=1, title="Удалить меня", board_id=1, author_id=1)
    await fake_uow.task.add(task)

    result = await service.delete_task(task_id=1, uow=fake_uow)

    assert result is True
    assert fake_uow.committed is True
    assert await fake_uow.task.get_by_id(1) is None


@pytest.mark.asyncio
async def test_delete_task_not_found_returns_false(service: TaskService, fake_uow):
    result = await service.delete_task(task_id=999, uow=fake_uow)
    assert result is False
    assert fake_uow.committed is False


@pytest.mark.asyncio
async def test_list_tasks_filters_correctly(service: TaskService, fake_uow):
    board = Board(id=1, name="Board", owner_id=1)
    user1 = User(id=1, username="u1", email="u1@x.com", hashed_password="x")
    user2 = User(id=2, username="u2", email="u2@x.com", hashed_password="x")
    await fake_uow.board.add(board)
    await fake_uow.user.add(user1)
    await fake_uow.user.add(user2)

    tasks = [
        Task(id=1, title="A", author_id=1, assignee_id=2, status=TaskStatus.TODO, board_id=1),
        Task(id=2, title="B", author_id=1, assignee_id=None, status=TaskStatus.DONE, board_id=1),
        Task(id=3, title="C", author_id=2, assignee_id=1, status=TaskStatus.TODO, board_id=1),
    ]
    for t in tasks:
        await fake_uow.task.add(t)

    all_tasks = await service.list_tasks(author_id=None, status=None, assignee_id=None, uow=fake_uow)
    assert len(all_tasks) == 3

    todo = await service.list_tasks(author_id=None, status=TaskStatus.TODO, assignee_id=None, uow=fake_uow)
    assert len(todo) == 2
    assert all(t.status == TaskStatus.TODO for t in todo)

    from_u1 = await service.list_tasks(author_id=1, status=None, assignee_id=None, uow=fake_uow)
    assert len(from_u1) == 2

    assigned_to_2 = await service.list_tasks(author_id=None, status=None, assignee_id=2, uow=fake_uow)
    assert len(assigned_to_2) == 1
    assert assigned_to_2[0].title == "A"
