from nicegui import ui


def create_footer() -> None:
    """Footer strip."""
    with ui.footer(elevated=True).classes(
        "items-center justify-center py-3 border-t "
        "bg-slate-100 text-slate-600 border-slate-200 "
        "dark:bg-slate-900 dark:text-slate-300 dark:border-slate-700"
    ):
        with ui.row().classes("items-center gap-2 text-caption"):
            ui.icon("bolt", size="xs").classes("text-emerald-600 dark:text-emerald-400")
            ui.label("© 2026 CS3203 Productivity App · Built for deep work.")
