# src/ai/orchestrator.py

from datetime import datetime, timedelta
from typing import List, Dict, Any

from src.ai.inference import (
    predict_duration,
    predict_priority
)

from src.ai.user_stats_service import get_user_stats



class AIOrchestrator:
    """
    Central AI management system for UnCram.

    Responsibilities:
    ---------------------------------
    - Task duration prediction
    - Task priority prediction
    - Smart scheduling
    - Schedule repair
    - Focus estimation
    - Delay prediction
    - Reinforcement-learning scheduling
    - Behavioral adaptation
    """

    # ---------------------------------
    # INIT
    # ---------------------------------
    def __init__(
        self,
        session,
        use_rl=False,
        max_hours_per_day=8
    ):

        self.session = session

        self.use_rl = use_rl
        self.max_hours_per_day = max_hours_per_day

        self.rl_agent = None

    # =========================================================
    # DURATION PREDICTION
    # =========================================================
    def estimate_duration(self, task):

        stats = get_user_stats(
            self.session,
            task.user_id
        )

        try:

            duration = predict_duration(
                task,
                stats
            )

            return max(duration, 0.25)

        except Exception as e:

            print(
                "[AI] Duration prediction failed:",
                e
            )

            return task.estimated_duration or 1.0

    # =========================================================
    # PRIORITY PREDICTION
    # =========================================================
    def estimate_priority(self, task, duration):

        stats = get_user_stats(
            self.session,
            task.user_id
        )

        try:

            priority = predict_priority(
                task,
                stats,
                duration
            )

            return max(priority, 0.1)

        except Exception as e:

            print(
                "[AI] Priority prediction failed:",
                e
            )

            return task.user_importance or 1.0

    # =========================================================
    # PRODUCTIVITY SCORE
    # =========================================================
    def estimate_focus_score(self, user_stats):

        """
        Predicts how focused/productive
        the user likely is currently.
        """

        now = datetime.utcnow()

        hour = now.hour

        base = user_stats.completion_rate * 10

        # Productivity time windows
        if 8 <= hour <= 11:
            base += 3

        elif 13 <= hour <= 16:
            base += 2

        elif 1 <= hour <= 5:
            base -= 4

        # Penalize delays
        base -= user_stats.avg_delay * 0.1

        return max(base, 1)

    # =========================================================
    # DELAY RISK
    # =========================================================
    def estimate_delay_risk(
        self,
        task,
        duration,
        user_stats
    ):

        """
        Returns:
        0.0 -> low risk
        1.0 -> high risk
        """

        now = datetime.utcnow()

        hours_left = (
            task.deadline - now
        ).total_seconds() / 3600

        if hours_left <= 0:
            return 1.0

        workload_ratio = duration / hours_left

        delay_risk = (
            workload_ratio * 0.5 +
            (user_stats.avg_delay / 10) * 0.3 +
            (1 - user_stats.completion_rate) * 0.2
        )

        return min(delay_risk, 1.0)

    # =========================================================
    # TASK SCORING
    # =========================================================
    def calculate_task_score(
        self,
        task,
        duration,
        priority,
        delay_risk,
        focus_score
    ):

        now = datetime.utcnow()

        time_left = (
            task.deadline - now
        ).total_seconds() / 3600

        urgency = 1 / max(time_left, 1)

        duration_penalty = 1 / (duration + 1)

        score = (
            priority * 0.40 +
            urgency * 0.25 +
            focus_score * 0.15 +
            duration_penalty * 0.10 -
            delay_risk * 0.10
        )

        return score

    # =========================================================
    # MAIN SMART SCHEDULER
    # =========================================================
    def schedule_tasks(
        self,
        tasks
    ):

        """
        Main scheduling pipeline.
        """

        now = datetime.utcnow()

        current_time = now

        hours_today = 0

        enriched_tasks = []

        # ---------------------------------
        # Analyze tasks
        # ---------------------------------
        for task in tasks:

            stats = get_user_stats(
                self.session,
                task.user_id
            )

            duration = self.estimate_duration(task)

            priority = self.estimate_priority(
                task,
                duration
            )

            delay_risk = self.estimate_delay_risk(
                task,
                duration,
                stats
            )

            focus_score = self.estimate_focus_score(
                stats
            )

            score = self.calculate_task_score(
                task,
                duration,
                priority,
                delay_risk,
                focus_score
            )

            task.predicted_duration = duration
            task.predicted_priority = priority

            enriched_tasks.append({
                "task": task,
                "duration": duration,
                "priority": priority,
                "delay_risk": delay_risk,
                "focus_score": focus_score,
                "score": score
            })

        # ---------------------------------
        # RL Scheduling
        # ---------------------------------
        if self.use_rl and self.rl_agent:

            enriched_tasks = self.rl_optimize_schedule(
                enriched_tasks
            )

        else:

            enriched_tasks.sort(
                key=lambda x: x["score"],
                reverse=True
            )

        # ---------------------------------
        # Time-block assignment
        # ---------------------------------
        scheduled = []

        for item in enriched_tasks:

            task = item["task"]

            duration = item["duration"]

            # Daily overflow handling
            if (
                hours_today + duration >
                self.max_hours_per_day
            ):

                current_time = (
                    current_time +
                    timedelta(days=1)
                ).replace(
                    hour=9,
                    minute=0,
                    second=0
                )

                hours_today = 0

            start = current_time

            end = (
                start +
                timedelta(hours=duration)
            )

            task.scheduled_start = start
            task.scheduled_end = end

            scheduled.append(task)

            current_time = end

            hours_today += duration

        return scheduled

    # =========================================================
    # RL OPTIMIZATION
    # =========================================================
    def rl_optimize_schedule(
        self,
        enriched_tasks
    ):

        """
        Placeholder RL optimization layer.
        """

        try:

            enriched_tasks.sort(
                key=lambda x: (
                    x["score"] -
                    x["delay_risk"]
                ),
                reverse=True
            )

            return enriched_tasks

        except Exception as e:

            print(
                "[AI] RL optimization failed:",
                e
            )

            return enriched_tasks

    # =========================================================
    # SCHEDULE REPAIR
    # =========================================================
    def repair_schedule(
        self,
        incomplete_tasks,
        future_tasks
    ):

        """
        Dynamically rebuilds schedule
        after missed tasks.
        """

        merged = (
            incomplete_tasks +
            future_tasks
        )

        return self.schedule_tasks(merged)

    # =========================================================
    # ANALYTICS SUMMARY
    # =========================================================
    def generate_analytics(
        self,
        tasks
    ) -> Dict[str, Any]:

        total_tasks = len(tasks)

        completed = len([
            t for t in tasks
            if getattr(t, "completed", False)
        ])

        overdue = len([
            t for t in tasks
            if (
                hasattr(t, "deadline") and
                t.deadline < datetime.utcnow()
            )
        ])

        completion_rate = (
            completed / total_tasks
            if total_tasks > 0 else 0
        )

        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed,
            "overdue_tasks": overdue,
            "completion_rate": completion_rate
        }

    # =========================================================
    # AUTO LOGGING
    # =========================================================
    def log_task_completion(
        self,
        task,
        actual_duration
    ):

        """
        Hook for automatic dataset collection.
        """

        print(
            f"[AI] Logged completion for task "
            f"{task.id}"
        )

        # Extend later:
        # - save TaskExecutionLog
        # - save TaskFeatureSnapshot
        # - update user stats
