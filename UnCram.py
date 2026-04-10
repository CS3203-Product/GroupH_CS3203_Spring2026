from datetime import datetime
from nicegui import ui

class TaskRecord:
    """Represents a single completed or in-progress task with timing metadata."""

    def __init__(self, task_id: str, title: str, category: str = "general"):
        self.task_id = task_id
        self.title = title
        self.category = category
        self.created_at = datetime.now()
        self.completed_at = None
        self.time_spent_minutes = 0.0
        self.is_completed = False
        self._timer_start = None

    def start_timer(self):
        if self._timer_start is not None:
            raise ValueError("Timer already running")
        self._timer_start = datetime.now()

    def stop_timer(self):
        if self._timer_start is None:
            raise ValueError("Timer not running")
        elapsed = (datetime.now() - self._timer_start).total_seconds() / 60.0
        self.time_spent_minutes += elapsed
        self._timer_start = None
        return elapsed

    def mark_complete(self):
        if self._timer_start is not None:
            self.stop_timer()
        self.is_completed = True
        self.completed_at = datetime.now()

    @property
    def elapsed_days(self):
        end = self.completed_at or datetime.now()
        return (end - self.created_at).total_seconds() / 86400.0


class TaskAnalyticsDashboard:
    """Tracks task completion, time spent, and productivity trends.

    Planned capabilities (not yet implemented):
        - Daily/weekly/monthly summary reports
        - Productivity trend analysis over time
        - Personalized insight generation
        - Category-level breakdowns
    """

    def __init__(self):
        self._records: dict[str, TaskRecord] = {}

    def add_task(self, task_id: str, title: str, category: str = "general") -> TaskRecord:
        if task_id in self._records:
            raise KeyError(f"Task '{task_id}' already exists")
        record = TaskRecord(task_id, title, category)
        self._records[task_id] = record
        return record

    def get_task(self, task_id: str) -> TaskRecord:
        if task_id not in self._records:
            raise KeyError(f"Task '{task_id}' not found")
        return self._records[task_id]

    def complete_task(self, task_id: str) -> TaskRecord:
        record = self.get_task(task_id)
        record.mark_complete()
        return record

    def log_time(self, task_id: str, minutes: float):
        if minutes < 0:
            raise ValueError("Minutes must be non-negative")
        record = self.get_task(task_id)
        record.time_spent_minutes += minutes

    @property
    def total_tasks(self) -> int:
        return len(self._records)

    @property
    def completed_tasks(self) -> int:
        return sum(1 for r in self._records.values() if r.is_completed)

    @property
    def completion_rate(self) -> float:
        if self.total_tasks == 0:
            return 0.0
        return self.completed_tasks / self.total_tasks

    @property
    def total_time_spent(self) -> float:
        return sum(r.time_spent_minutes for r in self._records.values())

class Task:               
    def __init__(self, name, due_day):
        self.name = name
        self.due_day = due_day
        self.importance = 0
    pass
