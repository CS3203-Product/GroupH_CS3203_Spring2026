"""Collaboration hub UI (tasks + invites)."""

from nicegui import ui

from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.productivity.collaboration_hub import CollaborationHub
from src.productivity.collaboration_models import CollaborationTask, CollaborationInvite
from sqlmodel import select
from src.db.session import get_db_context
from src.models.models import Task


class CollaborationDesk:
    def __init__(self) -> None:
        self.hub = CollaborationHub()
        self.tasks: list[CollaborationTask] = []

    def find_task(self, task_name: str) -> CollaborationTask | None:
        for task in self.tasks:
            if task.name == task_name:
                return task
        return None

    def build(self) -> None:
        ui.label("Collaboration hub").classes(
            "text-h5 font-bold text-emerald-800 dark:text-emerald-200"
        )

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("Create task").classes("text-lg font-semibold")
            self.owner_input = ui.input("Task owner")
            self.task_input = ui.input("Task name")
            ui.button("Create task", on_click=self.create_task).props("color=primary")

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("Send invite").classes("text-lg font-semibold")
            self.sender_input = ui.input("Sender")
            self.receiver_input = ui.input("Receiver")
            self.invite_task_input = ui.input("Task name")
            ui.button("Send invite", on_click=self.send_invite_gui).props(
                "color=primary"
            )

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("Pending invites").classes("text-lg font-semibold")
            self.invite_user_input = ui.input("Username")
            ui.button("Refresh invites", on_click=self.refresh_invites).props("outline")
            self.invite_list = ui.column()

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("All tasks").classes("text-lg font-semibold")
            self.task_list = ui.column()

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("Status").classes("text-lg font-semibold")
            self.result_label = ui.label("Ready.")

        self.refresh_tasks()
        self.refresh_invites()

    def refresh_tasks(self) -> None:
        self.task_list.clear()

        with get_db_context() as db:
            tasks = db.exec(select(Task)).all()

            if not tasks:
                with self.task_list:
                    ui.label("No tasks created yet.").classes("text-slate-500")
                return

            with self.task_list:
                for task in tasks:

                    accepted_invites = db.exec(
                        select(CollaborationInvite).where(
                            CollaborationInvite.task_id == task.id,
                            CollaborationInvite.status == "accepted",
                        )
                    ).all()

                    shared_users = [invite.receiver for invite in accepted_invites]

                    shared = ", ".join(shared_users) if shared_users else "No one"

                    ui.label(
                        f"Task: {task.name} | Owner: {task.owner} | Shared with: {shared}"
                    )

    def refresh_invites(self) -> None:
        self.invite_list.clear()
        selected_user = self.invite_user_input.value.strip()

        with self.invite_list:
            if not selected_user:
                ui.label("Enter a username to view invites.").classes("text-slate-500")
                return

            with get_db_context() as db:
                invites = self.hub.view_invites(db, selected_user)

                if not invites:
                    ui.label(f"No pending invites for {selected_user}.")
                    return

                for invite in invites:
                    task = db.get(Task, invite.task_id)
                    task_name = task.name if task else "Unknown task"

                    with ui.row().classes("items-center gap-2 flex-wrap"):
                        ui.label(
                            f"{invite.sender} → {invite.receiver} · '{task_name}'"
                        )

                        ui.button(
                            "Accept",
                            on_click=lambda invite_id=invite.id: self.accept_invite_gui(invite_id),
                        ).props("dense color=primary")

                        ui.button(
                            "Decline",
                            on_click=lambda invite_id=invite.id: self.decline_invite_gui(invite_id),
                        ).props("dense outline")

    def create_task(self) -> None:
        owner = self.owner_input.value.strip()
        task_name = self.task_input.value.strip()

        if not owner or not task_name:
            self.result_label.text = "Please enter both owner and task name."
            return

        with get_db_context() as db:
            existing_task = db.exec(
                select(Task).where(Task.name == task_name)
            ).first()

            if existing_task:
                self.result_label.text = "A task with that name already exists."
                return

            task_row = Task(
                name=task_name,
                owner=owner,
            )

            db.add(task_row)
            db.commit()
            db.refresh(task_row)

        self.result_label.text = f"Task '{task_name}' created for {owner}."
        self.refresh_tasks()

    def send_invite_gui(self) -> None:
        sender = self.sender_input.value.strip()
        receiver = self.receiver_input.value.strip()
        task_name = self.invite_task_input.value.strip()

        if not sender or not receiver or not task_name:
            self.result_label.text = "Please fill in sender, receiver, and task name."
            return

        with get_db_context() as db:
            task_row = db.exec(
                select(Task).where(Task.name == task_name)
            ).first()

            if not task_row:
                self.result_label.text = "Task not found."
                return

            task = CollaborationTask(
                name=task_row.name,
                owner=task_row.owner
            )

            self.result_label.text = self.hub.send_invite(db, sender, receiver, task)

        self.refresh_invites()

    def accept_invite_gui(self, invite_id: int) -> None:
        with get_db_context() as db:
            self.result_label.text = self.hub.accept_invite(db, invite_id)

        self.refresh_tasks()
        self.refresh_invites()


    def decline_invite_gui(self, invite_id: int) -> None:
        with get_db_context() as db:
            self.result_label.text = self.hub.decline_invite(db, invite_id)

        self.refresh_invites()


@ui.page("/collaboration")
def collaboration_page() -> None:
    if not guard_authenticated():
        return
    with dashboard_frame(title="Collaboration"):
        CollaborationDesk().build()
