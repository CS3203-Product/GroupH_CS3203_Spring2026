from fastapi import HTTPException
from nicegui import app, ui

from src.core import security
from src.db.session import get_db_context
from src.frontend import state
from src.frontend.components import notifications
from src.frontend.components.form_utils import enable_button_on_user_inputs
from src.repositories.user import user_repo


@ui.page("/login")
def login_page():
    """Sign in to UnCram."""
    if state.get_auth():
        ui.navigate.to("/dashboard")
        return

    with ui.column().classes(
        "absolute-center w-full max-w-md items-stretch gap-6 px-4"
    ):
        with ui.row().classes("items-center justify-center gap-3"):
            ui.icon("eco", color="primary", size="lg")
            with ui.column().classes("gap-0"):
                ui.label("UnCram").classes("text-h4 font-bold text-slate-800 dark:text-slate-100")
                ui.label("Your productive workspace").classes(
                    "text-body2 text-slate-600 dark:text-slate-400"
                )

        with ui.card().classes(
            "w-full p-8 shadow-xl border border-emerald-100 dark:border-emerald-900/40 bg-white/95 dark:bg-slate-900/95 backdrop-blur"
        ):
            ui.label("Sign in").classes("text-h6 text-slate-700 dark:text-slate-200 mb-4")

            email = (
                ui.input("Email")
                .props("autocomplete=username outlined")
                .classes("w-full")
            )
            password = (
                ui.input("Password")
                .props("type=password autocomplete=current-password outlined")
                .classes("w-full")
            )
            login_button = (
                ui.button("Continue", icon="login")
                .props("color=primary unelevated")
                .classes("w-full")
            )

            login_button.on("click", lambda: perform_login(email, password))
            email.on("keydown.enter", lambda: perform_login(email, password))
            password.on("keydown.enter", lambda: perform_login(email, password))

            email.on(
                "update:model-value",
                lambda: enable_button_on_user_inputs([email, password], login_button),
            )
            password.on(
                "update:model-value",
                lambda: enable_button_on_user_inputs([email, password], login_button),
            )

            enable_button_on_user_inputs([email, password], login_button)


async def perform_login(email_input: ui.input, password_input: ui.input):
    if not email_input.validate() or not password_input.validate():
        return
    try:
        with get_db_context() as db:
            user = user_repo.authenticate(
                db=db, email=email_input.value, password=password_input.value
            )
            auth_data = {
                "access_token": security.create_access_token(user.id),
                "token_type": "bearer",
            }
            state.set_auth(auth_data)
            app.storage.user["is_superuser"] = user.is_superuser
            ui.navigate.to("/dashboard")
    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")
