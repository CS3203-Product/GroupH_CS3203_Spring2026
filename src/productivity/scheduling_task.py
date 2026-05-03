"""Task model shared by time blocking and prioritization UIs."""


class SchedulingTask:
    def __init__(self, name: str, due_day: str, importance: int = 0):
        self.name = name
        self.due_day = due_day
        self.importance = importance
