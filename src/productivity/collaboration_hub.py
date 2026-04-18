"""Collaboration invites and shared task access (logic only, no UI)."""

from src.productivity.collaboration_models import CollaborationTask


class CollaborationHub:
    def __init__(self):
        self.invites: list[dict] = []

    def send_invite(self, sender: str, receiver: str, task: CollaborationTask) -> str:
        if task.owner != sender:
            return "Only the owner can invite others."

        if receiver in task.shared_with:
            return f"{receiver} already has access to this task."

        for invite in self.invites:
            if (
                invite["sender"] == sender
                and invite["receiver"] == receiver
                and invite["task"] == task
                and invite["status"] == "pending"
            ):
                return f"Invite already pending for {receiver}."

        invite = {
            "sender": sender,
            "receiver": receiver,
            "task": task,
            "status": "pending",
        }

        self.invites.append(invite)
        return f"Invite sent from {sender} to {receiver} for task '{task.name}'."

    def view_invites(self, user: str) -> list[dict]:
        user_invites = []
        for invite in self.invites:
            if invite["receiver"] == user and invite["status"] == "pending":
                user_invites.append(invite)
        return user_invites

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
