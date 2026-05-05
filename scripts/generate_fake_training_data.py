"""
Generate fake AI training data for UnCram.

This script creates fake Items using the same structure as the Task board
and Dashboard task creation forms, then creates matching TaskExecutionLog
records so the AI models have data to train on.

Run from the project root:

    python scripts/generate_fake_training_data.py --email admin@example.com --tasks 75

Or for your user account:

    python scripts/generate_fake_training_data.py --email your_email@example.com --tasks 75
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse
import random
from datetime import datetime, timedelta

from sqlmodel import Session, select

from src.db.session import engine
from src.models.models import User, Item, ItemCreate
from src.repositories.item import item_repo
from src.db.models_ai import TaskExecutionLog
from src.ai.user_stats_service import rebuild_user_stats
from src.ai.retrain import retrain_all_models


CATEGORIES = [
    "general",
    "study",
    "programming",
    "reading",
    "exercise",
    "meeting",
]

TASK_TEMPLATES = {
    "general": [
        "Organize workspace",
        "Update weekly checklist",
        "Review personal tasks",
        "Plan tomorrow",
    ],
    "study": [
        "Study lecture notes",
        "Complete homework problems",
        "Review exam material",
        "Summarize textbook chapter",
    ],
    "programming": [
        "Fix database bug",
        "Refactor dashboard code",
        "Implement login validation",
        "Write unit tests",
        "Debug API endpoint",
    ],
    "reading": [
        "Read assigned chapter",
        "Annotate article",
        "Review documentation",
        "Summarize research paper",
    ],
    "exercise": [
        "Complete workout",
        "Go for a run",
        "Stretch and mobility session",
        "Track fitness progress",
    ],
    "meeting": [
        "Prepare team meeting notes",
        "Attend project sync",
        "Review group tasks",
        "Plan sprint meeting",
    ],
}

DESCRIPTIONS = [
    "Generated fake task for AI model training.",
    "Synthetic task matching the Task board and Dashboard structure.",
    "Used to help train duration and priority models.",
    "Fake historical task completion record.",
]

SESSION_TYPES = [
    "deep_work",
    "focus",
    "planning",
    "meeting",
    "quick_task",
]


def get_user_by_email(session: Session, email: str) -> User:
    user = session.exec(
        select(User).where(User.email == email)
    ).first()

    if not user:
        raise ValueError(
            f"No user found with email '{email}'. "
            "Create/login with that user first, then rerun this script."
        )

    return user


def calculate_fake_actual_duration(
    estimated_duration: float,
    difficulty: int,
    importance: int,
    category: str,
    interruptions: int,
) -> float:
    """
    Create realistic actual_duration values.

    Harder tasks, programming tasks, and interrupted tasks tend to take longer.
    Easier tasks and exercise/reading tasks are closer to the estimate.
    """

    multiplier = random.uniform(0.75, 1.35)

    if difficulty >= 8:
        multiplier += random.uniform(0.25, 0.75)
    elif difficulty <= 3:
        multiplier -= random.uniform(0.05, 0.20)

    if category == "programming":
        multiplier += random.uniform(0.20, 0.80)
    elif category == "meeting":
        multiplier += random.uniform(-0.10, 0.20)
    elif category == "exercise":
        multiplier += random.uniform(-0.20, 0.10)

    if importance >= 8:
        multiplier += random.uniform(0.00, 0.20)

    multiplier += interruptions * random.uniform(0.02, 0.08)

    actual_duration = estimated_duration * multiplier

    return round(max(actual_duration, 0.25), 2)


def calculate_fake_priority_target(
    difficulty: int,
    importance: int,
    hours_until_deadline: float,
    was_delayed: bool,
    missed_deadline: bool,
) -> float:
    """
    Create a useful fake priority value.

    This is stored on Item.predicted_priority so the fake tasks look realistic
    in the dashboard/priorities page. The retrain model still learns mainly
    from TaskExecutionLog.
    """

    urgency_score = max(0, 10 - (hours_until_deadline / 12))

    priority = (
        importance * 0.45
        + difficulty * 0.20
        + urgency_score * 0.25
        + (1.0 if was_delayed else 0.0)
        + (1.0 if missed_deadline else 0.0)
    )

    return round(min(max(priority, 1.0), 10.0), 2)


def create_fake_item_and_log(
    session: Session,
    user: User,
    index: int,
    completed_ratio: float,
) -> None:
    category = random.choice(CATEGORIES)
    title_base = random.choice(TASK_TEMPLATES[category])

    difficulty = random.randint(1, 10)
    user_importance = random.randint(1, 10)
    estimated_duration = round(random.uniform(0.5, 5.0), 2)

    created_at = datetime.utcnow() - timedelta(
        days=random.randint(1, 60),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59),
    )

    deadline = created_at + timedelta(
        hours=random.randint(8, 168)
    )

    started_at = created_at + timedelta(
        hours=random.randint(0, 72)
    )

    interruptions = random.randint(0, 8)

    actual_duration = calculate_fake_actual_duration(
        estimated_duration=estimated_duration,
        difficulty=difficulty,
        importance=user_importance,
        category=category,
        interruptions=interruptions,
    )

    completed_at = started_at + timedelta(hours=actual_duration)

    was_completed = random.random() < completed_ratio
    missed_deadline = was_completed and completed_at > deadline
    was_delayed = missed_deadline or interruptions >= 5 or actual_duration > estimated_duration * 1.5

    delay_amount = 0.0
    if missed_deadline:
        delay_amount = round(
            (completed_at - deadline).total_seconds() / 3600,
            2,
        )

    hours_until_deadline = max(
        (deadline - created_at).total_seconds() / 3600,
        1,
    )

    predicted_priority = calculate_fake_priority_target(
        difficulty=difficulty,
        importance=user_importance,
        hours_until_deadline=hours_until_deadline,
        was_delayed=was_delayed,
        missed_deadline=missed_deadline,
    )

    item_in = ItemCreate(
        title=f"{title_base} #{index}",
        description=random.choice(DESCRIPTIONS),
        completed=was_completed,
        category=category,
        difficulty=difficulty,
        user_importance=user_importance,
        estimated_duration=estimated_duration,
        deadline=deadline,
    )

    item = item_repo.create(
        db=session,
        obj_in=item_in,
        owner_id=user.id,
    )

    item.created_at = created_at
    item.predicted_duration = actual_duration
    item.predicted_priority = predicted_priority

    if was_completed:
        item.completed = True

    session.add(item)
    session.commit()
    session.refresh(item)

    # Only completed tasks should become training logs.
    # The model learns from tasks that have actual outcomes.
    if was_completed:
        focus_score = round(random.uniform(4.0, 10.0), 2)

        if interruptions >= 5:
            focus_score = round(random.uniform(1.0, 5.5), 2)

        stress_level = round(random.uniform(1.0, 10.0), 2)

        if difficulty >= 8 or missed_deadline:
            stress_level = round(random.uniform(6.0, 10.0), 2)

        completion_quality = round(random.uniform(4.0, 10.0), 2)

        if stress_level >= 8 or interruptions >= 6:
            completion_quality = round(random.uniform(2.0, 7.0), 2)

        log = TaskExecutionLog(
            user_id=user.id,
            task_id=item.id,
            category=category,
            difficulty=difficulty,
            user_importance=user_importance,
            estimated_duration=estimated_duration,
            actual_duration=actual_duration,
            assigned_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            deadline=deadline,
            was_completed=True,
            was_delayed=was_delayed,
            missed_deadline=missed_deadline,
            delay_amount=delay_amount,
            completion_quality=completion_quality,
            focus_score=focus_score,
            stress_level=stress_level,
            interruptions=interruptions,
            reschedule_count=random.randint(0, 4),
            day_of_week=started_at.weekday(),
            hour_started=started_at.hour,
            session_type=random.choice(SESSION_TYPES),
            created_at=datetime.utcnow(),
        )

        session.add(log)
        session.commit()


def main(email: str, tasks: int, completed_ratio: float, train: bool) -> None:
    with Session(engine) as session:
        user = get_user_by_email(session, email)

        for index in range(1, tasks + 1):
            create_fake_item_and_log(
                session=session,
                user=user,
                index=index,
                completed_ratio=completed_ratio,
            )

        rebuild_user_stats(session, user.id)

        if train:
            retrain_all_models(session)

        print(
            f"Created {tasks} fake structured tasks for {email}. "
            f"Completed ratio: {completed_ratio}. "
            f"Training {'ran' if train else 'was skipped'}."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate fake structured UnCram task data for AI training."
    )

    parser.add_argument(
        "--email",
        required=True,
        help="Existing user email to attach fake tasks to.",
    )

    parser.add_argument(
        "--tasks",
        type=int,
        default=100,
        help="Number of fake structured tasks to create.",
    )

    parser.add_argument(
        "--completed-ratio",
        type=float,
        default=0.85,
        help="Ratio of tasks that should be marked completed and logged.",
    )

    parser.add_argument(
        "--no-train",
        action="store_true",
        help="Create fake data but do not retrain models immediately.",
    )

    args = parser.parse_args()

    main(
        email=args.email,
        tasks=args.tasks,
        completed_ratio=args.completed_ratio,
        train=not args.no_train,
    )