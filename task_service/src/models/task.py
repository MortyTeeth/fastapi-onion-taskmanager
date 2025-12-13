from typing import Optional, List
from sqlalchemy import Table, Column, ForeignKey, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.sqltypes import Enum as SQLEnum

from .base import Base
from .enums import TaskStatus



task_watchers = Table(
    "task_watchers",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", Integer, primary_key=True),
)


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    owner_id: Mapped[int] = mapped_column(Integer, nullable=False)

    sprints: Mapped[List["Sprint"]] = relationship(
        "Sprint", back_populates="board", cascade="all, delete-orphan"
    )
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="board")


class Sprint(Base):
    __tablename__ = "sprints"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)
    board: Mapped["Board"] = relationship("Board", back_populates="sprints")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="sprint")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus), default=TaskStatus.TODO, nullable=False
    )

    author_id: Mapped[int] = mapped_column(Integer, nullable=False)
    assignee_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)
    board: Mapped["Board"] = relationship("Board", back_populates="tasks")

    sprint_id: Mapped[Optional[int]] = mapped_column(ForeignKey("sprints.id"), nullable=True)
    sprint: Mapped[Optional["Sprint"]] = relationship("Sprint", back_populates="tasks")

    column: Mapped[Optional[str]] = mapped_column(nullable=True)
    group: Mapped[Optional[str]] = mapped_column(nullable=True)