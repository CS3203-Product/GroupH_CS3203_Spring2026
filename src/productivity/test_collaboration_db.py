from sqlmodel import select

from src.db.session import get_db_context
from src.models.models import Item, User
from src.productivity.collaboration_hub import CollaborationHub


def main():
    hub = CollaborationHub()

    with get_db_context() as db:
        sender = db.exec(
            select(User).where(User.email == "sender@example.com")
        ).first()

        receiver = db.exec(
            select(User).where(User.email == "receiver@example.com")
        ).first()

        if not sender:
            print("Sender user not found.")
            return

        if not receiver:
            print("Receiver user not found.")
            return

        task_row = db.exec(
            select(Item).where(
                Item.title == "Finish CS Project",
                Item.owner_id == sender.id,
            )
        ).first()

        if not task_row:
            task_row = Item(
                title="Finish CS Project",
                description="Demo collaboration task",
                owner_id=sender.id,
                category="general",
                difficulty=5,
                user_importance=5,
                estimated_duration=1.0,
            )

            db.add(task_row)
            db.commit()
            db.refresh(task_row)

        message = hub.send_invite(
            db=db,
            sender=sender,
            receiver=receiver,
            item=task_row,
        )

        print(message)


if __name__ == "__main__":
    main()