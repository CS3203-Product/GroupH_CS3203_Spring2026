<<<<<<< HEAD
import unittest
from unittest.mock import MagicMock
from UnCram import FocusModeTimer

class TestFocusModeTimer(unittest.TestCase):

    def setUp(self):
        """Runs before every test. Mocks NiceGUI to prevent UI errors."""
        # We 'Mock' the UI elements so the test doesn't crash without a browser
        import nicegui.ui as ui
        ui.label = MagicMock()
        ui.button = MagicMock()
        ui.card = MagicMock()
        ui.row = MagicMock()
        ui.timer = MagicMock()
        ui.audio = MagicMock()
        ui.notify = MagicMock()

        # Initialize timer with 1 min work, 5 min break, 20 min long break
        self.timer = FocusModeTimer(work_min=1, break_min=5, long_break_min=20)

    def test_initial_state(self):
        """Verify the timer starts in Work mode with 60 seconds."""
        self.assertEqual(self.timer.mode, "Work")
        self.assertEqual(self.timer.time_left, 60)
        self.assertEqual(self.timer.completed_pomodoros, 0)

    def test_format_time(self):
        """Verify seconds are converted to string correctly."""
        self.timer.time_left = 90
        self.assertEqual(self.timer.format_time(), "01:30")
        self.timer.time_left = 5
        self.assertEqual(self.timer.format_time(), "00:05")

    def test_manual_break_button(self):
        """Test the 'Start Break' button logic."""
        self.timer.start_break_session()
        self.assertEqual(self.timer.mode, "Break")
        self.assertEqual(self.timer.time_left, 300) # 5 minutes
        self.assertFalse(self.timer.is_running)

    def test_work_to_break_transition(self):
        """Test if finishing work automatically starts a short break."""
        self.timer.time_left = 0
        self.timer.tick() # This finishes the 'Work' session
        
        self.assertEqual(self.timer.completed_pomodoros, 1)
        self.assertEqual(self.timer.mode, "Break")
        self.assertEqual(self.timer.time_left, 300)

    def test_long_break_after_four_pomodoros(self):
        """Verify the 4th session triggers a Long Break."""
        self.timer.completed_pomodoros = 3
        self.timer.mode = "Work"
        self.timer.time_left = 0
        
        self.timer.tick() # Finishes 4th session
        
        self.assertEqual(self.timer.completed_pomodoros, 4)
        self.assertEqual(self.timer.mode, "Long Break")
        self.assertEqual(self.timer.time_left, 1200) # 20 minutes

    def test_reset_logic(self):
        """Verify reset returns everything to initial work state."""
        self.timer.mode = "Break"
        self.timer.time_left = 10
        self.timer.reset()
        
        self.assertEqual(self.timer.mode, "Work")
        self.assertEqual(self.timer.time_left, 60)
        self.assertFalse(self.timer.is_running)

if __name__ == '__main__':
    unittest.main()
=======

>>>>>>> 6e92cd4 (Create unit test)
