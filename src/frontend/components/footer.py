from nicegui import ui


def create_footer() -> None:
    """Footer strip."""
    with ui.footer(elevated=True).classes(
        "bg-slate-900 text-slate-300 items-center justify-center py-3 border-t border-slate-700"
    ):
        with ui.row().classes("items-center gap-2 text-caption"):
            ui.icon("bolt", size="xs", color="emerald-5")
            ui.label("© 2026 CS3203 Productivity App · Built for deep work.")
