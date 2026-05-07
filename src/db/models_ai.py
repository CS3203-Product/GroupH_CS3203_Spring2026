from datetime import datetime
from typing import Optional

from sqlmodel import SQLModel, Field
from src.core.config import settings


# =========================================================
# TASK EXECUTION LOG
# =========================================================

class TaskExecutionLog(SQLModel, table=True):

    __tablename__ = "task_execution_logs"
    __table_args__ = {"schema": settings.SCHEMA_NAME}

    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    # =====================================
    # IDENTIFIERS
    # =====================================

    user_id: int = Field(
    foreign_key=f"{settings.SCHEMA_NAME}.user.id"
    )

    task_id: int = Field(
    foreign_key=f"{settings.SCHEMA_NAME}.item.id"
    )

    # =====================================
    # TASK METADATA
    # =====================================

    category: Optional[str] = None

    difficulty: Optional[int] = None

    user_importance: Optional[int] = None

    estimated_duration: Optional[float] = None

    actual_duration: Optional[float] = None

    # =====================================
    # TIMING
    # =====================================

    assigned_at: Optional[datetime] = None

    started_at: Optional[datetime] = None

    completed_at: Optional[datetime] = None

    deadline: Optional[datetime] = None

    # =====================================
    # OUTCOMES
    # =====================================

    was_completed: bool = False

    was_delayed: bool = False

    missed_deadline: bool = False

    delay_amount: Optional[float] = None

    completion_quality: Optional[float] = None

    # =====================================
    # PRODUCTIVITY SIGNALS
    # =====================================

    focus_score: Optional[float] = None

    stress_level: Optional[float] = None

    interruptions: Optional[int] = None

    reschedule_count: Optional[int] = None

    # =====================================
    # CONTEXT
    # =====================================

    day_of_week: Optional[int] = None

    hour_started: Optional[int] = None

    session_type: Optional[str] = None

    created_at: datetime = Field(
        default_factory=datetime.utcnow
    )


# =========================================================
# USER BEHAVIOR STATS
# =========================================================

class UserBehaviorStats(SQLModel, table=True):

    __tablename__ = "user_behavior_stats"
    __table_args__ = {"schema": settings.SCHEMA_NAME}
    id: Optional[int] = Field(
        default=None,
        primary_key=True
    )

    user_id: int = Field(unique=True)

    avg_task_duration: float = 1.0

    completion_rate: float = 0.5

    avg_delay: float = 0.0

    overdue_tasks: int = 0