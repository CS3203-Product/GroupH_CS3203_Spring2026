from sqlalchemy import func

from db.models_ai import TaskExecutionLog, UserBehaviorStats


# =========================================================
# REBUILD USER STATS
# =========================================================

def rebuild_user_stats(session, user_id):

    logs = (
        session.query(TaskExecutionLog)
        .filter_by(user_id=user_id)
        .all()
    )

    if not logs:

        default_stats = UserBehaviorStats(
            user_id=user_id,
            avg_task_duration=1.0,
            completion_rate=0.5,
            avg_delay=0.0,
            overdue_tasks=0
        )

        session.add(default_stats)
        session.commit()

        return default_stats

    total_tasks = len(logs)

    completed_tasks = sum(
        1 for l in logs if l.was_completed
    )

    delayed_tasks = [
        l.delay_amount for l in logs
        if l.was_delayed
    ]

    durations = [
        l.actual_duration for l in logs
        if l.actual_duration
    ]

    avg_duration = (
        sum(durations) / len(durations)
        if durations else 1.0
    )

    completion_rate = completed_tasks / total_tasks

    avg_delay = (
        sum(delayed_tasks) / len(delayed_tasks)
        if delayed_tasks else 0.0
    )

    overdue_tasks = len(delayed_tasks)

    stats = UserBehaviorStats(
        user_id=user_id,
        avg_task_duration=avg_duration,
        completion_rate=completion_rate,
        avg_delay=avg_delay,
        overdue_tasks=overdue_tasks
    )

    session.merge(stats)
    session.commit()

    return stats