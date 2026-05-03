"""NiceGUI weekly grid for time blocking."""

from nicegui import ui

from src.productivity.scheduling_task import SchedulingTask as Task


class TimeBlockingScheduler:
    def __init__(self) -> None:
        ui.label("Weekly schedule").classes(
            "text-h5 font-semibold text-emerald-800 dark:text-emerald-200"
        )
        self.error_label = ui.label("").classes("text-red-600")

        self.columns = [
            {"name": "importance", "label": "Importance", "field": "importance"},
            {"name": "sun", "label": "Sunday", "field": "sun"},
            {"name": "mon", "label": "Monday", "field": "mon"},
            {"name": "tues", "label": "Tuesday", "field": "tues"},
            {"name": "wed", "label": "Wednesday", "field": "wed"},
            {"name": "thur", "label": "Thursday", "field": "thur"},
            {"name": "fri", "label": "Friday", "field": "fri"},
            {"name": "sat", "label": "Saturday", "field": "sat"},
        ]

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

        with ui.row().classes("flex-wrap gap-2 items-end"):
            self.task_name_input = ui.input("Task name").classes("min-w-[12rem]")
            self.day_input = ui.select(
                ["sun", "mon", "tues", "wed", "thur", "fri", "sat"],
                label="Due day",
            )
            self.importance_input = ui.number(
                "Importance (0–20)", min=0, max=20, value=0
            )
            ui.button("Add task", on_click=self.add_task).props("color=primary")

        self.table = ui.table(columns=self.columns, rows=self.rows).classes("w-full")

    def add_task(self) -> None:
        name = self.task_name_input.value
        day = self.day_input.value
        importance = self.importance_input.value

        if not name or not day:
            self.error_label.text = "Please enter a task name and select a day."
            return

        self.error_label.text = ""

        new_task = Task(name, day)
        new_task.importance = int(importance or 0)
        self.tasks.append(new_task)

        self.populate_calendar()
        self.table.rows = self.rows
        self.table.update()

        self.task_name_input.value = ""
        self.day_input.value = None
        self.importance_input.value = 0

    def populate_calendar(self) -> None:
        for row in self.rows:
            for d in ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]:
                row[d] = ""

        for task in self.tasks:
            target_row = self.rows[task.importance]
            if target_row[task.due_day]:
                target_row[task.due_day] += f", {task.name}"
            else:
                target_row[task.due_day] = task.name
