from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel

from src.core.config import settings
from src.db import models_ai
from src.db.session import engine
from src.models import models
from src.repositories.user import user_repo


def _table_info(table_name: str) -> tuple[set[str], str, str, str, str] | None:
    """Return existing column names and SQL snippets for the configured database."""
    inspector = inspect(engine)
    dialect = engine.dialect.name
    schema = settings.SCHEMA_NAME-

    if dialect == "sqlite":
        if not inspector.has_table(table_name):
            return None
        col_names = {c["name"] for c in inspector.get_columns(table_name)}
        return col_names, table_name, "REAL", "INTEGER", "0"

    if not inspector.has_table(table_name, schema=schema):
        return None

    col_names = {c["name"] for c in inspector.get_columns(table_name, schema=schema)}
    return col_names, f'"{schema}"."{table_name}"', "DOUBLE PRECISION", "BOOLEAN", "false"


def _run_alters(alters: list[str]) -> None:
    if not alters:
        return
    with engine.begin() as conn:
        for stmt in alters:
            conn.execute(text(stmt))


def _ensure_item_ai_columns() -> None:
    """Add AI task columns to ``item`` if the table predates the AI merge."""
    info = _table_info("item")
    if not info:
        return

    col_names, table_sql, float_sql, bool_sql, bool_default = info
    alters: list[str] = []

    if "completed" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN completed {bool_sql} NOT NULL DEFAULT {bool_default}"
        )
    if "category" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN category VARCHAR NOT NULL DEFAULT 'general'"
        )
    if "difficulty" not in col_names:
        alters.append(f"ALTER TABLE {table_sql} ADD COLUMN difficulty INTEGER NOT NULL DEFAULT 5")
    if "user_importance" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN user_importance INTEGER NOT NULL DEFAULT 5"
        )
    if "estimated_duration" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN estimated_duration {float_sql} NOT NULL DEFAULT 1.0"
        )
    if "predicted_duration" not in col_names:
        alters.append(f"ALTER TABLE {table_sql} ADD COLUMN predicted_duration {float_sql}")
    if "predicted_priority" not in col_names:
        alters.append(f"ALTER TABLE {table_sql} ADD COLUMN predicted_priority {float_sql}")
    if "deadline" not in col_names:
        alters.append(f"ALTER TABLE {table_sql} ADD COLUMN deadline TIMESTAMP")
    if "scheduled_start" not in col_names:
        alters.append(f"ALTER TABLE {table_sql} ADD COLUMN scheduled_start TIMESTAMP")
    if "scheduled_end" not in col_names:
        alters.append(f"ALTER TABLE {table_sql} ADD COLUMN scheduled_end TIMESTAMP")
    if "created_at" not in col_names:
        default_now = "CURRENT_TIMESTAMP"
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT {default_now}"
        )

    _run_alters(alters)


def _ensure_weekly_schedule_tracker_columns() -> None:
    """Add tracker columns to ``weekly_schedule_entry`` if the table predates them."""
    info = _table_info("weekly_schedule_entry")
    if not info:
        return

    col_names, table_sql, float_sql, bool_sql, bool_default = info
    alters: list[str] = []

    if "time_spent_minutes" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN time_spent_minutes {float_sql} NOT NULL DEFAULT 0"
        )
    if "is_completed" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN is_completed {bool_sql} NOT NULL DEFAULT {bool_default}"
        )
    if "category" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN category VARCHAR NOT NULL DEFAULT 'general'"
        )
    if "sort_order" not in col_names:
        alters.append(f"ALTER TABLE {table_sql} ADD COLUMN sort_order INTEGER NOT NULL DEFAULT 0")

    _run_alters(alters)


def _ensure_user_distraction_columns() -> None:
    """Add distraction blocker schedule columns to ``user`` if missing."""
    info = _table_info("user")
    if not info:
        return

    col_names, table_sql, *_ = info
    alters: list[str] = []

    if "distraction_block_start" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN distraction_block_start VARCHAR(5) NOT NULL DEFAULT '10:30'"
        )
    if "distraction_block_end" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN distraction_block_end VARCHAR(5) NOT NULL DEFAULT '20:00'"
        )

    _run_alters(alters)


def init() -> None:
    """Initialize tables and ensure the first superuser account exists."""
    SQLModel.metadata.create_all(engine)

    _ensure_item_ai_columns()
    _ensure_weekly_schedule_tracker_columns()
    _ensure_user_distraction_columns()

    with Session(engine) as session:
        user = user_repo.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
        if not user:
            user_in = models.UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user_repo.create(db=session, obj_in=user_in)
