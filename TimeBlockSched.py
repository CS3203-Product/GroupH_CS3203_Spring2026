from nicegui import ui
from Task import Task

class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    def __init__(self):
        ui.label("Schedule - Basic Daily view").style(
            "font-family: 'Comic Sans MS'; font-size: 40px; color: black;"
        )
        self.error_label = ui.label("").style("color: red")

        # --- TABLE DATA ---
        self.columns = [ {'name': 'importance', 'label': 'Importance', 'field': 'importance'},
        {'name': 'sun', 'label': 'Sunday', 'field': 'sun'},
        {'name': 'mon', 'label': 'Monday', 'field': 'mon'},
        {'name': 'tues', 'label': 'Tuesday', 'field': 'tues'},
        {'name': 'wed', 'label': 'Wednesday', 'field': 'wed'},
        {'name': 'thur', 'label': 'Thursday', 'field': 'thur'},
        {'name': 'fri', 'label': 'Friday', 'field': 'fri'},
        {'name': 'sat', 'label': 'Saturday', 'field': 'sat'}, ]

        importance = list(range(0, 21))

        self.rows = [
            {'importance': str(t), 'sun': '', 'mon': '', 'tues': '', 'wed': '', 'thur': '', 'fri': '', 'sat': ''}
            for t in importance]
        self.tasks = []

        with ui.row():
            self.task_name_input = ui.input("Task name")
            self.day_input = ui.select(
                ["sun", "mon", "tues", "wed", "thur", "fri", "sat"],
                label="Due day" )
            self.importance_input = ui.number("Importance (0–20)", min=0, max=20, value=0)
            ui.button("Add Task", on_click=self.add_task)
            
        self.table = ui.table(columns=self.columns, rows=self.rows)

    def add_task(self):
        name = self.task_name_input.value
        day = self.day_input.value
        importance = self.importance_input.value
            
        if not name or not day:
            self.error_label.text = ("Please enter a task name and select a day.")
            return
        else:
            self.error_label.text = ""
            
        new_task = Task(name, day)
        new_task.importance = int(importance)
        self.tasks.append(new_task)

        self.populate_calendar()
        self.table.update() 

        self.task_name_input.value = ""
        self.day_input.value = None
        self.importance_input.value = 0

    def populate_calendar(self):
        for row in self.rows:
            for day in ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]:
                row[day] = ""
            
        for task in self.tasks:
                target_row = self.rows[task.importance]
                if target_row[task.due_day]:
                    target_row[task.due_day] += f", {task.name}"
                else:
                    target_row[task.due_day] = task.name
        self.table.rows = self.rows