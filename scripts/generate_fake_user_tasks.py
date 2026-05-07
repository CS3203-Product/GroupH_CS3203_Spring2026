import random
from datetime import datetime, timedelta
from sqlmodel import Session, select

from src.db.session import engine
from src.db.models_ai import TaskExecutionLog
from src.models.models import User, ItemCreate
from src.repositories.item import item_repo

TASK_TITLES = [
    "Write report",
    "Finish research notes",
    "Review code",
    "Prepare presentation",
    "Read chapter",
    "Plan sprint",
    "Schedule meeting",
    "Clean inbox",
    "Update roadmap",
    "Practice exercises"
]

TASK_DESCRIPTIONS = [
    "High-priority task for this week.",
    "Requires focused attention.",
    "Follow up with the team.",
    "Capture the main ideas and next steps.",
    "Keep this short and precise.",
    "Update progress and timeline.",
    "Check dependencies before starting.",
    "Prepare any required resources.",
    "Review and revise after completion.",
    "Log the results and next action items."
]

CATEGORIES = [
    "study",
    "programming",
    "reading",
    "meeting",
    "exercise",
    "general"
]

SESSION_TYPES = [
    "deep_work",
    "focus",
    "break",
    "meeting",
    "planning"
]


def get_user_by_email(session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    return session.exec(statement).first()


def random_datetime_within_days(days_back: int) -> datetime:
    return datetime.utcnow() - timedelta(days=random.randint(0, days_back), hours=random.randint(0, 23), minutes=random.randint(0, 59))


def create_fake_items_for_user(session: Session, user: User, count: int = 10) -> list[int]:
    task_ids = []

    for i in range(count):
        title = random.choice(TASK_TITLES)
        description = random.choice(TASK_DESCRIPTIONS)

        obj_in = ItemCreate(title=f"{title} ({i + 1})", description=description)
        item = item_repo.create(db=session, obj_in=obj_in, owner_id=user.id)
        task_ids.append(item.id)

    session.commit()
    return task_ids


def create_fake_task_execution_logs(session: Session, user: User, task_ids: list[int], count: int = 50) -> None:
    for i in range(count):
        started_at = random_datetime_within_days(60)
        estimated_duration = round(random.uniform(0.5, 4.0), 2)
        actual_duration = round(estimated_duration * random.uniform(0.6, 2.0), 2)

        deadline_offset_hours = random.randint(1, 72)
        deadline = started_at + timedelta(hours=deadline_offset_hours)
        completed_at = started_at + timedelta(hours=actual_duration)
        was_delayed = completed_at > deadline

        assigned_at = started_at - timedelta(hours=random.randint(0, 24))

        log = TaskExecutionLog(
            user_id=user.id,
            task_id=random.choice(task_ids) if task_ids else i + 1,
            category=random.choice(CATEGORIES),
            difficulty=random.randint(1, 10),
            user_importance=random.randint(1, 10),
            estimated_duration=estimated_duration,
            actual_duration=actual_duration,
            assigned_at=assigned_at,
            started_at=started_at,
            completed_at=completed_at,
            deadline=deadline,
            was_completed=True,
            was_delayed=was_delayed,
            missed_deadline=was_delayed,
            delay_amount=round(max(0.0, (completed_at - deadline).total_seconds()) / 3600, 2),
            completion_quality=random.uniform(1, 10),
            focus_score=random.uniform(1, 10),
            stress_level=random.uniform(1, 10),
            interruptions=random.randint(0, 8),
            reschedule_count=random.randint(0, 5),
            day_of_week=started_at.weekday(),
            hour_started=started_at.hour,
            session_type=random.choice(SESSION_TYPES),
            created_at=datetime.utcnow()
        )

        session.add(log)

    session.commit()


def main(email: str, num_items: int = 10, num_logs: int = 50) -> None:
    with Session(engine) as session:
        user = get_user_by_email(session, email)
        if not user:
            raise ValueError(f"No user found with email: {email}")

        task_ids = create_fake_items_for_user(session, user, count=num_items)
        create_fake_task_execution_logs(session, user, task_ids, count=num_logs)

        print(f"Created {num_items} fake tasks and {num_logs} fake execution logs for {email}.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate fake tasks and task logs for a given user.")
    parser.add_argument("--email", required=True, help="Email of the user account")
    parser.add_argument("--items", type=int, default=10, help="Number of fake items to create")
    parser.add_argument("--logs", type=int, default=50, help="Number of fake execution logs to create")
    args = parser.parse_args()

    main(email=args.email, num_items=args.items, num_logs=args.logs)
