"""Unit tests for TaskAnalyticsDashboard."""

import unittest

from src.productivity.task_analytics_dashboard import TaskAnalyticsDashboard


class TestTaskAnalyticsDashboard(unittest.TestCase):
    def setUp(self):
        self.dashboard = TaskAnalyticsDashboard()

    def test_add_task_returns_record_and_registers_task(self):
        record = self.dashboard.add_task("t1", "First task", "work")
        self.assertEqual(record.task_id, "t1")
        self.assertEqual(record.title, "First task")
        self.assertEqual(record.category, "work")
        self.assertIs(self.dashboard.get_task("t1"), record)
        self.assertEqual(self.dashboard.total_tasks, 1)

    def test_add_task_duplicate_id_raises_key_error(self):
        self.dashboard.add_task("t1", "A")
        with self.assertRaisesRegex(KeyError, "already exists"):
            self.dashboard.add_task("t1", "B")

    def test_get_task_missing_raises_key_error(self):
        with self.assertRaisesRegex(KeyError, "not found"):
            self.dashboard.get_task("missing")

    def test_complete_task_marks_completed(self):
        self.dashboard.add_task("t1", "Todo")
        self.assertEqual(self.dashboard.completed_tasks, 0)
        self.assertEqual(self.dashboard.completion_rate, 0.0)
        returned = self.dashboard.complete_task("t1")
        self.assertTrue(returned.is_completed)
        self.assertEqual(self.dashboard.completed_tasks, 1)
        self.assertEqual(self.dashboard.completion_rate, 1.0)

    def test_complete_task_missing_raises_key_error(self):
        with self.assertRaisesRegex(KeyError, "not found"):
            self.dashboard.complete_task("nope")

    def test_log_time_adds_minutes(self):
        self.dashboard.add_task("t1", "Work")
        self.dashboard.log_time("t1", 30.5)
        self.dashboard.log_time("t1", 10.0)
        self.assertAlmostEqual(self.dashboard.get_task("t1").time_spent_minutes, 40.5)
        self.assertAlmostEqual(self.dashboard.total_time_spent, 40.5)

    def test_log_time_negative_minutes_raises_value_error(self):
        self.dashboard.add_task("t1", "Work")
        with self.assertRaisesRegex(ValueError, "non-negative"):
            self.dashboard.log_time("t1", -1.0)

    def test_log_time_missing_task_raises_key_error(self):
        with self.assertRaisesRegex(KeyError, "not found"):
            self.dashboard.log_time("missing", 5.0)

    def test_completion_rate_partial(self):
        self.dashboard.add_task("a", "A")
        self.dashboard.add_task("b", "B")
        self.dashboard.add_task("c", "C")
        self.dashboard.complete_task("a")
        self.dashboard.complete_task("b")
        self.assertEqual(self.dashboard.total_tasks, 3)
        self.assertEqual(self.dashboard.completed_tasks, 2)
        self.assertAlmostEqual(self.dashboard.completion_rate, 2.0 / 3.0)

    def test_completion_rate_empty_dashboard(self):
        self.assertEqual(self.dashboard.total_tasks, 0)
        self.assertEqual(self.dashboard.completed_tasks, 0)
        self.assertEqual(self.dashboard.completion_rate, 0.0)
        self.assertEqual(self.dashboard.total_time_spent, 0.0)

    def test_total_time_spent_across_tasks(self):
        self.dashboard.add_task("x", "X")
        self.dashboard.add_task("y", "Y")
        self.dashboard.log_time("x", 15.0)
        self.dashboard.log_time("y", 25.0)
        self.assertAlmostEqual(self.dashboard.total_time_spent, 40.0)


if __name__ == "__main__":
    unittest.main()
