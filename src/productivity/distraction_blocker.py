"""Blocks configured sites during a fixed daily focus window."""


class DistractionBlocker:
    def __init__(self) -> None:
        self.blocked_sites: list[str] = []

    def set_blocked_sites(self, sites: list[str]) -> None:
        self.blocked_sites = sites

    def check_access(self, url: str, current_time: str) -> bool:
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

        hours, minutes = map(int, current_time.split(":"))
        total_minutes = hours * 60 + minutes

        session_start = 10 * 60 + 30
        session_end = 20 * 60
        in_session = session_start <= total_minutes < session_end

        if in_session and url in self.blocked_sites:
            return True
        return False
