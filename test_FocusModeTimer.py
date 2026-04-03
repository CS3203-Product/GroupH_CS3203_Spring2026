import unittest
from UnCram import FocusModeTimer

class TestFocusModeTimer(unittest.TestCase):

    def setUp(self):
        # Initializing with small numbers (1 min) makes testing math easier
        self.timer = FocusModeTimer(work_min=25, break_min=5, long_break_min=20)

    def test_initialization(self):
        """Test if the timer starts with the correct settings."""
        self.assertEqual(self.timer.work_sec, 1500) # 25 * 60
        self.assertEqual(self.timer.mode, "Work")
        self.assertEqual(self.timer.completed_pomodoros, 0)
        self.assertFalse(self.timer.is_running)

    def test_format_time(self):
        """Test if seconds are converted to MM:SS correctly."""
        self.timer.time_left = 125 # 2 minutes and 5 seconds
        self.assertEqual(self.timer.format_time(), "02:05")
        
        self.timer.time_left = 45
        self.assertEqual(self.timer.format_time(), "00:45")

    def test_start_break_manual(self):
        """Test the manual 'Start Break' button logic you added."""
        self.timer.start_break_session()
        self.assertEqual(self.timer.mode, "Break")
        self.assertEqual(self.timer.time_left, 300) # 5 * 60
        self.assertTrue(self.timer.is_running)

    def test_pomodoro_completion_loop(self):
        """
        Test the 'tick' logic: When work hits 0, 
        does it increment the count and switch to Break?
        """
        self.timer.mode = "Work"
        self.timer.time_left = 0
        
        # This simulates the clock hitting zero
        self.timer.tick() 
        
        self.assertEqual(self.timer.completed_pomodoros, 1)
        self.assertEqual(self.timer.mode, "Break")
        self.assertEqual(self.timer.time_left, 300)

    def test_long_break_trigger(self):
        """Test if 4 pomodoros trigger a Long Break."""
        self.timer.mode = "Work"
        self.timer.completed_pomodoros = 3 # Already did 3
        self.timer.time_left = 0
        
        # Finish the 4th pomodoro
        self.timer.tick()
        
        self.assertEqual(self.timer.completed_pomodoros, 4)
        self.assertEqual(self.timer.mode, "Long Break")
        self.assertEqual(self.timer.time_left, 1200) # 20 * 60

    def test_reset(self):
        """Test if reset puts everything back to the start."""
        self.timer.mode = "Break"
        self.timer.time_left = 10
        self.timer.reset()
        
        self.assertEqual(self.timer.mode, "Work")
        self.assertEqual(self.timer.time_left, 1500)
        self.assertFalse(self.timer.is_running)

if __name__ == "__main__":
    unittest.main()
