from datetime import datetime

from fastapi import HTTPException
from nicegui import ui
from sqlmodel import select

from src.db.models_ai import TaskExecutionLog
from src.ai.auto_retrain import trigger_background_retrain
from src.ai.inference import predict_duration, predict_priority
from src.ai.services import behavior_tracker
from src.ai.task_logger import TaskLogger
from src.ai.user_stats_service import get_user_stats, rebuild_user_stats
from src.core.constants import TASK_CATEGORIES
from src.db.session import get_db_context
from src.frontend.components import notifications
from src.frontend.components.auth_utils import get_current_user_from_state
from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.models import ItemCreate, ItemUpdate
from src.models.models import WeeklyScheduleEntryUpdate
from src.productivity.focus_mode_timer import FocusTaskTimer
from src.repositories.item import item_repo
from src.repositories.weekly_schedule import weekly_schedule_repo

_SCHEDULE_DAYS = ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]
_TASK_CATEGORY_OPTIONS = (
    TASK_CATEGORIES if "general" in TASK_CATEGORIES else ["general", *TASK_CATEGORIES]
)


def _weekly_entry_blurb(entry) -> str:
    cat = getattr(entry, "category", None) or "general"
    return f"{cat} · weekly · {entry.due_day}"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value if value is not None else default)
    except (TypeError, ValueError):
        return default


def _safe_int(value, default: int = 0) -> int:
    try:
        return int(value if value is not None else default)
    except (TypeError, ValueError):
        return default


def _parse_due_date(value) -> datetime | None:
    """Convert the task-board due date input into a deadline datetime."""
    raw = (value or "").strip() if isinstance(value, str) else value
    if not raw:
        return None

    try:
        # Browser date inputs return YYYY-MM-DD. Store it as end-of-day local time.
        return datetime.strptime(str(raw), "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, microsecond=0
        )
    except ValueError as exc:
        raise ValueError("Due date must use YYYY-MM-DD format.") from exc


def _deadline_priority_seed(deadline: datetime | None) -> int:
    """Create a hidden urgency seed from the due date for the priority model."""
    if deadline is None:
        return 5

    hours_until_due = (deadline - datetime.utcnow()).total_seconds() / 3600
    if hours_until_due <= 24:
        return 10
    if hours_until_due <= 48:
        return 9
    if hours_until_due <= 72:
        return 8
    if hours_until_due <= 7 * 24:
        return 7
    if hours_until_due <= 14 * 24:
        return 6
    if hours_until_due <= 30 * 24:
        return 5
    return 4


def _format_deadline(deadline) -> str:
    if not deadline:
        return "No due date"
    if isinstance(deadline, datetime):
        return deadline.strftime("%Y-%m-%d")
    return str(deadline)



def _active_timer_map(db, item_ids: list[int], user_id: int) -> dict[int, TaskExecutionLog]:
    """Return the newest unfinished timer log for each task on the board."""
    if not item_ids:
        return {}

    logs = db.exec(
        select(TaskExecutionLog)
        .where(TaskExecutionLog.task_id.in_(item_ids))
        .where(TaskExecutionLog.user_id == user_id)
        .where(TaskExecutionLog.was_completed == False)  # noqa: E712
        .order_by(TaskExecutionLog.task_id, TaskExecutionLog.id.desc())
    ).all()

    active: dict[int, TaskExecutionLog] = {}
    for log in logs:
        if log.task_id not in active:
            active[log.task_id] = log
    return active


