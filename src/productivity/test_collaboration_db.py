from src.db.session import get_db_context
from src.productivity.collaboration_hub import CollaborationHub
from src.productivity.collaboration_models import CollaborationTask
from src.models.models import Task
from sqlmodel import select

hub = CollaborationHub()

task = CollaborationTask(
    name="Finish CS Project",
    owner="Zander",
    due_day="Friday"
)

with get_db_context() as db:

    task_row = db.exec(
        select(Task).where(Task.name == "Finish CS Project")
    ).first()

    if not task_row:
        task_row = Task(
            name="Finish CS Project",
            owner="Zander"
        )
        db.add(task_row)
        db.commit()
        db.refresh(task_row)

    # send invite
    print(hub.send_invite(db, "Zander", "Alex", task))

    invites = hub.view_invites(db, "Alex")

    print("Alex's pending invites:")
    for invite in invites:
        print(invite.sender, invite.receiver, invite.task_id, invite.status)

    # test accept invite
    if invites:
        first_invite = invites[0]
        print(hub.accept_invite(db, first_invite.id))

        
    invites = hub.view_invites(db, "Alex")

    #test decline invite
    if invites:
        first_invite = invites[0]
        print(hub.decline_invite(db, first_invite.id))

        print("Can Alex view task?")

    #test view permissions
    print(hub.can_view_task(db, "Alex", task_row))

    print("Can Bob view task?")
    print(hub.can_view_task(db, "Bob", task_row))