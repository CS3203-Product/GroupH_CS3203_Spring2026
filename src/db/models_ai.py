# src/db/models_ai.py

from sqlalchemy import (
    Column,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    String
)

from sqlalchemy.orm import relationship

from sqlalchemy.orm import declarative_base
Base = declarative_base()

class TaskExecutionLog(Base):
    __tablename__ = "task_execution_logs"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=False)

    task_id = Column(Integer, nullable=False)

    category = Column(String, default="general")

    start_time = Column(DateTime)

    end_time = Column(DateTime)

    estimated_duration = Column(Float)

    actual_duration = Column(Float)

    was_completed = Column(Boolean, default=False)

    was_delayed = Column(Boolean, default=False)

    delay_amount = Column(Float, default=0.0)

    created_at = Column(DateTime)

class UserBehaviorStats(Base):
    __tablename__ = "user_behavior_stats"

    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, nullable=False, unique=True)

    avg_task_duration = Column(Float, default=1.0)

    completion_rate = Column(Float, default=0.5)

    avg_delay = Column(Float, default=0.0)

    overdue_tasks = Column(Integer, default=0)
