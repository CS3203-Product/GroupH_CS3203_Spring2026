"""Application façade used by collaboration tests and future UnCram features."""

from __future__ import annotations

from src.productivity.collaboration_hub import CollaborationHub
from src.productivity.collaboration_models import CollaborationTask


class Uncram:
    def __init__(self) -> None:
        self.users: set[str] = set()
        self.tasks: list[CollaborationTask] = []
        self.collaboration_hub = CollaborationHub()

    def add_user(self, name: str) -> str:
        self.users.add(name)
        return f"User '{name}' added."

    def create_task(self, owner: str, name: str, due_day) -> CollaborationTask:
        task = CollaborationTask(name=name, owner=owner, due_day=due_day)
        self.tasks.append(task)
        return task

    def view_tasks_for_user(self, user: str) -> list[CollaborationTask]:
        return [
            t
            for t in self.tasks
            if t.owner == user or user in t.shared_with
        ]
