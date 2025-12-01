from typing import Optional, TYPE_CHECKING

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from .base import Base
from .enums import TaskStatus

if TYPE_CHECKING:
    from .user import User

task_watchers = Table(
    "task_watchers",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner: Mapped["User"] = relationship("User", back_populates="owned_boards")

    sprints: Mapped[list["Sprint"]] = relationship("Sprint", back_populates="board", cascade="all, delete-orphan")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="board")


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(nullable=False)

    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)
    board: Mapped["Board"] = relationship("Board", back_populates="sprints")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False
    )

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    author: Mapped["User"] = relationship("User", back_populates="authored_tasks", foreign_keys=[author_id])

    assignee_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assignee: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_tasks",
                                                      foreign_keys=[assignee_id])

    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)
    board: Mapped["Board"] = relationship("Board", back_populates="tasks")

    sprint_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sprints.id"), nullable=True)
    sprint: Mapped[Optional["Sprint"]] = relationship("Sprint")

    column: Mapped[Optional[str]] = mapped_column(nullable=True)
    group: Mapped[Optional[str]] = mapped_column(nullable=True)

    watchers: Mapped[list["User"]] = relationship(
        "User",
        secondary=task_watchers,
        back_populates="watched_tasks",
    )
