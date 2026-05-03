"""Time-blocking schedule page."""

from nicegui import ui

from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.productivity.time_block_sched import TimeBlockingScheduler


@ui.page("/schedule")
def schedule_page() -> None:
    if not guard_authenticated():
        return
    with dashboard_frame(title="Schedule"):
        ui.label(
            "Plan tasks by importance and weekday. Entries update the grid instantly."
        ).classes("text-body2 text-slate-600 dark:text-slate-300 max-w-3xl mb-4")
        TimeBlockingScheduler()
