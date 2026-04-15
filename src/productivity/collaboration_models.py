"""Domain models for collaboration (distinct from scheduling tasks)."""


class CollaborationTask:
    def __init__(self, name: str, owner: str, due_day=None):
        self.name = name
        self.owner = owner
        self.due_day = due_day
        self.shared_with: list[str] = []
