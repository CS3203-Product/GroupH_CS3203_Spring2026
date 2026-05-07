"""Ambient focus audio page."""

from nicegui import ui

from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.productivity.ambient_focus_aid import AmbientFocusAid


@ui.page("/ambient")
def ambient_page() -> None:
    if not guard_authenticated():
        return
    with dashboard_frame(title="Ambient focus"):
        ui.label("Background audio to stay in flow.").classes(
            "text-body2 text-slate-600 dark:text-slate-300 mb-4"
        )
        with ui.card().classes("p-6 max-w-lg"):
            AmbientFocusAid()