def _format_timer_elapsed(started_at) -> str:
    """Return a compact elapsed-time label for an active task timer."""
    if not started_at:
        return "0m"
    try:
        elapsed_seconds = max(0, (datetime.utcnow() - started_at).total_seconds())
    except TypeError:
        return "0m"

    total_minutes = int(elapsed_seconds // 60)
    hours, minutes = divmod(total_minutes, 60)
    if hours:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


async def update_schedule_entry(
    entry_id: int,
    title_input: ui.input,
    day_input: ui.select,
    importance_value: int,
    category_input: ui.select,
    dialog: ui.dialog,
    grid: ui.grid,
) -> None:
    name = (title_input.value or "").strip()
    day = day_input.value
    category = category_input.value or "general"
    if not name or not day:
        notifications.show_error("Task name and day are required.")
        return
    if day not in _SCHEDULE_DAYS:
        notifications.show_error("Invalid day.")
        return
    imp = max(0, min(20, int(importance_value or 0)))
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            row = weekly_schedule_repo.get_with_permission(
                db=db, id=entry_id, current_user=current_user
            )
            weekly_schedule_repo.update(
                db=db,
                db_obj=row,
                obj_in=WeeklyScheduleEntryUpdate(
                    name=name,
                    due_day=day,
                    importance=imp,
                    category=category,
                ),
            )
        notifications.show_success("Weekly task updated.")
        dialog.close()
        await load_items(grid)
    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")


async def delete_schedule_entry(
    entry_id: int, grid: ui.grid, confirm_dialog: ui.dialog | None = None
) -> None:
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            weekly_schedule_repo.get_with_permission(
                db=db, id=entry_id, current_user=current_user
            )
            weekly_schedule_repo.remove(db=db, id=entry_id)
        if confirm_dialog is not None:
            confirm_dialog.close()
        notifications.show_success("Weekly task removed.")
        await load_items(grid)
    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")


def _render_weekly_schedule_card(entry, grid: ui.grid) -> None:
    with ui.card().classes("p-0 ring-1 ring-emerald-500/40 dark:ring-emerald-400/30"):
        ui.image(f"https://picsum.photos/600/400?random={900000 + entry.id}")
        with ui.column().classes("p-4 w-full"):
            ui.label(entry.name).classes("text-xl font-semibold")
            ui.label("Weekly schedule").classes(
                "text-xs font-medium uppercase tracking-wide text-emerald-700 dark:text-emerald-300"
            )
            ui.separator().classes("w-full my-1")
            ui.label(_weekly_entry_blurb(entry)).classes("text-sm line-clamp-3")

            with ui.row().classes("w-full justify-end mt-4 gap-2"):
                with (
                    ui.dialog() as modify_dialog,
                    ui.card().classes("min-w-[480px]"),
                ):
                    ui.label("Edit weekly task").classes("text-h6")
                    modify_title = ui.input("Task name", value=entry.name).classes(
                        "w-full"
                    )
                    modify_day = ui.select(
                        _SCHEDULE_DAYS,
                        value=entry.due_day,
                        label="Day",
                    ).classes("w-full")
                    modify_cat = ui.select(
                        _TASK_CATEGORY_OPTIONS,
                        value=getattr(entry, "category", None) or "general",
                        label="Category",
                    ).classes("w-full")
                    ui.button(
                        "Save",
                        on_click=lambda: update_schedule_entry(
                            entry.id,
                            modify_title,
                            modify_day,
                            int(entry.importance or 0),
                            modify_cat,
                            modify_dialog,
                            grid,
                        ),
                    ).classes("w-full")

                ui.button(icon="edit", on_click=modify_dialog.open).props("flat dense")

                with ui.dialog() as confirm_dialog, ui.card():
                    ui.label(f"Remove '{entry.name}' from your weekly schedule?")
                    with ui.row().classes("w-full justify-end"):
                        ui.button(
                            "Cancel",
                            on_click=confirm_dialog.close,
                            color="gray-100",
                        )
                        ui.button(
                            "Yes",
                            on_click=lambda eid=entry.id, d=confirm_dialog: delete_schedule_entry(
                                eid, grid, d
                            ),
                            color="red",
                        )

                ui.button(icon="delete", on_click=confirm_dialog.open).props(
                    "flat dense color=red"
                )


@ui.page("/items")
def items_page():
    """Task board backed by the template items API with weekly schedule and AI task metadata."""
    if not guard_authenticated():
        return
    with dashboard_frame(title="Task board"):
        ui.label(
            "Task cards and weekly schedule entries in one place. AI estimates and priority badges help you decide what to work on next."
        ).classes(
            "text-body2 text-slate-600 dark:text-slate-400 max-w-3xl mb-4 self-start"
        )
        items_grid = ui.grid().classes(
            "w-full gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
        )

        with ui.dialog() as dialog, ui.card().classes("min-w-[700px]"):
            ui.label("New task").classes("text-h6")
            title_input = ui.input("Task title").classes("w-full")
            desc_input = ui.textarea("Description").classes("w-full")

            with ui.row().classes("w-full gap-3 flex-wrap items-end"):
                category_input = ui.select(
                    _TASK_CATEGORY_OPTIONS,
                    value="general",
                    label="Category",
                ).classes("min-w-[160px]")

                difficulty_input = ui.number(
                    "Difficulty",
                    value=5,
                    min=1,
                    max=10,
                    step=1,
                ).classes("w-32")

                due_date_input = ui.input(
                    "Due date",
                    placeholder="YYYY-MM-DD",
                ).props("type=date").classes("w-40")

                duration_input = ui.number(
                    "Est. hours",
                    value=1.0,
                    min=0.25,
                    step=0.25,
                ).classes("w-32")

            ui.button(
                "Create task",
                icon="add",
                on_click=lambda: create_item(
                    title_input,
                    desc_input,
                    category_input,
                    difficulty_input,
                    due_date_input,
                    duration_input,
                    dialog,
                    items_grid,
                ),
            ).classes("w-full").props("color=primary")

        ui.button("Add task", on_click=dialog.open, icon="add").props("color=primary")
        ui.timer(0.1, lambda: load_items(items_grid), once=True)


async def load_items(grid: ui.grid):
    """Fetches items and weekly schedule entries, then populates the grid."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            items = item_repo.get_for_user(db=db, current_user=current_user)
            schedule_entries = weekly_schedule_repo.list_for_owner(
                db, owner_id=current_user.id
            )
            user_stats = get_user_stats(db, current_user.id)
            item_ids = [item.id for item in items if item.id is not None]
            active_timers = _active_timer_map(db, item_ids, current_user.id)

        grid.clear()
        with grid:
            for item in items:
                if getattr(item, "completed", False):
                    continue

                active_log = active_timers.get(item.id)

                with ui.card().classes("p-0"):
                    ui.image(f"https://picsum.photos/600/400?random={item.id}")
                    with ui.column().classes("p-4 w-full"):
                        ui.label(item.title).classes("text-xl font-semibold")
                        ui.separator().classes("w-full my-1")
                        ui.label(item.description or "").classes("text-sm line-clamp-3")

                        with ui.row().classes("w-full gap-2 mt-2 flex-wrap"):
                            ui.badge(getattr(item, "category", None) or "general").props(
                                "color=grey"
                            )
                            ui.badge(
                                f"Difficulty: {_safe_int(getattr(item, 'difficulty', 5), 5)}"
                            ).props("color=purple")
                            ui.badge(
                                f"Due: {_format_deadline(getattr(item, 'deadline', None))}"
                            ).props("color=amber")
                            ui.badge(
                                f"Est: {_safe_float(getattr(item, 'estimated_duration', 1.0), 1.0):.1f}h"
                            ).props("color=blue")
                            if active_log is not None:
                                ui.badge(
                                    f"Timer: {_format_timer_elapsed(active_log.started_at)}"
                                ).props("color=green")

                        if active_log is not None:
                            FocusTaskTimer(
                                task_title=item.title,
                                started_at=active_log.started_at,
                                on_complete=lambda item_id=item.id: complete_item(
                                    item_id, grid
                                ),
                                compact=True,
                            )

                        try:
                            pred_duration = predict_duration(item, user_stats)
                            pred_priority = predict_priority(
                                item, user_stats, pred_duration
                            )
                            with ui.row().classes("w-full gap-2 mt-2 mb-2"):
                                ui.badge(f"AI Est: {pred_duration:.1f}h").props(
                                    "color=blue"
                                )
                                ui.badge(f"AI Priority: {pred_priority:.1f}/10").props(
                                    "color=orange"
                                )
                        except Exception:
                            ui.label("Predictions unavailable").classes(
                                "text-xs text-gray-400"
                            )

                        with ui.row().classes("w-full justify-end mt-4 gap-2"):
                            with (
                                ui.dialog() as modify_dialog,
                                ui.card().classes("min-w-[600px]"),
                            ):
                                ui.label("Modify Item").classes("text-h6")
                                modify_title = ui.input(
                                    "Title", value=item.title
                                ).classes("w-full")
                                modify_desc = ui.textarea(
                                    "Description", value=item.description
                                ).classes("w-full")
                                modify_due = ui.input(
                                    "Due date",
                                    value=_format_deadline(getattr(item, "deadline", None))
                                    if getattr(item, "deadline", None)
                                    else "",
                                    placeholder="YYYY-MM-DD",
                                ).props("type=date").classes("w-full")
                                ui.button(
                                    "Save",
                                    on_click=lambda i=item,
                                    t=modify_title,
                                    d=modify_desc,
                                    due=modify_due: update_item(
                                        i.id, t, d, due, modify_dialog, grid
                                    ),
                                ).classes("w-full")

                            ui.button(icon="edit", on_click=modify_dialog.open).props(
                                "flat dense"
                            )

                            if active_log is None:
                                ui.button(
                                    icon="play_arrow",
                                    on_click=lambda item_id=item.id: start_task_timer(
                                        item_id, grid
                                    ),
                                ).props("flat dense color=primary").tooltip(
                                    "Start focus timer"
                                )
                                ui.button(
                                    icon="task_alt",
                                    on_click=lambda item_id=item.id: complete_item(
                                        item_id, grid
                                    ),
                                ).props("flat dense color=green").tooltip(
                                    "Mark task complete without timer"
                                )
                            else:
                                ui.button(
                                    icon="task_alt",
                                    on_click=lambda item_id=item.id: complete_item(
                                        item_id, grid
                                    ),
                                ).props("flat dense color=green").tooltip(
                                    "Complete task and log timer"
                                )

                            with ui.dialog() as confirm_dialog, ui.card():
                                ui.label(
                                    f"Are you sure you want to delete '{item.title}'?"
                                )
                                with ui.row().classes("w-full justify-end"):
                                    ui.button(
                                        "Cancel",
                                        on_click=confirm_dialog.close,
                                        color="gray-100",
                                    )
                                    ui.button(
                                        "Yes",
                                        on_click=lambda item_id=item.id: delete_item(
                                            item_id, grid
                                        ),
                                        color="red",
                                    )

                            ui.button(
                                icon="delete", on_click=confirm_dialog.open
                            ).props("flat dense color=red")

            for entry in schedule_entries:
                _render_weekly_schedule_card(entry, grid)

    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")


async def start_task_timer(item_id: int, grid: ui.grid):
    """Start a focus-style timer for a task and create an unfinished AI log row."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            item = item_repo.get_with_permission(
                db=db,
                id=item_id,
                current_user=current_user,
            )

            existing_log = db.exec(
                select(TaskExecutionLog)
                .where(TaskExecutionLog.task_id == item_id)
                .where(TaskExecutionLog.user_id == current_user.id)
                .where(TaskExecutionLog.was_completed == False)  # noqa: E712
                .order_by(TaskExecutionLog.id.desc())
            ).first()

            if existing_log is not None:
                notifications.show_info("This task timer is already running.")
                await load_items(grid)
                return

            TaskLogger(db).log_task_started(item)

        notifications.show_success("Focus timer started for this task.")
        await load_items(grid)

    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"Could not start task timer: {e}")


