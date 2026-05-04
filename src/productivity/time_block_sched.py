"""NiceGUI weekly grid for time blocking."""

from collections import defaultdict

from fastapi import HTTPException
from nicegui import ui

from src.core.constants import TASK_CATEGORIES
from src.db.session import get_db_context
from src.frontend.components import notifications
from src.frontend.components.auth_utils import get_current_user_from_state
from src.productivity.scheduling_task import SchedulingTask as Task
from src.repositories.weekly_schedule import weekly_schedule_repo

_VALID_DAYS = frozenset(["sun", "mon", "tues", "wed", "thur", "fri", "sat"])

_DAY_ORDER = {
    "sun": 0,
    "mon": 1,
    "tues": 2,
    "wed": 3,
    "thur": 4,
    "fri": 5,
    "sat": 6,
}


class TimeBlockingScheduler:
    def __init__(self) -> None:
        ui.label("Weekly schedule").classes(
            "text-h5 font-semibold text-emerald-800 dark:text-emerald-200"
        )
        self.error_label = ui.label("").classes("text-red-600")

        self.columns = [
            {"name": "importance", "label": "Importance", "field": "importance"},
            {"name": "sun", "label": "Sunday", "field": "sun"},
            {"name": "mon", "label": "Monday", "field": "mon"},
            {"name": "tues", "label": "Tuesday", "field": "tues"},
            {"name": "wed", "label": "Wednesday", "field": "wed"},
            {"name": "thur", "label": "Thursday", "field": "thur"},
            {"name": "fri", "label": "Friday", "field": "fri"},
            {"name": "sat", "label": "Saturday", "field": "sat"},
        ]

        importance = list(range(0, 21))

        self.rows = [
            {
                "importance": str(t),
                "sun": "",
                "mon": "",
                "tues": "",
                "wed": "",
                "thur": "",
                "fri": "",
                "sat": "",
            }
            for t in importance
        ]
        self.tasks: list[Task] = []

        with ui.row().classes("flex-wrap gap-2 items-end"):
            self.task_name_input = ui.input("Task name").classes("min-w-[12rem]")
            self.day_input = ui.select(
                ["sun", "mon", "tues", "wed", "thur", "fri", "sat"],
                label="Due day",
            )
            self.importance_input = ui.number(
                "Importance (0–20)", min=0, max=20, value=0
            )
            self.category_input = ui.select(
                TASK_CATEGORIES,
                value="general",
                label="Category",
            ).classes("min-w-[10rem]")
            ui.button("Add task", on_click=self.add_task).props("color=primary")

        self.table = ui.table(columns=self.columns, rows=self.rows).classes("w-full")

        ui.label("Reorder (within same day & importance)").classes(
            "text-subtitle2 font-semibold text-slate-700 dark:text-slate-200 mt-6 mb-1"
        )
        ui.label(
            "Use ↑ / ↓ to change the order tasks appear in each grid cell."
        ).classes("text-caption text-slate-500 dark:text-slate-400 mb-2")
        self.reorder_column = ui.column().classes("w-full gap-1")

        self._load_from_db()

    def _shift_task(self, entry_id: int | None, delta: int) -> None:
        if entry_id is None:
            return
        try:
            with get_db_context() as db:
                user = get_current_user_from_state(db)
                weekly_schedule_repo.shift_sort_order_in_cell(
                    db, entry_id=entry_id, delta=delta, current_user=user
                )
        except HTTPException as e:
            notifications.show_error(e.detail)
            return
        except Exception as e:
            notifications.show_error(f"Could not reorder: {e}")
            return
        self._load_from_db()

    def _refresh_reorder_panel(self) -> None:
        self.reorder_column.clear()
        ordered = sorted(
            self.tasks,
            key=lambda t: (
                _DAY_ORDER.get(t.due_day, 99),
                t.importance,
                t.sort_order,
                t.name,
            ),
        )
        with self.reorder_column:
            for task in ordered:
                bucket = [
                    x
                    for x in self.tasks
                    if x.importance == task.importance and x.due_day == task.due_day
                ]
                bucket.sort(key=lambda x: (x.sort_order, x.name))
                idx = next(
                    (
                        i
                        for i, x in enumerate(bucket)
                        if x.entry_id == task.entry_id
                    ),
                    -1,
                )
                tot = len(bucket)
                can_up = idx > 0 and task.entry_id is not None
                can_down = 0 <= idx < tot - 1 and task.entry_id is not None

                with ui.row().classes(
                    "w-full flex-wrap items-center gap-2 py-1 border-b border-slate-200/50 dark:border-slate-600/50"
                ):
                    ui.label(
                        f"{task.due_day} · imp {task.importance} · {task.category}"
                    ).classes("text-xs text-slate-500 dark:text-slate-400 shrink-0")
                    ui.label(task.name).classes(
                        "flex-1 min-w-[120px] text-sm font-medium"
                    )
                    up_btn = ui.button(
                        icon="keyboard_arrow_up",
                        on_click=lambda eid=task.entry_id: self._shift_task(eid, -1),
                    ).props("flat dense round size=sm")
                    down_btn = ui.button(
                        icon="keyboard_arrow_down",
                        on_click=lambda eid=task.entry_id: self._shift_task(eid, 1),
                    ).props("flat dense round size=sm")
                    if not can_up:
                        up_btn.disable()
                    if not can_down:
                        down_btn.disable()

    def _load_from_db(self) -> None:
        try:
            with get_db_context() as db:
                user = get_current_user_from_state(db)
                entries = weekly_schedule_repo.list_for_owner(db, owner_id=user.id)
            self.tasks = [
                Task(
                    e.name,
                    e.due_day,
                    max(0, min(20, int(e.importance))),
                    entry_id=e.id,
                    category=getattr(e, "category", None) or "general",
                    sort_order=int(getattr(e, "sort_order", 0) or 0),
                )
                for e in entries
            ]
            self.populate_calendar()
            self.table.rows = self.rows
            self.table.update()
            self._refresh_reorder_panel()
        except HTTPException as e:
            notifications.show_error(e.detail)
        except Exception as e:
            notifications.show_error(f"Could not load schedule: {e}")

    def add_task(self) -> None:
        name = (self.task_name_input.value or "").strip()
        day = self.day_input.value
        importance = self.importance_input.value
        category = self.category_input.value or "general"

        if not name or not day:
            self.error_label.text = "Please enter a task name and select a day."
            return

        if day not in _VALID_DAYS:
            self.error_label.text = "Invalid day."
            return

        imp = max(0, min(20, int(importance or 0)))

        self.error_label.text = ""

        try:
            with get_db_context() as db:
                user = get_current_user_from_state(db)
                entry = weekly_schedule_repo.create(
                    db,
                    owner_id=user.id,
                    name=name,
                    due_day=day,
                    importance=imp,
                    category=category,
                )
        except HTTPException as e:
            notifications.show_error(e.detail)
            return
        except Exception as e:
            notifications.show_error(f"Could not save task: {e}")
            return

        new_task = Task(
            name,
            day,
            imp,
            entry_id=entry.id,
            category=entry.category or "general",
            sort_order=int(entry.sort_order or 0),
        )
        self.tasks.append(new_task)

        self.populate_calendar()
        self.table.rows = self.rows
        self.table.update()
        self._refresh_reorder_panel()

        self.task_name_input.value = ""
        self.day_input.value = None
        self.importance_input.value = 0
        self.category_input.value = "general"

    def populate_calendar(self) -> None:
        for row in self.rows:
            for d in ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]:
                row[d] = ""

        groups: dict[tuple[int, str], list[Task]] = defaultdict(list)
        for task in self.tasks:
            groups[(task.importance, task.due_day)].append(task)

        for (imp, day), bucket in groups.items():
            bucket.sort(key=lambda t: (t.sort_order, t.name))
            target_row = self.rows[imp]
            target_row[day] = ", ".join(t.name for t in bucket)
