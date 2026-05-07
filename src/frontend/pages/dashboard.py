"""Dashboard — real-time overview of tasks, analytics, DB state, and AI predictions."""

from __future__ import annotations

from fastapi import HTTPException
from nicegui import ui
from sqlmodel import select

from src.ai.auto_retrain import trigger_background_retrain
from src.ai.inference import predict_duration, predict_priority
from src.ai.task_logger import TaskLogger
from src.ai.user_stats_service import get_user_stats, rebuild_user_stats
from src.db.models_ai import TaskExecutionLog
from src.db.session import get_db_context
from src.frontend.components import notifications
from src.frontend.components.auth_utils import get_current_user_from_state
from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.models import ItemCreate, ItemUpdate
from src.productivity.task_analytics_dashboard import TaskAnalyticsDashboard
from src.repositories.item import item_repo
from src.repositories.weekly_schedule import weekly_schedule_repo


REFRESH_SECONDS = 3.0


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
    for task in analytics._tasks.values():
        entry = cats.setdefault(task.category or "general", {"done": 0, "open": 0})
        if task.is_completed:
            entry["done"] += 1
        else:
            entry["open"] += 1

    categories = list(cats.keys()) or ["(none)"]
    done_vals = [cats.get(c, {}).get("done", 0) for c in categories]
    open_vals = [cats.get(c, {}).get("open", 0) for c in categories]

    ui.echart(
        {
            "tooltip": {"trigger": "axis", "axisPointer": {"type": "shadow"}},
            "legend": {"top": "0%", "textStyle": {"color": "#94a3b8"}},
            "grid": {
                "left": "3%",
                "right": "4%",
                "top": "15%",
                "bottom": "3%",
                "containLabel": True,
            },
            "xAxis": {
                "type": "category",
                "data": categories,
                "axisLabel": {"color": "#94a3b8", "interval": 0},
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
        task for task in analytics._tasks.values() if task.time_spent_minutes > 0
    ]
    tasks_with_time.sort(key=lambda task: task.time_spent_minutes, reverse=True)
    tasks_with_time = tasks_with_time[:10]

    labels = [task.title[:24] for task in tasks_with_time] or ["(none)"]
    values = [round(task.time_spent_minutes, 1) for task in tasks_with_time] or [0]

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
    """Manages the dashboard UI and keeps it synced with SQLModel + AI."""

    def __init__(self) -> None:
        self.analytics = TaskAnalyticsDashboard()
        self._log_select: ui.select | None = None
        self._metrics_container: ui.row | None = None
        self._charts_container: ui.column | None = None
        self._table_container: ui.column | None = None
        self._refreshing = False

    def _sync_from_db(self) -> tuple[int, str]:
        """Refresh analytics from persisted items and update AI predictions."""
        try:
            with get_db_context() as db:
                current_user = get_current_user_from_state(db)
                items = item_repo.get_for_user(db=db, current_user=current_user)
                user_stats = get_user_stats(db, current_user.id)

                logs = db.exec(
                    select(TaskExecutionLog).where(TaskExecutionLog.user_id == current_user.id)
                ).all()
                minutes_by_task_id: dict[int, float] = {}
                for log in logs:
                    if log.actual_duration:
                        minutes_by_task_id[log.task_id] = (
                            minutes_by_task_id.get(log.task_id, 0.0)
                            + float(log.actual_duration) * 60
                        )

                active_task_ids: set[str] = set()
                for item in items:
                    task_id = f"item-{item.id}"
                    active_task_ids.add(task_id)

                    predicted_duration = getattr(item, "predicted_duration", None)
                    predicted_priority = getattr(item, "predicted_priority", None)

                    try:
                        predicted_duration = predict_duration(item, user_stats)
                        predicted_priority = predict_priority(
                            item, user_stats, predicted_duration
                        )

                        # Store the latest predictions so other pages can use them too.
                        item.predicted_duration = predicted_duration
                        item.predicted_priority = predicted_priority
                        db.add(item)
                    except Exception:
                        # The dashboard should still render even if models are missing.
                        pass

                    self.analytics.upsert_task(
                        task_id=task_id,
                        db_id=item.id,
                        title=item.title,
                        category=getattr(item, "category", "general") or "general",
                        user_id=item.owner_id,
                        difficulty=getattr(item, "difficulty", 5),
                        user_importance=getattr(item, "user_importance", 5),
                        estimated_duration=getattr(item, "estimated_duration", 1.0),
                        deadline=getattr(item, "deadline", None),
                        is_completed=bool(item.completed),
                        predicted_duration=predicted_duration,
                        predicted_priority=predicted_priority,
                        time_spent_minutes=minutes_by_task_id.get(item.id, 0.0),
                    )

                self.analytics.remove_missing(active_task_ids)
                db.commit()

                first_name = (
                    current_user.full_name.split()[0]
                    if current_user.full_name
                    else current_user.email.split("@")[0]
                )
                return len(items), first_name
        except HTTPException as e:
            notifications.show_error(e.detail)
            return 0, ""
        except Exception as e:
            notifications.show_error(f"Could not sync dashboard: {e}")
            return 0, ""

    def build(self) -> None:
        """Build dashboard shell once, then refresh data in-place."""
        self._sync_from_db()

        self._metrics_container = ui.row().classes("w-full flex-wrap gap-4")
        self._charts_container = ui.column().classes("w-full")
        self._build_tracker_panel()

        self.refresh()
        ui.timer(REFRESH_SECONDS, self.refresh)

    def refresh(self) -> None:
        """Refresh dashboard data without navigating or rebuilding the whole page."""
        if self._refreshing:
            return

        self._refreshing = True
        try:
            self._sync_from_db()
            self._refresh_metrics()
            self._refresh_charts()
            self._refresh_task_table()
            self._refresh_select()
        finally:
            self._refreshing = False

    def _refresh_metrics(self) -> None:
        if not self._metrics_container:
            return

        total = self.analytics.total_tasks
        completed = self.analytics.completed_tasks
        pending = total - completed
        time_spent = self.analytics.total_time_spent

        self._metrics_container.clear()
        with self._metrics_container:
            _stat_card("assignment", str(total), "Total tasks", "emerald-500")
            _stat_card("check_circle", str(completed), "Completed", "green-500")
            _stat_card("pending", str(pending), "In progress", "amber-500")
            _stat_card("schedule", f"{time_spent:.0f}m", "Time logged", "sky-500")

    def _refresh_charts(self) -> None:
        if not self._charts_container:
            return

        total = self.analytics.total_tasks
        completed = self.analytics.completed_tasks
        pending = total - completed
        time_spent = self.analytics.total_time_spent

        self._charts_container.clear()
        with self._charts_container:
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
                ui.label("Time spent from completed AI logs").classes(
                    "text-sm font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400 mb-2"
                )
                if time_spent > 0:
                    _build_time_chart(self.analytics)
                else:
                    ui.label("Complete tasks to populate this chart from AI logs.").classes(
                        "text-slate-500 dark:text-slate-400 py-4 text-center w-full"
                    )

    def _build_tracker_panel(self) -> None:
        """Quick-add panel for DB-backed task creation, completion, and refresh."""
        ui.label("Quick tracker").classes(
            "text-h6 font-bold text-emerald-700 dark:text-emerald-300 mt-6 mb-2"
        )

        with ui.card().classes("w-full p-5"):
            with ui.row().classes("w-full gap-3 flex-wrap items-end"):
                title_in = ui.input("Task title").classes("flex-1 min-w-[160px]")
                cat_in = ui.select(
                    ["general", "work", "study", "health", "personal", "programming", "reading"],
                    value="general",
                    label="Category",
                ).classes("min-w-[140px]")
                difficulty_in = ui.number("Difficulty", value=5, min=1, max=10, step=1).classes("w-32")
                importance_in = ui.number("Importance", value=5, min=1, max=10, step=1).classes("w-32")
                duration_in = ui.number("Est. hours", value=1.0, min=0.25, step=0.25).classes("w-32")
                ui.button(
                    "Add task",
                    icon="add",
                    on_click=lambda: self._add_task(
                        title_in,
                        cat_in,
                        difficulty_in,
                        importance_in,
                        duration_in,
                    ),
                ).props("color=primary")
                ui.button("Refresh", icon="refresh", on_click=self.refresh).props("outline")

            ui.separator().classes("my-3")

            with ui.row().classes("w-full gap-3 flex-wrap items-end"):
                self._log_select = ui.select(options={}, label="Select open task").classes(
                    "flex-1 min-w-[200px]"
                )
                ui.button(
                    "Mark done",
                    icon="check",
                    on_click=lambda: self._mark_done(self._log_select),
                ).props("outline color=positive")

        self._table_container = ui.column().classes("w-full")

    def _refresh_select(self) -> None:
        if not self._log_select:
            return

        opts = {
            task_id: f"{task.title} ({task.category})"
            for task_id, task in self.analytics._tasks.items()
            if not task.is_completed
        }
        previous_value = self._log_select.value
        self._log_select.options = opts
        self._log_select.value = previous_value if previous_value in opts else None
        self._log_select.update()

    def _refresh_task_table(self) -> None:
        if not self._table_container:
            return

        self._table_container.clear()
        tasks = sorted(
            self.analytics._tasks.values(),
            key=lambda task: (task.is_completed, task.title.lower()),
        )
        if not tasks:
            with self._table_container:
                ui.label("No tracked tasks.").classes("text-slate-500 dark:text-slate-400 mt-2")
            return

        rows = [
            {
                "title": task.title,
                "category": task.category,
                "status": "Done" if task.is_completed else "Open",
                "time": f"{task.time_spent_minutes:.0f}m",
                "duration": (
                    f"{task.predicted_duration:.1f}h"
                    if task.predicted_duration is not None
                    else "—"
                ),
                "priority": (
                    f"{task.predicted_priority:.1f}"
                    if task.predicted_priority is not None
                    else "—"
                ),
            }
            for task in tasks
        ]
        columns = [
            {"name": "title", "label": "Title", "field": "title", "align": "left", "sortable": True},
            {"name": "category", "label": "Category", "field": "category", "align": "left", "sortable": True},
            {"name": "status", "label": "Status", "field": "status", "align": "center", "sortable": True},
            {"name": "duration", "label": "AI duration", "field": "duration", "align": "right", "sortable": True},
            {"name": "priority", "label": "AI priority", "field": "priority", "align": "right", "sortable": True},
            {"name": "time", "label": "Logged time", "field": "time", "align": "right", "sortable": True},
        ]
        with self._table_container:
            ui.table(columns=columns, rows=rows, row_key="title").classes(
                "w-full mt-3"
            ).props("dense flat bordered")

    def _add_task(
        self,
        title_in: ui.input,
        cat_in: ui.select,
        difficulty_in: ui.number,
        importance_in: ui.number,
        duration_in: ui.number,
    ) -> None:
        title = (title_in.value or "").strip()
        if not title:
            notifications.show_error("Please enter a task title.")
            return

        try:
            with get_db_context() as db:
                current_user = get_current_user_from_state(db)
                item_in = ItemCreate(
                    title=title,
                    description="",
                    category=cat_in.value or "general",
                    difficulty=int(difficulty_in.value or 5),
                    user_importance=int(importance_in.value or 5),
                    estimated_duration=float(duration_in.value or 1.0),
                )
                item_repo.create_for_user(db=db, obj_in=item_in, current_user=current_user)
        except HTTPException as e:
            notifications.show_error(e.detail)
            return
        except Exception as e:
            notifications.show_error(f"Could not create task: {e}")
            return

        title_in.value = ""
        notifications.show_success(f"Task '{title}' added.")
        trigger_background_retrain()
        self.refresh()

    def _mark_done(self, select: ui.select | None) -> None:
        if not select or not select.value:
            notifications.show_error("Select a task first.")
            return

        try:
            record = self.analytics.get_task(select.value)
            with get_db_context() as db:
                current_user = get_current_user_from_state(db)
                item = item_repo.get_with_permission(
                    db=db,
                    id=record.id,
                    current_user=current_user,
                )

                if not item.completed:
                    item = item_repo.update_for_user(
                        db=db,
                        item_id=record.id,
                        obj_in=ItemUpdate(completed=True),
                        current_user=current_user,
                    )

                logger = TaskLogger(db)
                logger.log_task_started(item)
                logger.log_task_completed(item)
                rebuild_user_stats(db, item.owner_id)

            self.analytics.complete_task(select.value)
        except KeyError as e:
            notifications.show_error(str(e))
            return
        except HTTPException as e:
            notifications.show_error(e.detail)
            return
        except Exception as e:
            notifications.show_error(f"Could not complete task: {e}")
            return

        notifications.show_success("Task marked as complete and synced with AI.")
        trigger_background_retrain()
        self.refresh()


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
        ui.label("Your productivity at a glance. Auto-refreshes from PostgreSQL and AI predictions.").classes(
            "text-body2 text-slate-600 dark:text-slate-300 max-w-3xl mb-4"
        )
        DashboardView().build()
