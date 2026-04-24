"""Dashboard — overview of tasks, analytics, and productivity stats."""

from __future__ import annotations

from fastapi import HTTPException
from nicegui import ui

from src.db.session import get_db_context
from src.frontend.components import notifications
from src.frontend.components.auth_utils import get_current_user_from_state
from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.productivity.task_analytics_dashboard import TaskAnalyticsDashboard
from src.repositories.item import item_repo


def _stat_card(icon: str, value: str, label: str, color: str) -> None:
    """Render a single metric card."""
    with ui.card().classes("p-5 flex-1 min-w-[180px]"):
        with ui.row().classes("items-center gap-3 no-wrap"):
            ui.icon(icon, size="lg").classes(f"text-{color}")
            with ui.column().classes("gap-0"):
                ui.label(value).classes("text-2xl font-bold dark:text-white")
                ui.label(label).classes(
                    "text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400"
                )


def _build_completion_chart(completed: int, pending: int) -> None:
    """Donut chart showing completed vs pending tasks."""
    ui.echart(
        {
            "tooltip": {"trigger": "item"},
            "legend": {"bottom": "0%", "textStyle": {"color": "#94a3b8"}},
            "series": [
                {
                    "type": "pie",
                    "radius": ["50%", "75%"],
                    "avoidLabelOverlap": True,
                    "label": {"show": False},
                    "data": [
                        {
                            "value": completed,
                            "name": "Completed",
                            "itemStyle": {"color": "#059669"},
                        },
                        {
                            "value": pending,
                            "name": "Pending",
                            "itemStyle": {"color": "#475569"},
                        },
                    ],
                }
            ],
        }
    ).classes("w-full h-56")


def _build_category_chart(analytics: TaskAnalyticsDashboard) -> None:
    """Bar chart breaking down tasks by category."""
    cats: dict[str, dict[str, int]] = {}
    for t in analytics._tasks.values():
        entry = cats.setdefault(t.category, {"done": 0, "open": 0})
        if t.is_completed:
            entry["done"] += 1
        else:
            entry["open"] += 1

    categories = list(cats.keys()) or ["(none)"]
    done_vals = [cats.get(c, {}).get("done", 0) for c in categories]
    open_vals = [cats.get(c, {}).get("open", 0) for c in categories]

    ui.echart(
        {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {"textStyle": {"color": "#94a3b8"}},
            "grid": {"left": "3%", "right": "4%", "bottom": "10%", "containLabel": True},
            "xAxis": {
                "type": "category",
                "data": categories,
                "axisLabel": {"color": "#94a3b8"},
            },
            "yAxis": {"type": "value", "axisLabel": {"color": "#94a3b8"}},
            "series": [
                {
                    "name": "Completed",
                    "type": "bar",
                    "stack": "total",
                    "data": done_vals,
                    "itemStyle": {"color": "#059669"},
                },
                {
                    "name": "Open",
                    "type": "bar",
                    "stack": "total",
                    "data": open_vals,
                    "itemStyle": {"color": "#475569"},
                },
            ],
        }
    ).classes("w-full h-56")


def _build_time_chart(analytics: TaskAnalyticsDashboard) -> None:
    """Horizontal bar chart of time spent per task."""
    tasks_with_time = [
        t for t in analytics._tasks.values() if t.time_spent_minutes > 0
    ]
    tasks_with_time.sort(key=lambda t: t.time_spent_minutes, reverse=True)
    tasks_with_time = tasks_with_time[:10]

    labels = [t.title[:24] for t in tasks_with_time] or ["(none)"]
    values = [round(t.time_spent_minutes, 1) for t in tasks_with_time] or [0]

    ui.echart(
        {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "grid": {"left": "25%", "right": "8%", "bottom": "10%", "containLabel": False},
            "xAxis": {
                "type": "value",
                "name": "Minutes",
                "axisLabel": {"color": "#94a3b8"},
                "nameTextStyle": {"color": "#94a3b8"},
            },
            "yAxis": {
                "type": "category",
                "data": labels,
                "axisLabel": {"color": "#94a3b8", "width": 100, "overflow": "truncate"},
            },
            "series": [
                {
                    "type": "bar",
                    "data": values,
                    "itemStyle": {"color": "#34d399"},
                }
            ],
        }
    ).classes("w-full h-56")


