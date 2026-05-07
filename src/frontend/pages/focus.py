"""Focus timer (Pomodoro-style)."""

from nicegui import ui

from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.productivity.focus_mode_timer import FocusModeTimer


@ui.page("/focus")
def focus_page() -> None:
    if not guard_authenticated():
        return
    with dashboard_frame(title="Focus timer"):
        ui.label("Structured work sessions with short breaks.").classes(
            "text-body2 text-slate-600 dark:text-slate-300 mb-4"
        )
        with ui.row().classes("w-full justify-center"):
            FocusModeTimer(work_min=25, break_min=5, long_break_min=20)
