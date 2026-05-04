"""Task analytics and completion tracking.

This module intentionally stays UI/database independent. The NiceGUI dashboard
page is responsible for syncing these in-memory records with SQLModel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class TaskRecord:
    id: int
    task_id: str
    title: str
    category: str
    user_id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: Optional[datetime] = None
    difficulty: int = 5
    user_importance: int = 5
    estimated_duration: float = 1.0
    predicted_duration: Optional[float] = None
    predicted_priority: Optional[float] = None
    is_completed: bool = False
    started: bool = False
    time_spent_minutes: float = 0.0


class TaskAnalyticsDashboard:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskRecord] = {}
        self._next_manual_task_id = -1

    def _generate_next_task_id(self) -> int:
        value = self._next_manual_task_id
        self._next_manual_task_id -= 1
        return value

    def add_task(
        self,
        task_id: str,
        title: str,
        category: str = "general",
        user_id: Optional[int] = None,
        difficulty: int = 5,
        user_importance: int = 5,
        estimated_duration: float = 1.0,
        deadline: Optional[datetime] = None,
    ) -> TaskRecord:
        if task_id in self._tasks:
            raise KeyError(f"Task '{task_id}' already exists")
        record = TaskRecord(
            id=self._generate_next_task_id(),
            task_id=task_id,
            title=title,
            category=category,
            user_id=user_id,
            created_at=datetime.utcnow(),
            deadline=deadline,
            difficulty=difficulty,
            user_importance=user_importance,
            estimated_duration=estimated_duration,
        )
        self._tasks[task_id] = record
        return record

    def upsert_task(
        self,
        *,
        task_id: str,
        db_id: int,
        title: str,
        category: str = "general",
        user_id: Optional[int] = None,
        difficulty: int = 5,
        user_importance: int = 5,
        estimated_duration: float = 1.0,
        deadline: Optional[datetime] = None,
        is_completed: bool = False,
        predicted_duration: Optional[float] = None,
        predicted_priority: Optional[float] = None,
        time_spent_minutes: float = 0.0,
    ) -> TaskRecord:
        if task_id in self._tasks:
            record = self._tasks[task_id]
        else:
            record = self.add_task(
                task_id=task_id,
                title=title,
                category=category,
                user_id=user_id,
                difficulty=difficulty,
                user_importance=user_importance,
                estimated_duration=estimated_duration,
                deadline=deadline,
            )

        record.id = db_id
        record.title = title
        record.category = category or "general"
        record.user_id = user_id
        record.difficulty = difficulty
        record.user_importance = user_importance
        record.estimated_duration = estimated_duration
        record.deadline = deadline
        record.is_completed = is_completed
        record.predicted_duration = predicted_duration
        record.predicted_priority = predicted_priority
        record.time_spent_minutes = time_spent_minutes
        return record

    def remove_missing(self, active_task_ids: set[str]) -> None:
        for task_id in list(self._tasks):
            if task_id not in active_task_ids:
                del self._tasks[task_id]

    def get_task(self, task_id: str) -> TaskRecord:
        if task_id not in self._tasks:
            raise KeyError(f"Task '{task_id}' not found")
        return self._tasks[task_id]

    def complete_task(self, task_id: str) -> TaskRecord:
        t = self.get_task(task_id)
        t.is_completed = True
        return t

    def log_time(self, task_id: str, minutes: float) -> None:
        if minutes < 0:
            raise ValueError("minutes must be non-negative")
        t = self.get_task(task_id)
        t.started = True
        t.time_spent_minutes += minutes

    @property
    def total_tasks(self) -> int:
        return len(self._tasks)

    @property
    def completed_tasks(self) -> int:
        return sum(1 for t in self._tasks.values() if t.is_completed)

    @property
    def completion_rate(self) -> float:
        if not self._tasks:
            return 0.0
        return self.completed_tasks / len(self._tasks)

    @property
    def total_time_spent(self) -> float:
        return sum(t.time_spent_minutes for t in self._tasks.values())
