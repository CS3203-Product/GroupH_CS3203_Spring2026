# src/db/models_ai.py

from sqlalchemy import (
    Column,
    Integer,
    Float,
    Boolean,
    DateTime,
    String
)


from src.db.base import Base

class TaskExecutionLog(Base):
    __tablename__ = "task_execution_logs"

    id = Column(Integer, primary_key=True)

    # =====================================
    # IDENTIFIERS
    # =====================================

    user_id = Column(Integer, nullable=False)
    task_id = Column(Integer, nullable=False)

    # =====================================
    # TASK METADATA
    # =====================================

    category = Column(String)
    difficulty = Column(Integer)
    user_importance = Column(Integer)

    estimated_duration = Column(Float)
    actual_duration = Column(Float)

    # =====================================
    # TIMING
    # =====================================

    assigned_at = Column(DateTime)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    deadline = Column(DateTime)

    # =====================================
    # OUTCOMES
    # =====================================
    was_completed = Column(Boolean)
    was_delayed = Column(Boolean)
    missed_deadline = Column(Boolean)

    delay_amount = Column(Float)

    completion_quality = Column(Float)

    # =====================================
    # PRODUCTIVITY SIGNALS
    # =====================================
    
    focus_score = Column(Float)
    stress_level = Column(Float)

    interruptions = Column(Integer)
    reschedule_count = Column(Integer)

    # =====================================
    # CONTEXT
    # =====================================

    day_of_week = Column(Integer)
    hour_started = Column(Integer)

    session_type = Column(String)

    created_at = Column(DateTime)

class UserBehaviorStats(Base):
    __tablename__ = "user_behavior_stats"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=False, unique=True)

    avg_task_duration = Column(Float, default=1.0)

    completion_rate = Column(Float, default=0.5)

    avg_delay = Column(Float, default=0.0)

    overdue_tasks = Column(Integer, default=0)
