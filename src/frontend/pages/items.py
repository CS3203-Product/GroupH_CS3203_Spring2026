from fastapi import HTTPException
from nicegui import ui
from src.models import ItemCreate, ItemUpdate
from src.repositories.item import item_repo
from src.db.session import get_db_context
from src.ai.task_logger import TaskLogger
from src.frontend.components import notifications
from src.frontend.components.auth_utils import get_current_user_from_state
from src.frontend.layouts.default import dashboard_frame, guard_authenticated
from src.ai.inference import predict_duration, predict_priority
from src.ai.services import task_logger, behavior_tracker
from src.ai.user_stats_service import get_user_stats, rebuild_user_stats
from src.ai.auto_retrain import trigger_background_retrain


@ui.page("/items")
def items_page():
    """Task board backed by the template items API (cards per item)."""
    if not guard_authenticated():
        return
    with dashboard_frame(title="Task board"):
        ui.label(
            "Lightweight cards tied to your account — use this area for quick notes or demos."
        ).classes("text-body2 text-slate-600 dark:text-slate-400 max-w-3xl mb-4 self-start")
        items_grid = ui.grid().classes(
            "w-full gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4"
        )

        with ui.dialog() as dialog, ui.card().classes("min-w-[600px]"):
            ui.label("New card").classes("text-h6")
            title_input = ui.input("Title").classes("w-full")
            desc_input = ui.textarea("Description").classes("w-full")
            ui.button(
                "Create",
                on_click=lambda: create_item(
                    title_input,
                    desc_input,
                    dialog,
                    items_grid,
                ),
            ).classes("w-full")

        ui.button("Add card", on_click=dialog.open, icon="add").props("color=primary")
        ui.timer(0.1, lambda: load_items(items_grid), once=True)


async def load_items(grid: ui.grid):
    """Fetches items by directly calling repository functions and populates the grid."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            items = item_repo.get_for_user(db=db, current_user=current_user)
            user_stats = get_user_stats(db, current_user.id)

        grid.clear()
        with grid:
            for item in items:
                if getattr(item, "completed", False):
                    continue
                with ui.card().classes("p-0"):
                    ui.image(f"https://picsum.photos/600/400?random={item.id}")
                    with ui.column().classes("p-4 w-full"):
                        ui.label(item.title).classes("text-xl font-semibold")
                        ui.separator().classes("w-full my-1")
                        ui.label(item.description).classes("text-sm line-clamp-3")
                        
                        # AI Predictions
                        try:
                            pred_duration = predict_duration(item, user_stats)
                            pred_priority = predict_priority(item, user_stats, pred_duration)
                            
                            with ui.row().classes("w-full gap-2 mt-2 mb-2"):
                                ui.badge(f"Est: {pred_duration:.1f}h").props("color=blue")
                                ui.badge(f"Priority: {pred_priority:.1f}/10").props("color=orange")
                        except Exception as e:
                            ui.label("Predictions unavailable").classes("text-xs text-gray-400")

                        with ui.row().classes("w-full justify-end mt-4 gap-2"):
                            # Modify Button - opens its own dialog
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
                                # The lambda captures the item's specific data for the handler
                                ui.button(
                                    "Save",
                                    on_click=lambda i=item,
                                    t=modify_title,
                                    d=modify_desc: update_item(
                                        i.id,
                                        t,
                                        d,
                                        modify_dialog,
                                        grid,
                                    ),
                                ).classes("w-full")

                            ui.button(icon="edit", on_click=modify_dialog.open).props(
                                "flat dense"
                            )

                            ui.button(
                                icon="task_alt",
                                on_click=lambda item_id=item.id: complete_item(item_id, grid),
                            ).props("flat dense color=green").tooltip("Mark task complete")

                            # Delete Button - opens a confirmation dialog
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
                                    # The lambda captures the specific item_id for the handler
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
    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")

async def complete_item(item_id: int, grid: ui.grid):
    """Marks an item complete from the taskboard and syncs DB + AI."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            # Get a fresh Item inside the active session
            item = item_repo.get_with_permission(
                db=db,
                id=item_id,
                current_user=current_user,
            )

            if not item:
                notifications.show_error("Task not found.")
                return

            # Mark the actual task complete
            updated_item = item_repo.update_for_user(
                db=db,
                item_id=item_id,
                obj_in=ItemUpdate(completed=True),
                current_user=current_user,
            )

            # Log AI task activity using the active DB session
            logger = TaskLogger(db)

            logger.log_task_started(updated_item)
            logger.log_task_completed(updated_item)

            # Rebuild user stats while still using safe values
            owner_id = updated_item.owner_id
            title = updated_item.title

            rebuild_user_stats(db, owner_id)

        # Outside the DB session, only use copied primitive values
        behavior_tracker.build_behavior_profile(owner_id)
        trigger_background_retrain()

        notifications.show_success(
            f"Task '{title}' marked as completed."
        )

        await load_items(grid)

    except HTTPException as e:
        notifications.show_error(e.detail)

    except Exception as e:
        notifications.show_error(f"Could not mark task complete: {e}")

async def create_item(
    title_input: ui.input,
    desc_input: ui.textarea,
    dialog: ui.dialog,
    grid: ui.grid,
):
    """Creates a new item by directly calling repository functions."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            item_in = ItemCreate(title=title_input.value, description=desc_input.value)
            item_repo.create_for_user(db=db, obj_in=item_in, current_user=current_user)

        notifications.show_success("Item created successfully!")
        dialog.close()
        await load_items(grid)
    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")


async def update_item(
    item_id: int,
    title_input: ui.input,
    desc_input: ui.textarea,
    dialog: ui.dialog,
    grid: ui.grid,
):
    """Updates an item by directly calling repository functions."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            item_in = ItemUpdate(title=title_input.value, description=desc_input.value)
            item_repo.update_for_user(
                db=db,
                item_id=item_id,
                obj_in=item_in,
                current_user=current_user,
            )

        notifications.show_success("Item updated successfully.")
        dialog.close()
        trigger_background_retrain()
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
        trigger_background_retrain()
        await load_items(grid)

    except HTTPException as e:
        notifications.show_error(e.detail)
    except Exception as e:
        notifications.show_error(f"An unexpected error occurred: {e}")
