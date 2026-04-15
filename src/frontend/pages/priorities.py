"""Task prioritization page."""

from nicegui import ui

from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.productivity.task_priority import TaskPrioritizationEngine


@ui.page("/priorities")
def priorities_page() -> None:
    if not guard_authenticated():
        return
    with dashboard_frame(title="Priorities"):
        ui.label("Capture tasks and assign them to the next day buckets.").classes(
            "text-body2 text-slate-600 dark:text-slate-300 mb-4"
        )
        TaskPrioritizationEngine()
