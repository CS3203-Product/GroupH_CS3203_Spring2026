from nicegui import ui
from sqlmodel import select
from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.db.session import get_db_context
from src.models.models import Item, User
from src.productivity.collaboration_hub import CollaborationHub
from src.productivity.collaboration_models import CollaborationInvite
from src.frontend.components.auth_utils import get_current_user_from_state


class CollaborationPage:
    def __init__(self):
        self.hub = CollaborationHub()

        self.task_title_input = None
        self.receiver_email_input = None
        self.status_label = None
        self.invites_container = None
        self.shared_tasks_container = None

    def render(self):
        ui.label("Collaboration Hub").classes("text-3xl font-bold mb-4")

        with ui.card().classes("w-full max-w-2xl p-4"):
            ui.label("Send Task Invite").classes("text-xl font-semibold")

            self.task_title_input = ui.input("Task title").classes("w-full")
            self.receiver_email_input = ui.input("Receiver email").classes("w-full")

            ui.button("Send Invite", on_click=self.send_invite).classes("mt-2")

            self.status_label = ui.label("").classes("mt-2 text-sm")

        with ui.card().classes("w-full max-w-2xl p-4 mt-4"):
            ui.label("Pending Invites").classes("text-xl font-semibold")

            self.invites_container = ui.column().classes("w-full")
            ui.button("Refresh Invites", on_click=self.refresh_invites).classes("mt-2")

        with ui.card().classes("w-full max-w-2xl p-4 mt-4"):
            ui.label("Accessible Tasks").classes("text-xl font-semibold")

            self.shared_tasks_container = ui.column().classes("w-full")
            ui.button("Refresh Tasks", on_click=self.refresh_accessible_tasks).classes("mt-2")

        self.refresh_invites()
        self.refresh_accessible_tasks()

    def send_invite(self):
        task_title = self.task_title_input.value.strip()
        receiver_email = self.receiver_email_input.value.strip()

        if not task_title:
            self.status_label.text = "Please enter a task title."
            return

        if not receiver_email:
            self.status_label.text = "Please enter a receiver email."
            return

        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            if not current_user:
                self.status_label.text = "You must be logged in to send invites."
                return

            receiver = db.exec(
                select(User).where(User.email == receiver_email)
            ).first()

            if not receiver:
                self.status_label.text = "Receiver user not found."
                return

            message = self.hub.send_invite_by_title(
                db=db,
                sender=current_user,
                receiver=receiver,
                task_title=task_title,
            )

            self.status_label.text = message

        self.refresh_invites()
        self.refresh_accessible_tasks()

    def refresh_invites(self):
        if not self.invites_container:
            return

        self.invites_container.clear()

        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            if not current_user:
                with self.invites_container:
                    ui.label("Log in to view invites.")
                return

            invites = self.hub.view_invites(db, current_user)

            with self.invites_container:
                if not invites:
                    ui.label("No pending invites.")
                    return

                for invite in invites:
                    task = db.get(Item, invite.task_id)
                    task_title = task.title if task else "Unknown task"

                    with ui.row().classes("items-center gap-2"):
                        ui.label(
                            f"Task: {task_title} | From: {invite.sender}"
                        )

                        ui.button(
                            "Accept",
                            on_click=lambda invite_id=invite.id: self.accept_invite(invite_id),
                        ).classes("bg-green-600 text-white")

                        ui.button(
                            "Decline",
                            on_click=lambda invite_id=invite.id: self.decline_invite(invite_id),
                        ).classes("bg-red-600 text-white")

    def accept_invite(self, invite_id: int):
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            if not current_user:
                self.status_label.text = "You must be logged in."
                return

            message = self.hub.accept_invite(
                db=db,
                invite_id=invite_id,
                user=current_user,
            )

            self.status_label.text = message

        self.refresh_invites()
        self.refresh_accessible_tasks()

    def decline_invite(self, invite_id: int):
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            if not current_user:
                self.status_label.text = "You must be logged in."
                return

            message = self.hub.decline_invite(
                db=db,
                invite_id=invite_id,
                user=current_user,
            )

            self.status_label.text = message

        self.refresh_invites()
        self.refresh_accessible_tasks()

    def refresh_accessible_tasks(self):
        if not self.shared_tasks_container:
            return

        self.shared_tasks_container.clear()

        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            if not current_user:
                with self.shared_tasks_container:
                    ui.label("Log in to view shared tasks.")
                return

            tasks = self.hub.get_accessible_tasks(db, current_user)

            with self.shared_tasks_container:
                if not tasks:
                    ui.label("No owned or shared tasks yet.")
                    return

                for task in tasks:
                    owner_label = (
                        "Owned by you"
                        if task.owner_id == current_user.id
                        else f"Shared task from owner ID {task.owner_id}"
                    )

                    completed_label = "Completed" if task.completed else "Open"

                    ui.label(
                        f"{task.title} | {owner_label} | {completed_label}"
                    )


@ui.page("/collaboration")
def collaboration_page():
    if not guard_authenticated():
        return

    with dashboard_frame(title="Collaboration"):
        page = CollaborationPage()
        page.render()