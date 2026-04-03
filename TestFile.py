# test_scheduler_logic.py

from scheduler_logic import SchedulerLogic, Task

def test_add_single_task():
    scheduler = SchedulerLogic()
    task = Task("Study", "mon", importance=5)

    scheduler.add_task(task)

    assert scheduler.rows[5]["mon"] == "Study"


def test_add_multiple_tasks_same_slot():
    scheduler = SchedulerLogic()

    scheduler.add_task(Task("Math", "tues", 10))
    scheduler.add_task(Task("Physics", "tues", 10))

    assert scheduler.rows[10]["tues"] == "Math, Physics"


def test_tasks_go_to_correct_rows():
    scheduler = SchedulerLogic()

    scheduler.add_task(Task("Chemistry", "fri", 3))
    scheduler.add_task(Task("Biology", "fri", 4))

    assert scheduler.rows[3]["fri"] == "Chemistry"
    assert scheduler.rows[4]["fri"] == "Biology"


def test_populate_clears_then_refills():
    scheduler = SchedulerLogic()

    scheduler.add_task(Task("History", "sun", 2))
    scheduler.add_task(Task("English", "sun", 2))

    # Should contain both tasks
    assert scheduler.rows[2]["sun"] == "History, English"

    # Repopulate to ensure clearing logic works
    scheduler.populate_calendar()

    assert scheduler.rows[2]["sun"] == "History, English"


def test_empty_scheduler_starts_empty():
    scheduler = SchedulerLogic()

    for row in scheduler.rows:
        for day in ["sun", "mon", "tues", "wed", "thur", "fri", "sat"]:
            assert row[day] == ""
