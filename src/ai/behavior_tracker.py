from collections import defaultdict
from statistics import mean

from src.db.models_ai import TaskExecutionLog
from sqlmodel import select


class BehaviorTracker:
    """
    Learns behavioral patterns from users.

    This becomes the foundation for:
    - personalization
    - burnout detection
    - focus prediction
    - procrastination tracking
    - productivity forecasting
    """

    def __init__(self, session):
        self.session = session
# =========================================================
    # MAIN PROFILE BUILDER
    # =========================================================

    def build_behavior_profile(self, user_id):

        logs = self.session.exec(
            select(TaskExecutionLog).where(TaskExecutionLog.user_id == user_id)
            ).all()
        if not logs:
            return self.default_profile()

        profile = {
            "avg_completion_time": self.average_completion_time(logs),
            "completion_rate": self.completion_rate(logs),
            "procrastination_score": self.procrastination_score(logs),
            "preferred_focus_hours": self.preferred_focus_hours(logs),
            "productive_days": self.productive_days(logs),
            "burnout_risk": self.burnout_risk(logs),
            "difficulty_tolerance": self.difficulty_tolerance(logs)
        }

        return profile
 # =========================================================
    # DEFAULT PROFILE
    # =========================================================

    def default_profile(self):

        return {
            "avg_completion_time": 1.0,
            "completion_rate": 0.5,
            "procrastination_score": 5,
            "preferred_focus_hours": [9, 10, 11],
            "productive_days": [0, 1, 2, 3, 4],
            "burnout_risk": 0,
            "difficulty_tolerance": 5
        }
# =========================================================
    # COMPLETION TIME
    # =========================================================

    def average_completion_time(self, logs):

        durations = [
            log.actual_duration
            for log in logs
            if log.actual_duration
        ]

        if not durations:
            return 1.0

        return mean(durations)
# =========================================================
    # COMPLETION RATE
    # =========================================================

    def completion_rate(self, logs):

        completed = sum(
            1 for log in logs
            if log.was_completed
        )

        return completed / len(logs)
# =========================================================
    # PROCRASTINATION SCORE
    # =========================================================

    def procrastination_score(self, logs):

        delayed = sum(
            1 for log in logs
            if log.was_delayed
        )

        ratio = delayed / len(logs)

        # Scale to 1-10
        return round(ratio * 10, 2)
    # =========================================================
    # PREFERRED WORK HOURS
    # =========================================================

    def preferred_focus_hours(self, logs):

        hour_scores = defaultdict(int)

        for log in logs:

            if not log.started_at:
                continue

            hour = log.started_at.hour

            if log.was_completed:
                hour_scores[hour] += 2

            if not log.was_delayed:
                hour_scores[hour] += 1

        ranked = sorted(
            hour_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [hour for hour, _ in ranked[:5]]
# =========================================================
    # PRODUCTIVE DAYS
    # =========================================================

    def productive_days(self, logs):

        day_scores = defaultdict(int)

        for log in logs:

            if not log.started_at:
                continue

            weekday = log.started_at.weekday()

            if log.was_completed:
                day_scores[weekday] += 1

        ranked = sorted(
            day_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )

        return [day for day, _ in ranked]
# =========================================================
    # BURNOUT RISK
    # =========================================================

    def burnout_risk(self, logs):

        recent_logs = logs[-20:]

        delayed = sum(
            1 for log in recent_logs
            if log.was_delayed
        )

        return delayed / len(recent_logs) if recent_logs else 0
# =========================================================
    # DIFFICULTY TOLERANCE
    # =========================================================

    def difficulty_tolerance(self, logs):

        difficult_tasks = [
            log for log in logs
            if getattr(log, "difficulty", 5) >= 7
        ]

        if not difficult_tasks:
            return 5

        completed = sum(
            1 for log in difficult_tasks
            if log.was_completed
        )

        return round((completed / len(difficult_tasks)) * 10, 2)
