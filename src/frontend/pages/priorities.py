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
        
        priority_container = ui.column().classes("w-full space-y-3")
        ui.timer(0.1, lambda: load_priority_tasks(priority_container), once=True)


async def load_priority_tasks(container: ui.column):
    """Load items and sort by AI-predicted priority."""
    try:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)
            items = item_repo.get_for_user(db=db, current_user=current_user)
            user_stats = get_user_stats(db, current_user.id)
        
        container.clear()
        
        # Calculate predictions for each item
        items_with_scores = []
        for item in items:
            try:
                pred_duration = predict_duration(item, user_stats)
                pred_priority = predict_priority(item, user_stats, pred_duration)
                items_with_scores.append({
                    'item': item,
                    'duration': pred_duration,
                    'priority': pred_priority
                })
            except Exception as e:
                # Fallback for items that fail prediction
                items_with_scores.append({
                    'item': item,
                    'duration': 1.0,
                    'priority': 5.0
                })
        
        # Sort by priority (descending)
        items_with_scores.sort(key=lambda x: x['priority'], reverse=True)
        
        with container:
            for idx, data in enumerate(items_with_scores[:20], 1):  # Show top 20
                item = data['item']
                priority = data['priority']
                duration = data['duration']
                
                # Color code priority
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
                            ui.label(f"{idx}. {item.title}").classes("text-lg font-semibold")
                            ui.label(item.description or "No description").classes("text-sm text-gray-500 line-clamp-2")
                        
                        with ui.column().classes("items-end gap-1"):
                            ui.badge(priority_label).props(f"color={color}")
                            ui.label(f"Score: {priority:.1f}/10").classes("text-xs font-bold")
                    
                    ui.separator().classes("w-full my-2")
                    
                    with ui.row().classes("w-full justify-between text-sm"):
                        ui.label(f"Est: {duration:.1f}h").classes("text-slate-600")
                        ui.label(f"Title: {item.title[:30]}...").classes("text-slate-500") if len(item.title) > 30 else None
        
        if not items_with_scores:
            with container:
                ui.label("No tasks yet. Create some tasks to see AI priority recommendations!")
    
    except Exception as e:
        with container:
            ui.label(f"Error loading tasks: {str(e)}").classes("text-red-600")
