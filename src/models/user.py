from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .task import Task, Board


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)

    authored_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="author",
        foreign_keys="Task.author_id",
    )


    assigned_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )


    watched_tasks: Mapped[list["Task"]] = relationship(
        "Task",
        secondary="task_watchers",
        back_populates="watchers",
    )


    owned_boards: Mapped[list["Board"]] = relationship(
        "Board",
        back_populates="owner",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )