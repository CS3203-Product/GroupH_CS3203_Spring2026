from fastapi import HTTPException
from nicegui import app, ui

from src.core import security
from src.db.session import get_db_context
from src.frontend import state
from src.frontend.components import notifications
from src.frontend.components.form_utils import enable_button_on_user_inputs
from src.models import UserCreate
from src.repositories.user import user_repo


@ui.page("/signup")
def signup_page():
    """Public registration page for new users."""
    if state.get_auth():
        ui.navigate.to("/items")
        return

    with ui.column().classes(
        "absolute-center w-full max-w-md items-stretch gap-6 px-4"
    ):
        with ui.row().classes("items-center justify-center gap-3"):
            ui.icon("eco", color="primary", size="lg")
            with ui.column().classes("gap-0"):
                ui.label("UnCram").classes(
                    "text-h4 font-bold text-slate-800 dark:text-slate-100"
                )
                ui.label("Your productive workspace").classes(
                    "text-body2 text-slate-600 dark:text-slate-400"
                )

        with ui.card().classes(
            "w-full p-8 shadow-xl border border-emerald-100 "
            "dark:border-emerald-900/40 bg-white/95 dark:bg-slate-900/95 backdrop-blur"
        ):
            ui.label("Create your account").classes(
                "text-h6 text-slate-700 dark:text-slate-200 mb-4"
            )

            full_name = (
                ui.input("Full name")
                .props("outlined")
                .classes("w-full")
            )
            email = (
                ui.input("Email")
                .props("autocomplete=username outlined")
                .classes("w-full")
            )
            password = (
                ui.input("Password")
                .props("type=password autocomplete=new-password outlined")
                .classes("w-full")
            )
            confirm_pw = (
                ui.input("Confirm password")
                .props("type=password autocomplete=new-password outlined")
                .classes("w-full")
            )

            signup_button = (
                ui.button("Create account", icon="person_add")
                .props("color=primary unelevated")
                .classes("w-full")
            )

            required_fields = [email, password, confirm_pw]

            signup_button.on(
                "click",
                lambda: perform_signup(full_name, email, password, confirm_pw),
            )
            for field in [full_name, *required_fields]:
                field.on(
                    "keydown.enter",
                    lambda: perform_signup(full_name, email, password, confirm_pw),
                )
                field.on(
                    "update:model-value",
                    lambda: enable_button_on_user_inputs(required_fields, signup_button),
                )

            enable_button_on_user_inputs(required_fields, signup_button)

        with ui.row().classes("justify-center"):
            ui.label("Already have an account?").classes(
                "text-slate-600 dark:text-slate-400"
            )
            ui.link("Sign in", "/login").classes(
                "text-emerald-600 dark:text-emerald-400 font-medium"
            )


async def perform_signup(
    name_input: ui.input,
    email_input: ui.input,
    password_input: ui.input,
    confirm_input: ui.input,
):
    if not email_input.value or not password_input.value or not confirm_input.value:
        notifications.show_error("Please fill in all required fields.")
        return

    if password_input.value != confirm_input.value:
        notifications.show_error("Passwords do not match.")
        return

    if len(password_input.value) < 8:
        notifications.show_error("Password must be at least 8 characters.")
        return

    try:
        with get_db_context() as db:
            user_in = UserCreate(
                email=email_input.value,
                password=password_input.value,
                full_name=name_input.value or None,
                is_superuser=False,
            )
            user = user_repo.register(db=db, obj_in=user_in)

            auth_data = {
                "access_token": security.create_access_token(user.id),
                "token_type": "bearer",
            }
            state.set_auth(auth_data)
            app.storage.user["is_superuser"] = user.is_superuser
            notifications.show_success("Account created — welcome to UnCram!")
            ui.navigate.to("/items")
    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")
