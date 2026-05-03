"""Task analytics and completion tracking."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional

from src.ai.auto_retrain import trigger_background_retrain
from src.ai.services import (
    behavior_tracker,
    task_logger
)
from src.ai.user_stats_service import rebuild_user_stats


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

    def get_task(self, task_id: str) -> TaskRecord:
        if task_id not in self._tasks:
            raise KeyError(f"Task '{task_id}' not found")
        return self._tasks[task_id]

    def complete_task(self, task_id: str) -> TaskRecord:
        t = self.get_task(task_id)
        if t.user_id is not None:
            if not t.started:
                task_logger.log_task_started(t)
                t.started = True
            task_logger.log_task_completed(t)
            rebuild_user_stats(task_logger.session, t.user_id)
            behavior_tracker.build_behavior_profile(t.user_id)
            trigger_background_retrain()

        t.is_completed = True
        return t

    def log_time(self, task_id: str, minutes: float) -> None:
        if minutes < 0:
            raise ValueError("minutes must be non-negative")
        t = self.get_task(task_id)
        if t.user_id is not None and not t.started:
            task_logger.log_task_started(t)
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
