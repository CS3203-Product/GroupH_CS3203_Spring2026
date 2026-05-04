"""Collaboration invites and shared task access logic.

This version uses the real SQLModel task table: Item.
The old Task model used fields like name and owner.
The current Item model uses title and owner_id.
"""

from sqlmodel import Session, select

from src.models.models import Item, User
from src.productivity.collaboration_models import CollaborationInvite


class CollaborationHub:
    def __init__(self):
        self.invites: list[dict] = []

    # =========================================================
    # SEND INVITE
    # =========================================================

    def send_invite(
        self,
        db: Session,
        sender: User,
        receiver: User,
        item: Item,
    ) -> str:
        """
        Send a collaboration invite for an Item.

        sender:
            The currently logged-in user sending the invite.

        receiver:
            The user receiving the invite.

        item:
            The task/item being shared.
        """

        if item.owner_id != sender.id:
            return "Only the owner can invite others."

        if sender.id == receiver.id:
            return "You cannot invite yourself."

        existing_invite = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.sender == sender.email,
                CollaborationInvite.receiver == receiver.email,
                CollaborationInvite.task_id == item.id,
                CollaborationInvite.status == "pending",
            )
        ).first()

        if existing_invite:
            return f"Invite already pending for {receiver.email}."

        already_accepted = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.receiver == receiver.email,
                CollaborationInvite.task_id == item.id,
                CollaborationInvite.status == "accepted",
            )
        ).first()

        if already_accepted:
            return f"{receiver.email} already has access to this task."

        invite = CollaborationInvite(
            sender=sender.email,
            receiver=receiver.email,
            task_id=item.id,
            status="pending",
        )

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return (
            f"Invite sent from {sender.email} to {receiver.email} "
            f"for task '{item.title}'."
        )

    # =========================================================
    # SEND INVITE BY TASK TITLE
    # =========================================================

    def send_invite_by_title(
        self,
        db: Session,
        sender: User,
        receiver: User,
        task_title: str,
    ) -> str:
        """
        Convenience method for sending an invite by task title.

        This is useful for UI code where the user types/selects a task title.
        """

        item = db.exec(
            select(Item).where(
                Item.title == task_title,
                Item.owner_id == sender.id,
            )
        ).first()

        if not item:
            return "Task not found or you do not own this task."

        return self.send_invite(
            db=db,
            sender=sender,
            receiver=receiver,
            item=item,
        )

    # =========================================================
    # VIEW INVITES
    # =========================================================

    def view_invites(self, db: Session, user: User):
        """
        Return all pending invites for the given user.
        """

        statement = select(CollaborationInvite).where(
            CollaborationInvite.receiver == user.email,
            CollaborationInvite.status == "pending",
        )

        return db.exec(statement).all()

    # =========================================================
    # ACCEPT INVITE
    # =========================================================

    def accept_invite(self, db: Session, invite_id: int, user: User) -> str:
        """
        Accept a pending invite.

        The user must be the receiver of the invite.
        """

        invite = db.get(CollaborationInvite, invite_id)

        if not invite:
            return "Invite not found."

        if invite.receiver != user.email:
            return "You cannot accept an invite that was not sent to you."

        if invite.status != "pending":
            return "Invite is not pending."

        invite.status = "accepted"

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return f"{invite.receiver} accepted invite from {invite.sender}."

    # =========================================================
    # DECLINE INVITE
    # =========================================================

    def decline_invite(self, db: Session, invite_id: int, user: User) -> str:
        """
        Decline a pending invite.

        The user must be the receiver of the invite.
        """

        invite = db.get(CollaborationInvite, invite_id)

        if not invite:
            return "Invite not found."

        if invite.receiver != user.email:
            return "You cannot decline an invite that was not sent to you."

        if invite.status != "pending":
            return "Invite is not pending."

        invite.status = "declined"

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return f"{invite.receiver} declined invite from {invite.sender}."

    # =========================================================
    # CAN VIEW TASK
    # =========================================================

    def can_view_task(self, db: Session, user: User, item: Item) -> bool:
        """
        A user can view an Item if:
        1. They own it.
        2. They have an accepted collaboration invite.
        """

        if item.owner_id == user.id:
            return True

        accepted_invite = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.receiver == user.email,
                CollaborationInvite.task_id == item.id,
                CollaborationInvite.status == "accepted",
            )
        ).first()

        return accepted_invite is not None

    # =========================================================
    # GET SHARED TASKS
    # =========================================================

    def get_shared_tasks(self, db: Session, user: User) -> list[Item]:
        """
        Return all Items shared with the given user through accepted invites.
        """

        accepted_invites = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.receiver == user.email,
                CollaborationInvite.status == "accepted",
            )
        ).all()

        task_ids = [invite.task_id for invite in accepted_invites]

        if not task_ids:
            return []

        shared_items = db.exec(
            select(Item).where(Item.id.in_(task_ids))
        ).all()

        return shared_items

    # =========================================================
    # GET OWNED AND SHARED TASKS
    # =========================================================

    def get_accessible_tasks(self, db: Session, user: User) -> list[Item]:
        """
        Return tasks the user owns plus tasks shared with them.
        """

        owned_items = db.exec(
            select(Item).where(Item.owner_id == user.id)
        ).all()

        shared_items = self.get_shared_tasks(db, user)

        combined: dict[int, Item] = {}

        for item in owned_items:
            combined[item.id] = item

        for item in shared_items:
            combined[item.id] = item

        return list(combined.values())