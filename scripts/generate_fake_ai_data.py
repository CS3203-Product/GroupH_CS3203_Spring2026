import datetime
import random
from src.db.session import SessionLocal
from src.db.models_ai import TaskExecutionLog


session = SessionLocal()

categories = [
    "study",
    "programming",
    "reading",
    "meeting",
    "exercise"
]

for i in range(1000):

    difficulty = random.randint(1, 10)

    estimated_duration = random.uniform(0.5, 4)

    actual_duration = (
        estimated_duration * random.uniform(0.7, 2.5)
    )

    was_delayed = random.choice([True, False])

    started_at = (
        datetime.utcnow()
        - datetime.timedelta(days=random.randint(0, 60))
    )

    completed_at = (
        started_at
        + datetime.timedelta(hours=actual_duration)
    )

    deadline = (
        started_at
        + datetime.timedelta(hours=random.randint(1, 72))
    )

    log = TaskExecutionLog(
        user_id=1,
        task_id=i,
        category=random.choice(categories),
        difficulty=difficulty,
        user_importance=random.randint(1, 10),
        estimated_duration=estimated_duration,
        actual_duration=actual_duration,
        assigned_at=started_at,
        started_at=started_at,
        completed_at=completed_at,
        deadline=deadline,
        was_completed=True,
        was_delayed=was_delayed,
        missed_deadline=was_delayed,
        delay_amount=random.uniform(0, 5),
        completion_quality=random.uniform(1, 10),
        focus_score=random.uniform(1, 10),
        stress_level=random.uniform(1, 10),
        interruptions=random.randint(0, 10),
        reschedule_count=random.randint(0, 5),
        day_of_week=started_at.weekday(),
        hour_started=started_at.hour,
        session_type="deep_work",
        created_at=datetime.utcnow()
    )

    session.add(log)

session.commit()

print("Generated fake AI training data")