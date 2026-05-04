from sqlmodel import select

from src.db.models_ai import TaskExecutionLog, UserBehaviorStats


def get_user_stats(session, user_id):
    """Get user stats or create default if not exists."""
    stats = session.exec(
        select(UserBehaviorStats).where(UserBehaviorStats.user_id == user_id)
    ).first()

    if not stats:
        return rebuild_user_stats(session, user_id)

    return stats


def rebuild_user_stats(session, user_id):
    logs = session.exec(
        select(TaskExecutionLog).where(TaskExecutionLog.user_id == user_id)
    ).all()

    if not logs:
        default_stats = UserBehaviorStats(
            user_id=user_id,
            avg_task_duration=1.0,
            completion_rate=0.5,
            avg_delay=0.0,
            overdue_tasks=0,
        )

        session.add(default_stats)
        session.commit()
        session.refresh(default_stats)

        return default_stats

    total_tasks = len(logs)

    completed_tasks = sum(1 for log in logs if log.was_completed)

    delays = [
        log.delay_amount
        for log in logs
        if log.was_delayed and log.delay_amount is not None
    ]

    durations = [
        log.actual_duration
        for log in logs
        if log.actual_duration is not None
    ]

    avg_duration = sum(durations) / len(durations) if durations else 1.0
    completion_rate = completed_tasks / total_tasks
    avg_delay = sum(delays) / len(delays) if delays else 0.0
    overdue_tasks = len(delays)

    stats = session.exec(
        select(UserBehaviorStats).where(UserBehaviorStats.user_id == user_id)
    ).first()

    if not stats:
        stats = UserBehaviorStats(user_id=user_id)
        session.add(stats)

    stats.avg_task_duration = avg_duration
    stats.completion_rate = completion_rate
    stats.avg_delay = avg_delay
    stats.overdue_tasks = overdue_tasks

    session.add(stats)
    session.commit()
    session.refresh(stats)

    return stats