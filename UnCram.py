from nicegui import ui

class Task:               
    def __init__(self, name, due_day):
        self.name = name
        self.due_day = due_day
        self.importance = 0
        self.shared_with = []
        self.owner = None

    #temporary for testing
    def __str__(self):
        return f"Task: {self.name}, Due: {self.due_day}, Importance: {self.importance}"
    pass

#changed this for testing can be removed later
class Uncram:
    def __init__(self):
        self.users = []
        self.tasks = []
        self.collaboration_hub = CollaborationHub()

    def add_user(self, username):
        if username not in self.users:
            self.users.append(username)
            return f"User '{username}' added."
        return f"User '{username}' already exists."

    def create_task(self, owner, name, due_day):
        if owner not in self.users:
            return "Owner must be a registered user."

        task = Task(name, due_day)
        task.owner = owner
        self.tasks.append(task)
        return task

    def view_tasks_for_user(self, user):
        visible_tasks = []
        for task in self.tasks:
            if self.collaboration_hub.can_view_task(user, task):
                visible_tasks.append(task)
        return visible_tasks

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

class DistractionBlocker:
    # This class is responsible for blocking distracting websites and apps during focus mode
    pass

class TaskAnalyticsDashboard:
    # This class is responsible for providing analytics and insights on task completion and productivity
    pass

class CollaborationHub:
    def __init__(self):
        self.invites = []

    def send_invite(self, sender, receiver, task):
        if task.owner != sender:
            return "Only the owner can invite others."

        if receiver in task.shared_with:
            return f"{receiver} already has access to this task."

        for invite in self.invites:
            if(invite["sender"] == sender and invite["receiver"] == receiver and invite["task"] == task and invite["status"] == "pending"):
                return f"Invite already pending for {receiver}."

        invite = {"sender" : sender, "receiver": receiver, "task": task, "status" : "pending"}

        self.invites.append(invite)
        return f"Invite sent from {sender} to {receiver} for task '{task.name}'."

    def view_invites(self, user):
        user_invites = []
        for invite in self.invites:
            if invite["receiver"] == user and invite["status"] == "pending":
                user_invites.append(invite)
        return user_invites
    
    def accept_invite(self, receiver, task):
        for invite in self.invites:
            if(invite["receiver"] == receiver and invite["task"] == task and invite["status"] == "pending"):
                invite["status"] == "accepted"
                task.shared_with.append(receiver)
                return f"{receiver} accepted invite for task '{task.name}'."
        return "no pending invite found."

    def can_view_task(self, user, task):
        return user == task.owner or user in task.shared_with
    
    def decline_invite(self, receiver, task):
        for invite in self.invites:
            if(invite["receiver"] == receiver and invite["task"] == task, invite["status"] == "pending"):
                invite["status"] = "declined"
                return f"{receiver} declined invite for task '{task.name}'."
        return "No pending invite found."

    

class AmbientFocusAid:
    # This class is responsible for providing ambient sounds and music to help users stay focused while working on tasks
    pass

TimeBlockingScheduler()
ui.run()