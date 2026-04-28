"""Collaboration invites and shared task access (logic only, no UI)."""

from src.productivity.collaboration_models import CollaborationTask, CollaborationInvite
from sqlmodel import Session, select
from src.db.session import get_db_context


class CollaborationHub:
    def __init__(self):
        self.invites: list[dict] = []

    def send_invite(self, db: Session, sender: str, receiver: str, task: CollaborationTask) -> str:
        if task.owner != sender:
            return "Only the owner can invite others."

        if receiver in task.shared_with:
            return f"{receiver} already has access to this task."

        task_id = 1  # temporary for testing

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

        return f"Invite sent from {sender} to {receiver} for task '{task.name}'."

    def view_invites(self, db: Session, user: str):
        statement = select(CollaborationInvite).where(
            CollaborationInvite.receiver == user,
            CollaborationInvite.status == "pending"
        )
        results = db.exec(statement).all()
        return results

    def accept_invite(self, receiver: str, task: CollaborationTask) -> str:
        for invite in self.invites:
            if (
                invite["receiver"] == receiver
                and invite["task"] == task
                and invite["status"] == "pending"
            ):
                invite["status"] = "accepted"
                if receiver not in task.shared_with:
                    task.shared_with.append(receiver)
                return f"{receiver} accepted invite for task '{task.name}'."
        return "No pending invite found."

    def decline_invite(self, receiver: str, task: CollaborationTask) -> str:
        for invite in self.invites:
            if (
                invite["receiver"] == receiver
                and invite["task"] == task
                and invite["status"] == "pending"
            ):
                invite["status"] = "declined"
                return f"{receiver} declined invite for task '{task.name}'."
        return "No pending invite found."

    def can_view_task(self, user: str, task: CollaborationTask) -> bool:
        return user == task.owner or user in task.shared_with
