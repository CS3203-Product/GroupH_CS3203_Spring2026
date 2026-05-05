"""Task prioritization page."""

from nicegui import ui

from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.frontend.components.auth_utils import get_current_user_from_state
from src.db.session import get_db_context
from src.repositories.item import item_repo
from src.ai.inference import predict_duration, predict_priority
from src.ai.user_stats_service import get_user_stats


@ui.page("/priorities")
def priorities_page() -> None:
    if not guard_authenticated():
        return

    with dashboard_frame(title="Priorities"):
        ui.label("AI-sorted tasks by priority. Higher scores = more urgent.").classes(
            "text-body2 text-slate-600 dark:text-slate-300 mb-4"
        )

        with ui.row().classes("items-center gap-2 mb-4"):
            ui.button(
                "Refresh priorities",
                icon="refresh",
                on_click=lambda: load_priority_tasks(priority_container),
            ).props("color=primary")

        priority_container = ui.column().classes("w-full space-y-3")

        # Initial load
        ui.timer(
            0.1,
            lambda: load_priority_tasks(priority_container),
            once=True,
        )

        # Auto-refresh so completed tasks disappear after taskboard/dashboard updates
        ui.timer(
            3.0,
            lambda: load_priority_tasks(priority_container),
        )


def load_priority_tasks(container: ui.column):
    """Load incomplete items and sort by AI-predicted priority."""

    try:
        task_rows = []

        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            if not current_user:
                container.clear()
                with container:
                    ui.label("Please log in to view priorities.").classes(
                        "text-red-600"
                    )
                return

            items = item_repo.get_for_user(
                db=db,
                current_user=current_user,
            )

            user_stats = get_user_stats(
                db,
                current_user.id,
            )

            for item in items:
                # Do not show completed tasks on priorities page
                if item.completed:
                    continue

                try:
                    predicted_duration = item.predicted_duration

                    if predicted_duration is None:
                        predicted_duration = predict_duration(
                            item,
                            user_stats,
                        )
                        item.predicted_duration = predicted_duration

                    predicted_priority = item.predicted_priority

                    if predicted_priority is None:
                        predicted_priority = predict_priority(
                            item,
                            user_stats,
                            predicted_duration,
                        )
                        item.predicted_priority = predicted_priority

                    db.add(item)

                except Exception:
                    predicted_duration = item.estimated_duration or 1.0
                    predicted_priority = item.user_importance or 5.0

                # Convert SQLModel object into plain dict while session is open
                task_rows.append(
                    {
                        "id": item.id,
                        "title": item.title,
                        "description": item.description,
                        "category": item.category or "general",
                        "difficulty": item.difficulty,
                        "user_importance": item.user_importance,
                        "estimated_duration": item.estimated_duration,
                        "predicted_duration": predicted_duration,
                        "predicted_priority": predicted_priority,
                        "deadline": item.deadline,
                    }
                )

            db.commit()

        # Sort outside session using plain dictionaries
        task_rows.sort(
            key=lambda task: task["predicted_priority"] or 0,
            reverse=True,
        )

        container.clear()

        with container:
            if not task_rows:
                ui.label(
                    "No open tasks to prioritize. Completed tasks are hidden."
                ).classes("text-gray-500 italic")
                return

            for idx, task in enumerate(task_rows[:20], 1):
                render_priority_card(idx, task)

    except Exception as e:
        container.clear()

        with container:
            ui.label(f"Error loading priorities: {e}").classes(
                "text-red-600"
            )


def render_priority_card(idx: int, task: dict):
    priority = task["predicted_priority"] or 0
    duration = task["predicted_duration"] or task["estimated_duration"] or 1.0

    if priority >= 8:
        color = "red"
        priority_label = "URGENT"
    elif priority >= 6:
        color = "orange"
        priority_label = "HIGH"
    elif priority >= 4:
        color = "blue"
        priority_label = "MEDIUM"
    else:
        color = "green"
        priority_label = "LOW"

    with ui.card().classes("w-full p-4"):
        with ui.row().classes("w-full justify-between items-start"):
            with ui.column().classes("flex-grow"):
                ui.label(f"{idx}. {task['title']}").classes(
                    "text-lg font-semibold"
                )

                ui.label(
                    task["description"] or "No description"
                ).classes("text-sm text-gray-500 line-clamp-2")

            with ui.column().classes("items-end gap-1"):
                ui.badge(priority_label).props(f"color={color}")
                ui.label(f"Score: {priority:.1f}/10").classes(
                    "text-xs font-bold"
                )

        ui.separator().classes("w-full my-2")

        with ui.row().classes("w-full justify-between text-sm"):
            ui.label(f"Est: {duration:.1f}h").classes("text-slate-600")
            ui.label(f"Difficulty: {task['difficulty']}").classes("text-slate-500")
            ui.label(f"Importance: {task['user_importance']}").classes("text-slate-500")
            ui.label(f"Category: {task['category']}").classes("text-slate-500")

        if task["deadline"]:
            ui.label(f"Deadline: {task['deadline']}").classes(
                "text-xs text-slate-500 mt-2"
            )