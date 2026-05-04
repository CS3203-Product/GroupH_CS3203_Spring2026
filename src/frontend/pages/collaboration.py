"""Collaboration hub UI using existing home-screen tasks."""

from nicegui import ui
from sqlmodel import select
from jose import jwt, JWTError

from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.frontend.state import get_auth
from src.productivity.collaboration_hub import CollaborationHub
from src.productivity.collaboration_models import CollaborationInvite
from src.db.session import get_db_context
from src.models.models import User, Item
from src.core.config import settings
from src.core.security import ALGORITHM


class CollaborationDesk:
    def __init__(self) -> None:
        self.hub = CollaborationHub()
        self.current_user_email = ""
        self.current_user_id = None
        self.task_options = {}

    def build(self) -> None:
        ui.label("Collaboration hub").classes(
            "text-h5 font-bold text-emerald-800 dark:text-emerald-200"
        )

        auth = get_auth()

        if not auth:
            ui.label("You must be logged in to use collaboration.").classes("text-red-500")
            return

        try:
            token = auth.get("access_token")

            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[ALGORITHM],
            )

            user_id = payload.get("sub")

            with get_db_context() as db:
                user = db.get(User, int(user_id))

                if not user:
                    ui.label("Could not find your user account in the database.").classes("text-red-500")
                    return

                self.current_user_id = user.id
                self.current_user_email = user.email.strip().lower()

        except JWTError:
            ui.label("Your login session is invalid. Please log in again.").classes("text-red-500")
            return

        except Exception:
            ui.label("Failed to load your account information.").classes("text-red-500")
            return

        if not self.current_user_email:
            ui.label("Could not find your email from your login token.").classes("text-red-500")
            return

        ui.label(f"Logged in as: {self.current_user_email}").classes("text-slate-500")

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("Send invite").classes("text-lg font-semibold")

            self.task_select = ui.select(
                options={},
                label="Select one of your tasks",
            ).classes("w-full")

            self.receiver_email_input = ui.input(
                "Receiver email"
            ).classes("w-full")

            with ui.row().classes("gap-2"):
                ui.button(
                    "Send invite",
                    on_click=self.send_invite_gui,
                ).props("color=primary")

                ui.button(
                    "Refresh task list",
                    on_click=self.refresh_my_tasks_dropdown,
                ).props("outline")

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("Pending invites").classes("text-lg font-semibold")

            ui.label(
                f"Showing invites for: {self.current_user_email}"
            ).classes("text-slate-500")

            ui.button(
                "Refresh invites",
                on_click=self.refresh_invites,
            ).props("outline")

            self.invite_list = ui.column()

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("My tasks").classes("text-lg font-semibold")
            self.task_list = ui.column()

        with ui.card().classes("w-full max-w-xl p-4"):
            ui.label("Status").classes("text-lg font-semibold")
            self.result_label = ui.label("Ready.")

        self.refresh_my_tasks_dropdown()
        self.refresh_tasks()
        self.refresh_invites()

    def refresh_my_tasks_dropdown(self) -> None:
        with get_db_context() as db:
            items = db.exec(
                select(Item).where(Item.owner_id == self.current_user_id)
            ).all()

        self.task_options = {
            item.title: item.id
            for item in items
        }

        self.task_select.options = list(self.task_options.keys())
        self.task_select.update()

        if not self.task_options:
            self.result_label.text = "You do not have any tasks to share yet."

    def refresh_tasks(self) -> None:
        self.task_list.clear()

        with get_db_context() as db:
            items = db.exec(
                select(Item).where(Item.owner_id == self.current_user_id)
            ).all()

            if not items:
                with self.task_list:
                    ui.label("No tasks on your home screen yet.").classes("text-slate-500")
                return

            with self.task_list:
                for item in items:
                    ui.label(
                        f"Task: {item.title} | Category: {item.category} | Completed: {item.is_completed}"
                    )

    def refresh_invites(self) -> None:
        self.invite_list.clear()

        with self.invite_list:
            with get_db_context() as db:
                invites = self.hub.view_invites(
                    db,
                    self.current_user_email,
                )

                if not invites:
                    ui.label(f"No pending invites for {self.current_user_email}.")
                    return

                for invite in invites:
                    item = db.get(Item, invite.task_id)
                    task_title = item.title if item else "Unknown task"

                    with ui.row().classes("items-center gap-2 flex-wrap"):
                        ui.label(
                            f"{invite.sender} invited you to '{task_title}'"
                        )

                        ui.button(
                            "Accept",
                            on_click=lambda invite_id=invite.id: self.accept_invite_gui(invite_id),
                        ).props("dense color=primary")

                        ui.button(
                            "Decline",
                            on_click=lambda invite_id=invite.id: self.decline_invite_gui(invite_id),
                        ).props("dense outline")

    def send_invite_gui(self) -> None:
        sender_email = self.current_user_email
        receiver_email = self.receiver_email_input.value.strip().lower()
        selected_task_title = self.task_select.value

        if not selected_task_title or not receiver_email:
            self.result_label.text = "Please select a task and enter a receiver email."
            return

        selected_item_id = self.task_options.get(selected_task_title)

        if not selected_item_id:
            self.result_label.text = "Selected task was not found. Refresh the task list and try again."
            return

        with get_db_context() as db:
            self.result_label.text = self.hub.send_invite(
                db,
                sender_email,
                receiver_email,
                selected_item_id,
            )

        self.receiver_email_input.value = ""
        self.refresh_invites()

    def accept_invite_gui(self, invite_id: int) -> None:
        with get_db_context() as db:
            self.result_label.text = self.hub.accept_invite(
                db,
                invite_id,
            )

        self.refresh_my_tasks_dropdown()
        self.refresh_tasks()
        self.refresh_invites()

    def decline_invite_gui(self, invite_id: int) -> None:
        with get_db_context() as db:
            self.result_label.text = self.hub.decline_invite(
                db,
                invite_id,
            )

        self.refresh_invites()


@ui.page("/collaboration")
def collaboration_page() -> None:
    if not guard_authenticated():
        return

    with dashboard_frame(title="Collaboration"):
        CollaborationDesk().build()