class DashboardView:
    """Manages the dashboard UI and its backing analytics engine."""

    def __init__(self) -> None:
        self.analytics = TaskAnalyticsDashboard()

    def _sync_from_db(self) -> tuple[int, str]:
        """Seed analytics from the user's persisted items. Returns (item_count, first_name)."""
        try:
            with get_db_context() as db:
                current_user = get_current_user_from_state(db)
                items = item_repo.get_for_user(db=db, current_user=current_user)

            first_name = (
                current_user.full_name.split()[0]
                if current_user.full_name
                else current_user.email.split("@")[0]
            )

            for item in items:
                task_id = f"item-{item.id}"
                if task_id not in self.analytics._tasks:
                    self.analytics.add_task(task_id, item.title, category="tasks")
            return len(items), first_name
        except HTTPException as e:
            notifications.show_error(e.detail)
            return 0, ""
        except Exception as e:
            notifications.show_error(f"Could not load items: {e}")
            return 0, ""

    def build(self) -> None:
        item_count, first_name = self._sync_from_db()

        total = self.analytics.total_tasks
        completed = self.analytics.completed_tasks
        pending = total - completed
        rate = self.analytics.completion_rate
        time_spent = self.analytics.total_time_spent

        with ui.row().classes(
            "w-full flex-wrap gap-4"
        ):
            _stat_card("assignment", str(total), "Total tasks", "emerald-500")
            _stat_card("check_circle", str(completed), "Completed", "green-500")
            _stat_card("pending", str(pending), "In progress", "amber-500")
            _stat_card("schedule", f"{time_spent:.0f}m", "Time logged", "sky-500")

        with ui.row().classes("w-full gap-4 flex-wrap items-start mt-2"):
            with ui.card().classes("flex-1 min-w-[320px] p-5"):
                ui.label("Completion overview").classes(
                    "text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2"
                )
                if total > 0:
                    _build_completion_chart(completed, pending)
                else:
                    ui.label("No tasks yet — add some below to see analytics.").classes(
                        "text-slate-500 dark:text-slate-400 py-8 text-center w-full"
                    )

            with ui.card().classes("flex-1 min-w-[320px] p-5"):
                ui.label("Tasks by category").classes(
                    "text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2"
                )
                if total > 0:
                    _build_category_chart(self.analytics)
                else:
                    ui.label("Categories appear once tasks are tracked.").classes(
                        "text-slate-500 dark:text-slate-400 py-8 text-center w-full"
                    )

        with ui.card().classes("w-full p-5 mt-2"):
            ui.label("Time spent (top 10)").classes(
                "text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2"
            )
            if time_spent > 0:
                _build_time_chart(self.analytics)
            else:
                ui.label("Log time against tasks to populate this chart.").classes(
                    "text-slate-500 dark:text-slate-400 py-4 text-center w-full"
                )

        self._build_tracker_panel()

    def _build_tracker_panel(self) -> None:
        """Quick-add panel for tracking tasks, completion, and time."""
        ui.label("Quick tracker").classes(
            "text-h6 font-bold text-emerald-700 dark:text-emerald-300 mt-6 mb-2"
        )

        task_table_container = ui.column().classes("w-full")

        with ui.card().classes("w-full p-5"):
            with ui.row().classes("w-full gap-3 flex-wrap items-end"):
                title_in = ui.input("Task title").classes("flex-1 min-w-[160px]")
                cat_in = ui.select(
                    ["general", "work", "study", "health", "personal"],
                    value="general",
                    label="Category",
                ).classes("min-w-[140px]")
                ui.button(
                    "Add task",
                    icon="add",
                    on_click=lambda: self._add_task(title_in, cat_in, task_table_container),
                ).props("color=primary")

            ui.separator().classes("my-3")

            with ui.row().classes("w-full gap-3 flex-wrap items-end"):
                log_select = ui.select(
                    options={},
                    label="Select task",
                ).classes("flex-1 min-w-[200px]")
                minutes_in = ui.number("Minutes", value=25, min=1, step=5).classes(
                    "w-28"
                )
                ui.button(
                    "Log time",
                    icon="timer",
                    on_click=lambda: self._log_time(log_select, minutes_in, task_table_container),
                ).props("outline")
                ui.button(
                    "Mark done",
                    icon="check",
                    on_click=lambda: self._mark_done(log_select, task_table_container),
                ).props("outline color=positive")

        self._log_select = log_select
        self._refresh_task_table(task_table_container)
        self._refresh_select()

    def _refresh_select(self) -> None:
        opts = {
            tid: f"{t.title} ({t.category})"
            for tid, t in self.analytics._tasks.items()
            if not t.is_completed
        }
        self._log_select.options = opts
        self._log_select.update()

    def _refresh_task_table(self, container: ui.column) -> None:
        container.clear()
        tasks = list(self.analytics._tasks.values())
        if not tasks:
            with container:
                ui.label("No tracked tasks.").classes("text-slate-500 dark:text-slate-400 mt-2")
            return

        rows = [
            {
                "title": t.title,
                "category": t.category,
                "status": "Done" if t.is_completed else "Open",
                "time": f"{t.time_spent_minutes:.0f}m",
            }
            for t in tasks
        ]
        columns = [
            {"name": "title", "label": "Title", "field": "title", "align": "left", "sortable": True},
            {"name": "category", "label": "Category", "field": "category", "align": "left", "sortable": True},
            {"name": "status", "label": "Status", "field": "status", "align": "center", "sortable": True},
            {"name": "time", "label": "Time", "field": "time", "align": "right", "sortable": True},
        ]
        with container:
            ui.table(columns=columns, rows=rows, row_key="title").classes(
                "w-full mt-3"
            ).props("dense flat bordered")

    def _add_task(
        self,
        title_in: ui.input,
        cat_in: ui.select,
        table_container: ui.column,
    ) -> None:
        title = (title_in.value or "").strip()
        if not title:
            notifications.show_error("Please enter a task title.")
            return
        task_id = f"manual-{len(self.analytics._tasks) + 1}-{title[:12]}"
        try:
            self.analytics.add_task(task_id, title, category=cat_in.value)
        except KeyError:
            notifications.show_error("A task with that ID already exists.")
            return
        title_in.value = ""
        notifications.show_success(f"Task '{title}' added.")
        self._refresh_task_table(table_container)
        self._refresh_select()
        ui.navigate.to("/dashboard")

    def _log_time(
        self,
        select: ui.select,
        minutes_in: ui.number,
        table_container: ui.column,
    ) -> None:
        task_id = select.value
        if not task_id:
            notifications.show_error("Select a task first.")
            return
        try:
            self.analytics.log_time(task_id, float(minutes_in.value or 0))
        except (KeyError, ValueError) as e:
            notifications.show_error(str(e))
            return
        notifications.show_success("Time logged.")
        self._refresh_task_table(table_container)
        ui.navigate.to("/dashboard")

    def _mark_done(
        self,
        select: ui.select,
        table_container: ui.column,
    ) -> None:
        task_id = select.value
        if not task_id:
            notifications.show_error("Select a task first.")
            return
        try:
            self.analytics.complete_task(task_id)
        except KeyError as e:
            notifications.show_error(str(e))
            return
        notifications.show_success("Task marked as complete!")
        self._refresh_task_table(table_container)
        self._refresh_select()
        ui.navigate.to("/dashboard")


def _get_first_name() -> str:
    """Resolve the current user's first name for the greeting."""
    try:
        with get_db_context() as db:
            user = get_current_user_from_state(db)
        if user.full_name:
            return user.full_name.split()[0]
        return user.email.split("@")[0]
    except Exception:
        return ""


@ui.page("/dashboard")
def dashboard_page() -> None:
    if not guard_authenticated():
        return
    with dashboard_frame(title="Dashboard"):
        first_name = _get_first_name()
        if first_name:
            ui.label(f"Welcome back, {first_name}").classes(
                "text-h5 font-bold text-emerald-700 dark:text-emerald-300"
            )
        ui.label("Your productivity at a glance.").classes(
            "text-body2 text-slate-600 dark:text-slate-300 max-w-3xl mb-4"
        )
        DashboardView().build()
