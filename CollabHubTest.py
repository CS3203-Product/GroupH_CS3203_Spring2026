from UnCram import Uncram

app = Uncram()

print(app.add_user("Zander"))
print(app.add_user("Alex"))

task1 = app.create_task("Zander", "Finish CS Project", 5)

print(app.collaboration_hub.send_invite("Zander", "Alex", task1))

print("Alex's invites:")
for invite in app.collaboration_hub.view_invites("Alex"):
    print(f"{invite['sender']} invited {invite['receiver']} to '{invite['task'].name}'")

print(app.collaboration_hub.accpet_invite("Alex", task1))

print("Tasks Alex can see:")
for task in app.view_tasks_for_user("Alex"):
    print(task)