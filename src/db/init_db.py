from sqlalchemy import inspect, text
from sqlmodel import Session, SQLModel

from src.core.config import settings
from src.repositories.user import user_repo
from src.models import models
from src.db.session import engine


def _ensure_item_tracker_columns() -> None:
    """Add dashboard tracker columns to ``item`` if the table predates them."""
    inspector = inspect(engine)
    dialect = engine.dialect.name
    schema = settings.SCHEMA_NAME

    if dialect == "sqlite":
        if not inspector.has_table("item"):
            return
        col_names = {c["name"] for c in inspector.get_columns("item")}
        table_sql = "item"
        float_sql = "REAL"
        bool_sql = "INTEGER"
        bool_default = "0"
    else:
        if not inspector.has_table("item", schema=schema):
            return
        col_names = {c["name"] for c in inspector.get_columns("item", schema=schema)}
        table_sql = f'"{schema}"."item"'
        float_sql = "DOUBLE PRECISION"
        bool_sql = "BOOLEAN"
        bool_default = "false"

    alters: list[str] = []
    if "category" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN category VARCHAR NOT NULL DEFAULT 'general'"
        )
    if "time_spent_minutes" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN time_spent_minutes {float_sql} NOT NULL DEFAULT 0"
        )
    if "is_completed" not in col_names:
        alters.append(
            f"ALTER TABLE {table_sql} ADD COLUMN is_completed {bool_sql} NOT NULL DEFAULT {bool_default}"
        )
    if not alters:
        return
    with engine.begin() as conn:
        for stmt in alters:
            conn.execute(text(stmt))


def init() -> None:
    """Initializes the database, creating all necessary tables
    and ensuring the first superuser account is created."""
    SQLModel.metadata.create_all(engine)
    _ensure_item_tracker_columns()

    with Session(engine) as session:
        user = user_repo.get_by_email(db=session, email=settings.FIRST_SUPERUSER)
        if not user:
            user_in = models.UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            user_repo.create(db=session, obj_in=user_in)
