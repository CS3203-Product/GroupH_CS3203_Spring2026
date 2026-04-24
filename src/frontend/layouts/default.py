from contextlib import contextmanager

from nicegui import app, ui

from src.frontend import state
from src.frontend.components.footer import create_footer
from src.frontend.components.header import create_header
from src.frontend.state import clear_auth

_NAV = [
    ("dashboard", "/dashboard", "Dashboard"),
    ("assignment", "/items", "Task board"),
    ("calendar_month", "/schedule", "Schedule"),
    ("timer", "/focus", "Focus timer"),
    ("graphic_eq", "/ambient", "Ambient"),
    ("sort", "/priorities", "Priorities"),
    ("groups", "/collaboration", "Collaboration"),
]


def guard_authenticated() -> bool:
    """Return False and navigate to login when there is no session."""
    if not state.get_auth():
        ui.navigate.to("/login")
        return False
    return True


@contextmanager
def dashboard_frame(title: str):
    """Authenticated shell: drawer, header, main column, footer."""
    async def handle_logout():
        clear_auth()
        app.storage.user.clear()
        ui.navigate.to("/login")

    left_drawer = ui.left_drawer(value=True, elevated=True).classes(
        "bg-slate-900 text-slate-100 border-r border-slate-700"
    )

    create_header(left_drawer, title)

    with left_drawer:
        with ui.column().classes("w-full h-full flex flex-col justify-between no-wrap p-2"):
            with ui.column().classes("gap-1"):
                ui.label("Workspace").classes(
                    "text-caption text-emerald-400 uppercase tracking-widest px-3 pt-2"
                )
                for icon_name, path, label in _NAV:
                    with (
                        ui.item(on_click=lambda p=path: ui.navigate.to(p))
                        .props("clickable")
                        .classes("w-full rounded-lg")
                    ):
                        with ui.item_section().props("avatar"):
                            ui.icon(icon_name, color="emerald-4")
                        with ui.item_section():
                            ui.label(label).classes("text-slate-100 text-weight-medium")

                if app.storage.user.get("is_superuser"):
                    ui.separator().classes("my-2 bg-slate-700")
                    with (
                        ui.item(on_click=lambda: ui.navigate.to("/users/create"))
                        .props("clickable")
                        .classes("w-full rounded-lg")
                    ):
                        with ui.item_section().props("avatar"):
                            ui.icon("person_add", color="emerald-4")
                        with ui.item_section():
                            ui.label("Create user").classes(
                                "text-slate-100 text-weight-medium"
                            )

            with ui.column().classes("w-full"):
                ui.separator().classes("my-2 bg-slate-700")
                with (
                    ui.item(on_click=handle_logout)
                    .props("clickable")
                    .classes("w-full rounded-lg")
                ):
                    with ui.item_section().props("avatar"):
                        ui.icon("logout", color="grey-5")
                    with ui.item_section():
                        ui.label("Log out").classes("text-slate-300")

    with ui.column().classes(
        "w-full min-h-[70vh] p-4 md:p-8 items-stretch bg-slate-50 dark:bg-slate-950"
    ):
        yield

    create_footer()
