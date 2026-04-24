from nicegui import ui
from nicegui.elements.dark_mode import DarkMode

from src.frontend.components.theme_toggle import create_theme_toggle_button


def create_header(left_drawer: ui.left_drawer, title: str, dark_mode: DarkMode) -> None:
    """App bar with UnCram branding."""
    with ui.header(elevated=True).classes(
        "items-center justify-between shadow-md border-b border-slate-200/80 dark:border-slate-700/80 "
        "bg-gradient-to-r from-emerald-50 via-white to-emerald-100 "
        "dark:from-emerald-800 dark:via-emerald-700 dark:to-slate-900"
    ):
        with ui.row().classes("items-center gap-2 pl-1"):
            ui.button(on_click=lambda: left_drawer.toggle(), icon="menu").props(
                "flat round"
            ).classes("text-slate-800 dark:text-white")
            ui.icon("eco", size="md").classes("text-emerald-700 dark:text-white")
            ui.label("UnCram").classes(
                "text-h6 font-bold tracking-tight text-slate-900 dark:text-white"
            )
            ui.label("·").classes("text-slate-400 dark:text-white/50")
            ui.label(title).classes(
                "text-subtitle1 text-emerald-800 dark:text-emerald-100"
            )
        with ui.row().classes("items-center gap-1 pr-2"):
            create_theme_toggle_button(dark_mode, for_header=True)
