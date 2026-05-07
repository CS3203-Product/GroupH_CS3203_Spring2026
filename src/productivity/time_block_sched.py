"""NiceGUI weekly grid for time blocking."""

from nicegui import ui
from src.productivity.scheduling_task import SchedulingTask as Task
from src.productivity.scheduler_logic import SchedulerLogic

class TimeBlockingScheduler:
    def __init__(self):

        ui.label("Weekly schedule").classes(
            "text-h5 font-semibold text-emerald-800 dark:text-emerald-200"
        )
        self.error_label = ui.label("").classes("text-red-600")

        with ui.row().classes("items-end gap-4"):
            self.task_select = ui.select(
                options=[],
                label="Select Task"
            ).classes("w-64")

            self.day_select = ui.select(
                options=[
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                    "Saturday",
                ],
                label="Select New Due Date",
            ).classes("w-64")

            ui.button(
                "Update Due Date",
                on_click=self.apply_due_date_from_dropdown
            ).classes("bg-emerald-600 text-white")

        self.columns = [
            {"name": "no_due_day", "label": "No Due Date", "field": "no_due_day"},
            {"name": "importance", "label": "Importance", "field": "importance"},
        ]

        for key in ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]:
            self.columns.append({"name": key, "label": key, "field": key})

        importance = list(range(0, 21))

        self.rows = [
            {
                "importance": str(t),
                "Sunday": "",
                "Monday": "",
                "Tuesday": "",
                "Wednesday": "",
                "Thursday": "",
                "Friday": "",
                "Saturday": "",
                "no_due_day": "",
            }
            for t in importance
        ]

        self.table = ui.table(columns=self.columns, rows=self.rows).classes("w-full")
        
        for row in self.rows:
            for key in [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "no_due_day",
            ]: row[key] = ""

        logic = SchedulerLogic()
        logic.populate_calendar(self.rows)
        self.table.rows = self.rows
        self.table.update()

        self.task_select.options = {
            task.id: task.title.strip()
            for task in logic.tasks
        }
        self.task_select.update()

    def apply_due_date_from_dropdown(self, _):
        task_id = self.task_select.value
        new_day = self.day_select.value

        if not task_id or not new_day:
            ui.notify("Please select both a task and a day", color="red")
            return

        task_id = int(task_id)

        # Update DB
        logic = SchedulerLogic()
        logic.update_due_date(task_id, new_day)

        # Reload tasks from DB (fresh instance)
        logic = SchedulerLogic()

        # Reset table rows
        for row in self.rows:
            for key in [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "no_due_day",
            ]: row[key] = ""


        # Repopulate calendar with fresh tasks
        logic.populate_calendar(self.rows)
        self.table.rows = self.rows
        self.table.update()

        # Refresh dropdown
        self.task_select.options = {
            task.id: task.title.strip()
            for task in logic.tasks
        }
        self.task_select.update()

        task_title = next((t.title for t in logic.tasks if t.id == task_id), None)
        ui.notify(f"{task_title} is now due on {new_day}")
