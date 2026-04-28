from src.db.session import get_db_context
from src.productivity.collaboration_hub import CollaborationHub
from src.productivity.collaboration_models import CollaborationTask

hub = CollaborationHub()

task = CollaborationTask(
    name="Finish CS Project",
    owner="Zander",
    due_day="Friday"
)

with get_db_context() as db:
    print(hub.send_invite(db, "Zander", "Alex", task))

    invites = hub.view_invites(db, "Alex")

    print("Alex's pending invites:")
    for invite in invites:
        print(invite.sender, invite.receiver, invite.task_id, invite.status)