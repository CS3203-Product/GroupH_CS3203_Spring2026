from nicegui import ui


class Task:
    def __init__(self, name, owner):
        self.name = name
        self.owner = owner
        self.shared_with = []


class CollaborationHub:
    def __init__(self):
        self.invites = []

    def send_invite(self, sender, receiver, task):
        if task.owner != sender:
            return "Only the owner can invite others."

        if receiver in task.shared_with:
            return f"{receiver} already has access to this task."

        for invite in self.invites:
            if (
                invite["sender"] == sender
                and invite["receiver"] == receiver
                and invite["task"] == task
                and invite["status"] == "pending"
            ):
                return f"Invite already pending for {receiver}."

        invite = {
            "sender": sender,
            "receiver": receiver,
            "task": task,
            "status": "pending",
        }

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
            if (
                invite["receiver"] == receiver
                and invite["task"] == task
                and invite["status"] == "pending"
            ):
                invite["status"] = "accepted"
                if receiver not in task.shared_with:
                    task.shared_with.append(receiver)
                return f"{receiver} accepted invite for task '{task.name}'."
        return "No pending invite found."

    def decline_invite(self, receiver, task):
        for invite in self.invites:
            if (
                invite["receiver"] == receiver
                and invite["task"] == task
                and invite["status"] == "pending"
            ):
                invite["status"] = "declined"
                return f"{receiver} declined invite for task '{task.name}'."
        return "No pending invite found."

    def can_view_task(self, user, task):
        return user == task.owner or user in task.shared_with


hub = CollaborationHub()
tasks = []


def find_task(task_name):
    for task in tasks:
        if task.name == task_name:
            return task
    return None


def refresh_tasks():
    task_list.clear()
    if not tasks:
        with task_list:
            ui.label("No tasks created yet.")
        return

    with task_list:
        for task in tasks:
            shared_users = ", ".join(task.shared_with) if task.shared_with else "No one"
            ui.label(f"Task: {task.name} | Owner: {task.owner} | Shared With: {shared_users}")


def refresh_invites():
    invite_list.clear()
    selected_user = invite_user_input.value.strip()

    with invite_list:
        if not selected_user:
            ui.label("Enter a username above to view invites.")
            return

        invites = hub.view_invites(selected_user)
        if not invites:
            ui.label(f"No pending invites for {selected_user}.")
            return

        for invite in invites:
            task = invite["task"]
            with ui.row().classes("items-center gap-2"):
                ui.label(f"{invite['sender']} invited {invite['receiver']} to '{task.name}'")

                ui.button(
                    "Accept",
                    on_click=lambda t=task, u=selected_user: accept_invite_gui(u, t)
                )

                ui.button(
                    "Decline",
                    on_click=lambda t=task, u=selected_user: decline_invite_gui(u, t)
                )


def create_task():
    owner = owner_input.value.strip()
    task_name = task_input.value.strip()

    if not owner or not task_name:
        result_label.set_text("Please enter both owner and task name.")
        return

    if find_task(task_name):
        result_label.set_text("A task with that name already exists.")
        return

    new_task = Task(task_name, owner)
    tasks.append(new_task)
    result_label.set_text(f"Task '{task_name}' created for {owner}.")
    refresh_tasks()


def send_invite_gui():
    sender = sender_input.value.strip()
    receiver = receiver_input.value.strip()
    task_name = invite_task_input.value.strip()

    if not sender or not receiver or not task_name:
        result_label.set_text("Please fill in sender, receiver, and task name.")
        return

    task = find_task(task_name)
    if not task:
        result_label.set_text("Task not found.")
        return

    message = hub.send_invite(sender, receiver, task)
    result_label.set_text(message)
    refresh_invites()


def accept_invite_gui(user, task):
    message = hub.accept_invite(user, task)
    result_label.set_text(message)
    refresh_tasks()
    refresh_invites()


def decline_invite_gui(user, task):
    message = hub.decline_invite(user, task)
    result_label.set_text(message)
    refresh_invites()


ui.label("Collaboration Hub").classes("text-2xl font-bold")

with ui.card().classes("w-full max-w-xl p-4"):
    ui.label("Create Task").classes("text-lg font-semibold")
    owner_input = ui.input("Task Owner")
    task_input = ui.input("Task Name")
    ui.button("Create Task", on_click=create_task)

with ui.card().classes("w-full max-w-xl p-4"):
    ui.label("Send Invite").classes("text-lg font-semibold")
    sender_input = ui.input("Sender")
    receiver_input = ui.input("Receiver")
    invite_task_input = ui.input("Task Name")
    ui.button("Send Invite", on_click=send_invite_gui)

with ui.card().classes("w-full max-w-xl p-4"):
    ui.label("View Pending Invites").classes("text-lg font-semibold")
    invite_user_input = ui.input("Username")
    ui.button("Refresh Invites", on_click=refresh_invites)
    invite_list = ui.column()

with ui.card().classes("w-full max-w-xl p-4"):
    ui.label("All Tasks").classes("text-lg font-semibold")
    task_list = ui.column()

with ui.card().classes("w-full max-w-xl p-4"):
    ui.label("Status").classes("text-lg font-semibold")
    result_label = ui.label("Ready.")

refresh_tasks()
refresh_invites()

ui.run()