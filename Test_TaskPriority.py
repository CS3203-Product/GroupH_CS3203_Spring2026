# test_uncram.py

import pytest
from UnCram import TaskPrioritizationEngine


class TestTaskPrioritizationEngine:

    def setup_method(self):
        """Runs before each test"""
        self.engine = TaskPrioritizationEngine()

    def test_create_task_success(self):
        task = self.engine.create_task("Study")

        assert task is not None
        assert task.name == "Study"
        assert task.due_day == "Monday"
        assert len(self.engine.tasks) == 1

    def test_create_task_empty(self):
        task = self.engine.create_task("   ")

        assert task is None
        assert len(self.engine.tasks) == 0

    def test_update_selection(self):
        self.engine.update_selection("Day 1")

        assert self.engine.selected_day == "Day 1"

    def test_multiple_tasks(self):
        self.engine.create_task("Task 1")
        self.engine.create_task("Task 2")

        assert len(self.engine.tasks) == 2
        assert self.engine.tasks[0].name == "Task 1"
        assert self.engine.tasks[1].name == "Task 2"

    def test_task_due_day_after_change(self):
        self.engine.update_selection("Day 2")
        task = self.engine.create_task("Homework")

        assert task.due_day == "Day 2"

    def test_whitespace_trim(self):
        task = self.engine.create_task("   Clean room   ")

        assert task.name == "Clean room"

    def test_no_task_added_on_empty_after_valid(self):
        self.engine.create_task("Valid Task")
        self.engine.create_task("")

        assert len(self.engine.tasks) == 1