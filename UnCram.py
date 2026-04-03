class Task:               
    def __init__(self, name, due_day):
        self.name = name
        self.due_day = due_day
        self.importance = 0
    pass
from nicegui import ui

class Task:               
    def __init__(self, name, due_day):
        self.name = name
        self.due_day = due_day
        self.importance = 0
    pass

class Uncram:
    # This is the main class for the Uncram tool
    pass

class TimeBlockingScheduler:
    # This class is responsible for scheduling tasks into time blocks
    def __init__(self):
        ui.label("Schedule - Basic Daily view").style(
            "font-family: 'Comic Sans MS'; font-size: 40px; color: black;"
        )
        

        # --- TABLE DATA ---
        self.columns = [ {'name': 'importance', 'label': 'Importance', 'field': 'importance'},
        {'name': 'sun', 'label': 'Sunday', 'field': 'sun'},
        {'name': 'mon', 'label': 'Monday', 'field': 'mon'},
        {'name': 'tues', 'label': 'Tuesday', 'field': 'tues'},
        {'name': 'wed', 'label': 'Wednesday', 'field': 'wed'},
        {'name': 'thur', 'label': 'Thursday', 'field': 'thur'},
        {'name': 'fri', 'label': 'Friday', 'field': 'fri'},
        {'name': 'sat', 'label': 'Saturday', 'field': 'sat'}, ]

        importance = [f"{h}" for h in range(0, 21)] 

        self.rows = [
            {'importance': t, 'sun': '', 'mon': '', 'tues': '', 'wed': '', 'thur': '', 'fri': '', 'sat': ''}
            for t in importance ]
                
        self.tasks = [                      # Example tasks; they should come from Task Prioritization Engine
            Task("Math Homework", "mon"),
            Task("Science Project", "wed"),
            Task("Grocery Shopping", "sat"),
            Task("Read Chapter 5", "tues"), ]

        self.populate_calendar()

        ui.table(columns=self.columns, rows=self.rows)

    def populate_calendar(self):
        for task in self.tasks:
            for row in self.rows:
                if row[task.due_day] == "":
                    row[task.due_day] = task.name
                    break

TimeBlockingScheduler()
ui.run()