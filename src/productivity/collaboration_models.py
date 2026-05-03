"""Domain models for collaboration (distinct from scheduling tasks)."""

from typing import Optional
from sqlmodel import SQLModel, Field

class CollaborationTask:
    def __init__(self, name: str, owner: str, due_day=None):
        self.name = name
        self.owner = owner
        self.due_day = due_day
        self.shared_with: list[str] = []

class CollaborationInvite(SQLModel, table=True):
    __tablename__ = "invite"

    id: Optional[int] = Field(default=None, primary_key=True)
    sender: str
    receiver: str
    task_id: int
    status: str = "pending"
