"""Task analytics and completion tracking."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TaskRecord:
    task_id: str
    title: str
    category: str
    is_completed: bool = False
    time_spent_minutes: float = 0.0


class TaskAnalyticsDashboard:
    def __init__(self) -> None:
        self._tasks: dict[str, TaskRecord] = {}

    def add_task(
        self, task_id: str, title: str, category: str = "general"
    ) -> TaskRecord:
        if task_id in self._tasks:
            raise KeyError(f"Task '{task_id}' already exists")
        record = TaskRecord(task_id=task_id, title=title, category=category)
        self._tasks[task_id] = record
        return record

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
