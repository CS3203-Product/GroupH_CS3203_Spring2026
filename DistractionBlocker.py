class DistractionBlocker:
    # This feature blocks websites that are distractions to users during scheduled task sessions (10:30AM - 20:00).  
    # When the website is blocked, check_access returns true.
    # When website is not blocked, check_access returns false. 
    # Raise ValueError is for invalid/empty URLs.
    def __init__(self):
      
        self.blocked_sites = []

    def set_blocked_sites(self, sites):
        
        self.blocked_sites = sites
    #CWE-703: Validate URL inputs before processing to prevent unexpected crashse
    def check_access(self, url, current_time, window_start="10:30", window_end="20:00"):
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")
    #CWE-703: wrap time sparsing in try/except. Malformed time strings will crash without it
        hours, minutes = map(int, current_time.split(":"))
        total_minutes = hours * 60 + minutes

        def to_minutes(hm: str) -> int:
            h, m = map(int, hm.strip().split(":"))
            return h * 60 + m

        start_m = to_minutes(window_start)
        end_m = to_minutes(window_end)

        if start_m <= end_m:
            in_session = start_m <= total_minutes < end_m
        else:
            # Overnight window (e.g. 10:30 PM → 6:00 AM)
            in_session = total_minutes >= start_m or total_minutes < end_m

        if in_session and url in self.blocked_sites:
            return True
        return False
