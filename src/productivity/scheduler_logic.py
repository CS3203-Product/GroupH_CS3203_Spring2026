"""Grid scheduler logic (importance weekday)."""

from __future__ import annotations
from src.db.session import get_db_context
from src.frontend.components.auth_utils import get_current_user_from_state
from src.repositories.item import item_repo
from datetime import timedelta, datetime

DAY_MAP = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
}

WEEKDAY_TO_INT = {
    "Monday": 0,
    "Tuesday": 1,
    "Wednesday": 2,
    "Thursday": 3,
    "Friday": 4,
    "Saturday": 5,
    "Sunday": 6,
}

class SchedulerLogic:
    def __init__(self):
        self.importance = list(range(0, 21))
        self.tasks = []     # Code Weakness 459: This list must be cleared or synced with the database,                            
                            # because stale tasks left in memory can accumulate over repeated runs and                             
                            # overload the scheduler's memory and/or cause unpredictable behavior. 
                            
    def populate_calendar(self, rows) -> None:
        with get_db_context() as db:
            current_user = get_current_user_from_state(db)

            tasks = item_repo.get_for_user(
                db=db, 
                current_user=current_user,
            )        
            for task in tasks:
                if task.completed:
                    continue

                self.tasks.append(task)

                due_day = DAY_MAP[task.deadline.weekday()] if task.deadline else None

                importance = str(task.user_importance)

                # Find the row that matches the task's importance
                for row in rows:
                    if row["importance"] == importance:
                        if due_day not in [
                            "Sunday",
                            "Monday",
                            "Tuesday",
                            "Wednesday",
                            "Thursday",
                            "Friday",
                            "Saturday",
                        ]:
                            # All tasks should have due dates. Right now none of them do,
                            # so this is just to ensure the auto-populating works
                            if row["no_due_day"]:
                                row["no_due_day"] += f", {task.title}"
                            else:
                                row["no_due_day"] = task.title
                            continue

                        # Append or set the task title in the correct day column
                        if row[due_day]:
                            row[due_day] += f", {task.title}"
                        else:
                            row[due_day] = task.title

    def set_weekday(self, dt, target_weekday: int):
        current = dt.weekday()
        delta = target_weekday - current
        return dt + timedelta(days=delta)

    def update_due_date(self, task_id: int, new_day: str) -> None:
        # CWE‑459: If the DB context manager doesn't clean up the session fully,          
        # it can leak connections, creating memory pressure as the program tries to keep all the leaking connections running,         
        # and again cause unpredictable behavior
        with get_db_context() as db:
            task = item_repo.get(db, task_id)
            if not task:
                print("Task not found:", task_id)
                return

            print(task_id, "is now due on ", new_day)

            target_weekday = WEEKDAY_TO_INT[new_day]

            # Handle missing deadlines
            base_date = task.deadline or datetime.now()

            new_deadline = self.set_weekday(base_date, target_weekday)

            item_repo.update(
                db=db,
                db_obj=task,
                obj_in={"deadline": new_deadline}
            )

            db.refresh(task)  

            print("Updated deadline now:", task.deadline)