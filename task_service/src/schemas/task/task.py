from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

from task_service.src.models.enums import TaskStatus


class BoardResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class SprintResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=3)
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.TODO
    author_id: int
    assignee_id: Optional[int] = None
    watchers: List[int] = Field(default_factory=list)
    board_id: Optional[int] = None
    column: Optional[str] = None
    sprint_id: Optional[int] = None
    group: Optional[str] = None

    @field_validator("description")
    @classmethod
    def check_description(cls, v: Optional[str]) -> Optional[str]:
        if v and len(v) > 2000:
            raise ValueError("Description too long")
        if v is not None and not all(c.isprintable() or c.isspace() for c in v):
            raise ValueError("Description contains invalid characters")
        return v


class TaskUpdateRequest(TaskCreateRequest):
    title: Optional[str] = Field(None, min_length=3)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    author_id: Optional[int] = None
    assignee_id: Optional[int] = None
    watchers: Optional[List[int]] = None
    board_id: Optional[int] = None
    column: Optional[str] = None
    sprint_id: Optional[int] = None
    group: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus

    author_id: int
    assignee_id: Optional[int] = None
    watcher_ids: List[int] = Field(default_factory=list)

    board: BoardResponse
    column: Optional[str] = None
    sprint: Optional[SprintResponse] = None
    group: Optional[str] = None

    model_config = {"from_attributes": True}