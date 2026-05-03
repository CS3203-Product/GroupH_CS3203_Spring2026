"""Grid scheduler logic (importance weekday)."""

from src.productivity.scheduling_task import SchedulingTask as Task


class SchedulerLogic:
    def __init__(self):
        importance = list(range(0, 21))
        self.rows = [
            {
                "importance": str(t),
                "sun": "",
                "mon": "",
                "tues": "",
                "wed": "",
                "thur": "",
                "fri": "",
                "sat": "",
            }
            for t in importance
        ]
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)
        self.populate_calendar()

    def populate_calendar(self) -> None:
        for row in self.rows:
            for day in ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]:
                row[day] = ""

        for task in self.tasks:
            target_row = self.rows[task.importance]
            if target_row[task.due_day]:
                target_row[task.due_day] += f", {task.name}"
            else:
                target_row[task.due_day] = task.name
