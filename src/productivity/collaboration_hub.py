"""Collaboration invites using existing home-screen Item tasks."""

from sqlmodel import Session, select

from src.productivity.collaboration_models import CollaborationInvite
from src.models.models import User, Item, Task


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

        task_row = db.exec(
            select(Task).where(
                Task.name == item.title,
                Task.owner == sender_email,
            )
        ).first()

        if not task_row:
            task_row = Task(
                name=item.title,
                owner=sender_email,
            )

            db.add(task_row)
            db.commit()
            db.refresh(task_row)

        existing_invite = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.sender == sender_email,
                CollaborationInvite.receiver == receiver_email,
                CollaborationInvite.task_id == task_row.id,
                CollaborationInvite.status == "pending",
            )
        ).first()

        if existing_invite:
            return f"Invite already pending for {receiver_email}."

        already_accepted = db.exec(
            select(CollaborationInvite).where(
                CollaborationInvite.receiver == receiver_email,
                CollaborationInvite.task_id == task_row.id,
                CollaborationInvite.status == "accepted",
            )
        ).first()

        if already_accepted:
            return f"{receiver_email} already has access to this task."

        invite = CollaborationInvite(
            sender=sender_email,
            receiver=receiver_email,
            task_id=task_row.id,
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

    def accept_invite(
        self,
        db: Session,
        invite_id: int,
        user_email: str,
    ) -> str:
        invite = db.get(CollaborationInvite, invite_id)

        if not invite:
            return "Invite not found."

        user_email = user_email.strip().lower()

        if invite.receiver != user_email:
            return "You do not have permission to accept this invite."

        if invite.status != "pending":
            return "Invite is not pending."

        task_row = db.get(Task, invite.task_id)

        if not task_row:
            return "Original task not found."

        receiver_user = db.exec(
            select(User).where(User.email == invite.receiver)
        ).first()

        if not receiver_user:
            return "Receiver account not found."

        existing_item = db.exec(
            select(Item).where(
                Item.title == task_row.name,
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
            title=task_row.name,
            description=None,
            owner_id=receiver_user.id,
            category="general",
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

    def decline_invite(
        self,
        db: Session,
        invite_id: int,
        user_email: str,
    ) -> str:
        invite = db.get(CollaborationInvite, invite_id)

        if not invite:
            return "Invite not found."

        user_email = user_email.strip().lower()

        if invite.receiver != user_email:
            return "You do not have permission to decline this invite."

        if invite.status != "pending":
            return "Invite is not pending."

        invite.status = "declined"

        db.add(invite)

        db.commit()
        db.refresh(invite)

        return f"{invite.receiver} declined invite from {invite.sender}."