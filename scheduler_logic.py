# scheduler_logic.py

class Task:               
    def __init__(self, name, due_day, importance=0):
        self.name = name
        self.due_day = due_day
        self.importance = importance

class SchedulerLogic:
    def __init__(self):
        importance = list(range(0, 21))
        self.rows = [
            {'importance': str(t), 'sun': '', 'mon': '', 'tues': '', 'wed': '', 'thur': '', 'fri': '', 'sat': ''}
            for t in importance
        ]
        self.tasks = []

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.populate_calendar()

    def populate_calendar(self):
        # clear rows
        for row in self.rows:
            for day in ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]:
                row[day] = ""

        # fill rows
        for task in self.tasks:
            target_row = self.rows[task.importance]
            if target_row[task.due_day]:
                target_row[task.due_day] += f", {task.name}"
            else:
# scheduler_logic.py

class Task:               
    def __init__(self, name, due_day, importance=0):
        self.name = name
        self.due_day = due_day
        self.importance = importance

class SchedulerLogic:
    def __init__(self):
        importance = list(range(0, 21))
        self.rows = [
            {'importance': str(t), 'sun': '', 'mon': '', 'tues': '', 'wed': '', 'thur': '', 'fri': '', 'sat': ''}
            for t in importance
        ]
        self.tasks = []

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.populate_calendar()

    def populate_calendar(self):
        # clear rows
        for row in self.rows:
            for day in ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]:
                row[day] = ""

        # fill rows
        for task in self.tasks:
            target_row = self.rows[task.importance]
            if target_row[task.due_day]:
                target_row[task.due_day] += f", {task.name}"
            else:
                target_row[task.due_day] = task.name