"""Collaboration invites and shared task access (logic only, no UI)."""

from src.productivity.collaboration_models import CollaborationTask, CollaborationInvite
from sqlmodel import Session, select
from src.db.session import get_db_context
from src.models.models import Task


class CollaborationHub:
    def __init__(self):
        self.invites: list[dict] = []

    def send_invite(self, db: Session, sender: str, receiver: str, task: CollaborationTask) -> str:
        if task.owner != sender:
            return "Only the owner can invite others."

        if receiver in task.shared_with:
            return f"{receiver} already has access to this task."

        task_row = db.exec(
            select(Task).where(Task.name == task.name)
        ).first()

        if not task_row:
            return "Task not found."

        task_id = task_row.id

        existing_invite = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.sender == sender,
                CollaborationInvite.receiver == receiver,
                CollaborationInvite.task_id == task_id,
                CollaborationInvite.status == "pending",
            )
        ).first()

        if existing_invite:
            return f"Invite already pending for {receiver}."

        invite = CollaborationInvite(
            sender=sender,
            receiver=receiver,
            task_id=task_id,
            status="pending",
        )

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return f"Invite sent from {sender} to {receiver} for task '{task.name}'."

    def view_invites(self, db: Session, user: str):
        statement = select(CollaborationInvite).where(
            CollaborationInvite.receiver == user,
            CollaborationInvite.status == "pending"
        )
        results = db.exec(statement).all()
        return results

    def accept_invite(self, db: Session, invite_id: int) -> str:
        invite = db.get(CollaborationInvite, invite_id)

        if not invite:
            return "Invite not found."

        if invite.status != "pending":
            return "Invite is not pending."

        invite.status = "accepted"

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return f"{invite.receiver} accepted invite from {invite.sender}."

    def decline_invite(self, db: Session, invite_id: int) -> str:
        invite = db.get(CollaborationInvite, invite_id)

        if not invite:
            return "Invite not found."

        if invite.status != "pending":
            return "Invite is not pending."

        invite.status = "declined"

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return f"{invite.receiver} declined invite from {invite.sender}."

    def can_view_task(self, db: Session, user: str, task: Task) -> bool:
        if user == task.owner:
            return True

        accepted_invite = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.receiver == user,
                CollaborationInvite.task_id == task.id,
                CollaborationInvite.status == "accepted",
            )
        ).first()

        return accepted_invite is not None
