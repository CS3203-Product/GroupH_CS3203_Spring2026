import unittest

from src.productivity.uncram import Uncram


class TestCollaborationHub(unittest.TestCase):
    def setUp(self):
        self.app = Uncram()
        self.app.add_user("Zander")
        self.app.add_user("Luke")
        self.task = self.app.create_task("Zander", "Finish CS Project", 5)

    def test_add_user(self):
        result = self.app.add_user("Brittney")
        self.assertEqual(result, "User 'Brittney' added.")

    def test_create_task(self):
        self.assertEqual(self.task.name, "Finish CS Project")
        self.assertEqual(self.task.due_day, 5)
        self.assertEqual(self.task.owner, "Zander")

    def test_send_invite(self):
        result = self.app.collaboration_hub.send_invite("Zander", "Alex", self.task)
        self.assertEqual(
            result,
            "Invite sent from Zander to Alex for task 'Finish CS Project'.",
        )
        self.assertEqual(len(self.app.collaboration_hub.invites), 1)

    def test_view_invites(self):
        self.app.collaboration_hub.send_invite("Zander", "Cindy", self.task)
        invites = self.app.collaboration_hub.view_invites("Cindy")
        self.assertEqual(len(invites), 1)
        self.assertEqual(invites[0]["sender"], "Zander")
        self.assertEqual(invites[0]["receiver"], "Cindy")

    def test_accept_invite(self):
        self.app.collaboration_hub.send_invite("Zander", "Ryan", self.task)
        result = self.app.collaboration_hub.accept_invite("Ryan", self.task)
        self.assertEqual(result, "Ryan accepted invite for task 'Finish CS Project'.")
        self.assertIn("Ryan", self.task.shared_with)

    def test_view_tasks_for_shared_user(self):
        self.app.collaboration_hub.send_invite("Zander", "Alex", self.task)
        self.app.collaboration_hub.accept_invite("Alex", self.task)

        tasks = self.app.view_tasks_for_user("Alex")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "Finish CS Project")

    def test_duplicate_invite(self):
        self.app.collaboration_hub.send_invite("Zander", "Luke", self.task)
        result = self.app.collaboration_hub.send_invite("Zander", "Luke", self.task)
        self.assertEqual(result, "Invite already pending for Luke.")

    def test_decline_invite(self):
        self.app.collaboration_hub.send_invite("Zander", "Josh", self.task)
        result = self.app.collaboration_hub.decline_invite("Josh", self.task)
        self.assertEqual(
            result, "Josh declined invite for task 'Finish CS Project'."
        )

    def test_non_owner_cannot_invite(self):
        result = self.app.collaboration_hub.send_invite("Cindy", "Zander", self.task)
        self.assertEqual(result, "Only the owner can invite others.")


if __name__ == "__main__":
    unittest.main()