async def complete_item(item_id: int, grid: ui.grid):
    """Marks an item complete from the taskboard and syncs DB + AI."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            item = item_repo.get_with_permission(
                db=db,
                id=item_id,
                current_user=current_user,
            )

            if not item:
                notifications.show_error("Task not found.")
                return

            updated_item = item_repo.update_for_user(
                db=db,
                item_id=item_id,
                obj_in=ItemUpdate(completed=True),
                current_user=current_user,
            )

            existing_log = db.exec(
                select(TaskExecutionLog)
                .where(TaskExecutionLog.task_id == item_id)
                .where(TaskExecutionLog.user_id == current_user.id)
                .where(TaskExecutionLog.was_completed == False)  # noqa: E712
                .order_by(TaskExecutionLog.id.desc())
            ).first()

            logger = TaskLogger(db)
            if existing_log is None:
                logger.log_task_started(updated_item)
            logger.log_task_completed(updated_item)

            owner_id = updated_item.owner_id
            title = updated_item.title
            rebuild_user_stats(db, owner_id)

        behavior_tracker.build_behavior_profile(owner_id)
        # trigger_background_retrain()  # disabled during UI actions to prevent NiceGUI reconnects

        notifications.show_success(f"Task '{title}' marked as completed.")
        await load_items(grid)

    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"Could not mark task complete: {e}")


async def create_item(
    title_input: ui.input,
    desc_input: ui.textarea,
    category_input: ui.select,
    difficulty_input: ui.number,
    due_date_input: ui.input,
    duration_input: ui.number,
    dialog: ui.dialog,
    grid: ui.grid,
):
    """Creates a new AI-ready task from the taskboard."""
    title = (title_input.value or "").strip()

    if not title:
        notifications.show_error("Please enter a task title.")
        return

    try:
        deadline = _parse_due_date(due_date_input.value)
    except ValueError as e:
        notifications.show_error(str(e))
        return

    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            item_in = ItemCreate(
                title=title,
                description=desc_input.value or "",
                category=category_input.value or "general",
                difficulty=int(difficulty_input.value or 5),
                # Hidden model feature: urgency is inferred from due date, not typed by the user.
                user_importance=_deadline_priority_seed(deadline),
                estimated_duration=float(duration_input.value or 1.0),
                deadline=deadline,
            )

            item_repo.create_for_user(
                db=db,
                obj_in=item_in,
                current_user=current_user,
            )

        notifications.show_success(f"Task '{title}' created successfully.")

        title_input.value = ""
        desc_input.value = ""
        category_input.value = "general"
        difficulty_input.value = 5
        due_date_input.value = ""
        duration_input.value = 1.0

        dialog.close()
        # trigger_background_retrain()  # disabled during UI actions to prevent NiceGUI reconnects
        await load_items(grid)

    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")


async def update_item(
    item_id: int,
    title_input: ui.input,
    desc_input: ui.textarea,
    due_date_input: ui.input,
    dialog: ui.dialog,
    grid: ui.grid,
):
    """Updates an item by directly calling repository functions."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            deadline = _parse_due_date(due_date_input.value)
            item_in = ItemUpdate(
                title=title_input.value,
                description=desc_input.value,
                deadline=deadline,
                user_importance=_deadline_priority_seed(deadline),
            )
            item_repo.update_for_user(
                db=db,
                item_id=item_id,
                obj_in=item_in,
                current_user=current_user,
            )

        notifications.show_success("Item updated successfully.")
        dialog.close()
        # trigger_background_retrain()  # disabled during UI actions to prevent NiceGUI reconnects
        await load_items(grid)

    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")


async def delete_item(item_id: int, grid: ui.grid):
    """Deletes an item by directly calling repository functions."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            item_repo.delete_for_user(db=db, item_id=item_id, current_user=current_user)

        notifications.show_success("Item deleted successfully.")
        # trigger_background_retrain()  # disabled during UI actions to prevent NiceGUI reconnects
        await load_items(grid)

    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")
