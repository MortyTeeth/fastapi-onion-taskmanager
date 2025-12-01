import pytest
from pydantic import ValidationError
from fastapi import HTTPException

from src.models.enums import TaskStatus
from src.models.task import Task, Board
from src.models.user import User
from src.services.task_service import TaskService
from src.schemas.task.task import TaskCreateRequest, TaskUpdateRequest
from tests.constants import TASK_CREATE_DATA
from tests.fixtures.testing_cases import fake_uow

service = TaskService()



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload_mod, expected_status, check_field",
    [
        ({}, 201, lambda data: data.title == TASK_CREATE_DATA["title"]),
        ({"title": "Суперзадача!"}, 201, lambda data: data.title == "Суперзадача!"),
        ({"board_id": None}, 400, None),
        ({"title": ""}, 422, None),
        ({"status": "INVALID"}, 422, None),
    ],
    ids=["success_default", "success_custom_title", "missing_board_id", "empty_title", "invalid_status"]
)
async def test_create_task_variations(fake_uow, payload_mod, expected_status, check_field):
    author = User(id=1, username="author", email="a@x.com", hashed_password="x")
    await fake_uow.user.add(author)
    board_id = payload_mod.get("board_id", TASK_CREATE_DATA.get("board_id", 1))
    if board_id is not None:
        await fake_uow.board.add(Board(id=board_id, name="Board", owner_id=author.id))

    payload = TASK_CREATE_DATA.copy()
    payload.update(payload_mod)

    try:
        task_request = TaskCreateRequest(**payload)
        task = await service.create_task(fake_uow, task_request, author)
        assert expected_status == 201
        if check_field:
            assert check_field(task)
        assert task.status == TaskStatus.TODO
    except ValidationError:
        assert expected_status == 422
    except HTTPException as exc:
        assert exc.status_code == expected_status



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "status_filter, expected_count",
    [
        (TaskStatus.TODO, 1),
        (TaskStatus.IN_PROGRESS, 1),
        (TaskStatus.DONE, 1),
        (None, 3),
    ],
    ids=["filter_todo", "filter_in_progress", "filter_done", "no_filter"]
)
async def test_list_tasks_with_status_filter(fake_uow, status_filter, expected_count):
    author = User(id=1, username="author", email="a@x.com", hashed_password="x")
    await fake_uow.user.add(author)
    board = Board(id=1, name="Board", owner_id=1)
    await fake_uow.board.add(board)

    tasks_data = [
        {"title": "Задача TODO", "status": TaskStatus.TODO},
        {"title": "Задача IN_PROGRESS", "status": TaskStatus.IN_PROGRESS},
        {"title": "Задача DONE", "status": TaskStatus.DONE},
    ]
    for data in tasks_data:
        await service.create_task(
            fake_uow,
            TaskCreateRequest(
                title=data["title"],
                board_id=1,
                column="todo",
                group="backend",
                author_id=1,
                status=data["status"]
            ),
            author
        )

    all_tasks = await service.list_tasks(author_id=None, status=status_filter, assignee_id=None, uow=fake_uow)
    assert len(all_tasks) == expected_count



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "update_data, expected_values",
    [
        ({"title": "Новый тайтл"}, {"title": "Новый тайтл"}),
        ({"status": TaskStatus.DONE}, {"status": TaskStatus.DONE}),
        ({"description": "Очень важно!"}, {"description": "Очень важно!"}),
        ({"title": "Полное обновление", "status": TaskStatus.DONE, "description": "Готово!"},
         {"title": "Полное обновление", "status": TaskStatus.DONE, "description": "Готово!"}),
    ],
    ids=["update_title", "update_status", "update_description", "full_update"]
)
async def test_update_task(fake_uow, update_data, expected_values):
    author = User(id=1, username="author", email="a@x.com", hashed_password="x")
    await fake_uow.user.add(author)
    board = Board(id=1, name="Board", owner_id=1)
    await fake_uow.board.add(board)

    task = await service.create_task(fake_uow, TaskCreateRequest(**TASK_CREATE_DATA), author)
    update_request = TaskUpdateRequest(**{k: (v.value if isinstance(v, TaskStatus) else v) for k, v in update_data.items()})
    updated = await service.update_task(task_id=task.id, data=update_request, uow=fake_uow)

    for key, value in expected_values.items():
        assert getattr(updated, key) == value



@pytest.mark.asyncio
@pytest.mark.parametrize(
    "setup_task, task_id_to_delete, expected_status",
    [
        (True, "valid", 204),
    ],
    ids=["delete_existing"]
)
async def test_delete_task(fake_uow, setup_task, task_id_to_delete, expected_status):
    author = User(id=1, username="author", email="a@x.com", hashed_password="x")
    await fake_uow.user.add(author)
    board = Board(id=1, name="Board", owner_id=1)
    await fake_uow.board.add(board)

    if setup_task:
        task = await service.create_task(fake_uow, TaskCreateRequest(**TASK_CREATE_DATA), author)
        task_id_to_delete = task.id

    result = await service.delete_task(task_id=task_id_to_delete, uow=fake_uow)
    assert expected_status == 204
    all_tasks = await service.list_tasks(author_id=None, status=None, assignee_id=None, uow=fake_uow)
    assert task_id_to_delete not in [t.id for t in all_tasks]

