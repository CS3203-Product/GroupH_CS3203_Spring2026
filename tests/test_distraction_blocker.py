import unittest

from src.productivity.distraction_blocker import DistractionBlocker


class TestDistractionBlocker(unittest.TestCase):
    def setUp(self):
        self.blocker = DistractionBlocker()
        self.blocked = ["facebook.com"]
        self.blocker.set_blocked_sites(self.blocked)

    def test_block_valid_site_during_task_session(self):
        result = self.blocker.check_access("facebook.com", current_time="20:00")
        self.assertFalse(result, "Access to sites open after 20:00")

    def test_boundary_start_time(self):
        result = self.blocker.check_access("facebook.com", current_time="10:30")
        self.assertTrue(result, "Blocker activates at 10:30 AM")

    def test_invalid_url_format(self):
        with self.assertRaises(ValueError):
            self.blocker.check_access("", current_time="10:30")


if __name__ == "__main__":
    unittest.main()
