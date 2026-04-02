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

class TaskPrioritizationEngine:
    # This class is responsible for prioritizing tasks based on various factors
    pass

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

class FocusModeTimer:
    # This class is responsible for implementing a focus mode timer to help users stay focused on their tasks
    pass

import unittest


class DistractionBlocker:
    # This feature blocks websites that are distractions to users during scheduled task sessions (10:30AM - 20:00).  
    # When the website is blocked, check_access returns true.
    # When website is not blocked, check_access returns false. 
    # Raise ValueError is for invalid/empty URLs.

    def __init__(self):
        
        self.blocked_sites = []

    def set_blocked_sites(self, sites):
        
        self.blocked_sites = sites

    def check_access(self, url, current_time):
        
        if not url or not url.strip():
            
            raise ValueError("URL cannot be empty.")

        # Time format: hours and minutes
        hours, minutes = map(int, current_time.split(":"))
        
        total_minutes = hours * 60+ minutes

        # Task session (start and end time block): 10:30 (630 minutes) to 20:00 (1200 minutes)

        session_start = 10*60+ 30 

        session_end = 20 * 60          

        in_session= session_start <= total_minutes<session_end

        if in_session and url in self.blocked_sites:

            return True  # for when site is blocked

        return False  #for when site is unblocked , accessible


class TestDistractionBlocker(unittest.TestCase):

    def setUp(self):

        self.blocker = DistractionBlocker()

        self.blocked=  ["facebook.com"]

        self.blocker.set_blocked_sites(self.blocked)  

    def test_block_valid_site_during_task_session(self):

        # At 20:00, the session ends and access to other sites is opened

        result = self.blocker.check_access("facebook.com", current_time="20:00")
        
        self.assertFalse(result, "Access to sites open after 20:00")

    def test_boundary_start_time(self):

        # At 10:30, the session starts and access to other sites should be blocked

        result =self.blocker.check_access("facebook.com", current_time="10:30")
        
        self.assertTrue(result, "Blocker activates at 10:30 AM")

    def test_invalid_url_format(self):

        with self.assertRaises(ValueError):
            
            self.blocker.check_access("", current_time="10:30")


if __name__ == "__main__":
    
    unittest.main()

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    # This class is responsible for facilitating collaboration and communication among team members working on shared tasks
    pass

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass


TimeBlockingScheduler()
ui.run()