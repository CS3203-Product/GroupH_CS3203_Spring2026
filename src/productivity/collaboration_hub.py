"""Collaboration invites using existing home-screen Item tasks."""

from sqlmodel import Session, select

from src.productivity.collaboration_models import CollaborationInvite
from src.models.models import User, Item


class CollaborationHub:
    def send_invite(
        self,
        db: Session,
        sender_email: str,
        receiver_email: str,
        item_id: int,
    ) -> str:
        sender_email = sender_email.strip().lower()
        receiver_email = receiver_email.strip().lower()

        if sender_email == receiver_email:
            return "You cannot invite yourself."

        sender_user = db.exec(
            select(User).where(User.email == sender_email)
        ).first()

        if not sender_user:
            return "Sender account not found."

        receiver_user = db.exec(
            select(User).where(User.email == receiver_email)
        ).first()

        if not receiver_user:
            return f"No account found with email {receiver_email}."

        item = db.get(Item, item_id)

        if not item:
            return "Task not found."

        if item.owner_id != sender_user.id:
            return "Only the owner can invite others to this task."

        existing_invite = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.sender == sender_email,
                CollaborationInvite.receiver == receiver_email,
                CollaborationInvite.task_id == item.id,
                CollaborationInvite.status == "pending",
            )
        ).first()

        if existing_invite:
            return f"Invite already pending for {receiver_email}."

        already_accepted = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.receiver == receiver_email,
                CollaborationInvite.task_id == item.id,
                CollaborationInvite.status == "accepted",
            )
        ).first()

        if already_accepted:
            return f"{receiver_email} already has access to this task."

        invite = CollaborationInvite(
            sender=sender_email,
            receiver=receiver_email,
            task_id=item.id,
            status="pending",
        )

        db.add(invite)
        db.commit()
        db.refresh(invite)

        return f"Invite sent to {receiver_email} for task '{item.title}'."

    def view_invites(self, db: Session, user_email: str):
        user_email = user_email.strip().lower()

        return db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.receiver == user_email,
                CollaborationInvite.status == "pending",
            )
        ).all()

    def accept_invite(self, db: Session, invite_id: int) -> str:
        invite = db.get(CollaborationInvite, invite_id)

        if not invite:
            return "Invite not found."

        if invite.status != "pending":
            return "Invite is not pending."

        original_item = db.get(Item, invite.task_id)

        if not original_item:
            return "Original task not found."

        receiver_user = db.exec(
            select(User).where(User.email == invite.receiver)
        ).first()

        if not receiver_user:
            return "Receiver account not found."

        existing_item = db.exec(
            select(Item).where(
                Item.title == original_item.title,
                Item.owner_id == receiver_user.id,
            )
        ).first()

        if existing_item:
            invite.status = "accepted"
            db.add(invite)
            db.commit()
            db.refresh(invite)
            return f"{invite.receiver} already has this task."

        new_item = Item(
            title=original_item.title,
            description=original_item.description,
            owner_id=receiver_user.id,
            category=original_item.category,
            time_spent_minutes=0,
            is_completed=False,
        )

        db.add(new_item)

        invite.status = "accepted"
        db.add(invite)

        db.commit()
        db.refresh(invite)
        db.refresh(new_item)

        return f"{invite.receiver} accepted the invite. Task added to their home screen."

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