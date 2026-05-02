from datetime import datetime

from src.db.models_ai import TaskExecutionLog


class TaskLogger:

    def __init__(self, session):
        self.session = session

    # =====================================
    # TASK STARTED
    # =====================================

    def log_task_started(self, task):

        log = TaskExecutionLog(
            user_id=task.user_id,
            task_id=task.id,
            category=task.category,
            difficulty=task.difficulty,
            user_importance=task.user_importance,
            estimated_duration=task.estimated_duration,
            assigned_at=task.created_at,
            started_at=datetime.utcnow(),
            deadline=task.deadline,
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

        log = (
            self.session.query(TaskExecutionLog)
            .filter_by(task_id=task_id)
            .order_by(TaskExecutionLog.id.desc())
            .first()
        )

        if log:
            log.interruptions += 1
            self.session.commit()

    # =====================================
    # TASK RESCHEDULED
    # =====================================

    def log_reschedule(self, task_id):

        log = (
            self.session.query(TaskExecutionLog)
            .filter_by(task_id=task_id)
            .order_by(TaskExecutionLog.id.desc())
            .first()
        )

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

        log = (
            self.session.query(TaskExecutionLog)
            .filter_by(task_id=task.id)
            .order_by(TaskExecutionLog.id.desc())
            .first()
        )

        if not log:
            return

        now = datetime.utcnow()

        log.completed_at = now
        log.was_completed = True

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
        self.session.commit()