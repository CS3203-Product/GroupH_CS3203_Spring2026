"""Task model shared by time blocking and prioritization UIs."""

from typing import Optional


class SchedulingTask:
    def __init__(
        self,
        name: str,
        due_day: str,
        importance: int = 0,
        *,
        entry_id: Optional[int] = None,
        category: str = "general",
        sort_order: int = 0,
    ):
        self.name = name
        self.due_day = due_day
        self.importance = importance
        self.entry_id = entry_id
        self.category = category
        self.sort_order = sort_order
