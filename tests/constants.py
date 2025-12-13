from src.models.enums import TaskStatus

TEST_USER_ID = 1
TEST_BOARD_ID = 1

TASK_CREATE_DATA = {
    "title": "Тестовая задача",
    "description": "Описание",
    "status": TaskStatus.TODO,
    "author_id": TEST_USER_ID,
    "assignee_id": None,
    "board_id": TEST_BOARD_ID,
    "watchers": [],
}