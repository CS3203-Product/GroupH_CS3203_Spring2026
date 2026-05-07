from datetime import datetime

from src.db.models_ai import TaskExecutionLog
from src.ai.user_stats_service import rebuild_user_stats
from sqlmodel import select

class TaskLogger:

    def __init__(self, session):
        self.session = session

    def _get_task_attr(self, task, name, default=None):
        return getattr(task, name, default)

    # =====================================
    # TASK STARTED
    # =====================================

    def log_task_started(self, task):

        log = TaskExecutionLog(
            user_id=self._get_task_attr(task, "owner_id", self._get_task_attr(task, "user_id", 0)),
            task_id=self._get_task_attr(task, "id", 0),
            category=self._get_task_attr(task, "category", None),
            difficulty=self._get_task_attr(task, "difficulty", 5),
            user_importance=self._get_task_attr(task, "user_importance", 5),
            estimated_duration=self._get_task_attr(task, "estimated_duration", 1.0),
            assigned_at=self._get_task_attr(task, "created_at", datetime.utcnow()),
            started_at=datetime.utcnow(),
            deadline=self._get_task_attr(task, "deadline", None),
            was_completed=False,
            was_delayed=False,
            interruptions=0,
            reschedule_count=0,
            day_of_week=datetime.utcnow().weekday(),
            hour_started=datetime.utcnow().hour,
            created_at=datetime.utcnow()
        )

        self.session.add(log)
        self.session.commit()

        return log
    # =====================================
    # TASK INTERRUPTED
    # =====================================

    def log_interruption(self, task_id):

        log = self.session.exec(
            select(TaskExecutionLog)
            .where(TaskExecutionLog.task_id == task_id)
            .order_by(TaskExecutionLog.id.desc())
            ).first()

        if log:
            log.interruptions += 1
            self.session.commit()

    # =====================================
    # TASK RESCHEDULED
    # =====================================

    def log_reschedule(self, task_id):

        log = self.session.exec(
            select(TaskExecutionLog)
            .where(TaskExecutionLog.task_id == task_id)
            .order_by(TaskExecutionLog.id.desc())
            ).first()

        if log:
            log.reschedule_count += 1
            log.was_delayed = True
            self.session.commit()

    # =====================================
    # TASK COMPLETED
    # =====================================

    def log_task_completed(
        self,
        task,
        focus_score=5,
        stress_level=5,
        completion_quality=5
    ):

        log = self.session.exec(
            select(TaskExecutionLog)
            .where(TaskExecutionLog.task_id == task.id)
            .order_by(TaskExecutionLog.id.desc())
            ).first()
        if not log:
            return

        now = datetime.utcnow()

        log.completed_at = now
        log.was_completed = True
        # =====================================
        # UPDATE ACTUAL TASK
        # =====================================

        task.completed = True

        self.session.add(task)


        duration = (
            now - log.started_at
        ).total_seconds() / 3600

        log.actual_duration = duration

        log.focus_score = focus_score
        log.stress_level = stress_level
        log.completion_quality = completion_quality

        if task.deadline and now > task.deadline:

            log.missed_deadline = True
            log.was_delayed = True

            delay = (
                now - task.deadline
            ).total_seconds() / 3600

            log.delay_amount = delay
        self.session.add(log)

        self.session.commit()

# =====================================
# REBUILD USER STATS
# =====================================



        rebuild_user_stats(
            self.session,
            task.owner_id
        )

# =====================================
# AUTO RETRAIN
# =====================================


        # trigger_background_retrain()  # disabled to prevent file-watch reloads during UI actions