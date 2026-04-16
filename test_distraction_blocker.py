import unittest


class DistractionBlocker:
    # This feature blocks websites that are distractions to users during scheduled task sessions (10:30AM - 20:00).  
    # When the website is blocked, check_access returns true.
    # When website is not blocked, check_access returns false. 
    # Raise ValueError is for invalid/empty URLs.

    def __init__(self):
        
        self.blocked_sites = []

    def set_blocked_sites(self, sites):
        
        self.blocked_sites = sites

    def check_access(self, url, current_time):
        
        if not url or not url.strip():
            
            raise ValueError("URL cannot be empty.")

        # Time format: hours and minutes
        hours, minutes = map(int, current_time.split(":"))
        
        total_minutes = hours * 60+ minutes

        # Task session (start and end time block): 10:30 (630 minutes) to 20:00 (1200 minutes)

        session_start = 10*60+ 30 

        session_end = 20 * 60          

        in_session= session_start <= total_minutes<session_end

        if in_session and url in self.blocked_sites:

            return True  # for when site is blocked

        return False  #for when site is unblocked , accessible


class TestDistractionBlocker(unittest.TestCase):

    def setUp(self):

        self.blocker = DistractionBlocker()

        self.blocked=  ["facebook.com"]

        self.blocker.set_blocked_sites(self.blocked)  

    def test_block_valid_site_during_task_session(self):

        # At 20:00, the session ends and access to other sites is opened

        result = self.blocker.check_access("facebook.com", current_time="20:00")
        
        self.assertFalse(result, "Access to sites open after 20:00")

    def test_boundary_start_time(self):

        # At 10:30, the session starts and access to other sites should be blocked

        result =self.blocker.check_access("facebook.com", current_time="10:30")
        
        self.assertTrue(result, "Blocker activates at 10:30 AM")

    def test_invalid_url_format(self):

        with self.assertRaises(ValueError):
            
            self.blocker.check_access("", current_time="10:30")


if __name__ == "__main__":
    
    unittest.main()
