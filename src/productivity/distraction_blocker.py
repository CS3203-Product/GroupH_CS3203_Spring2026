"""Blocks configured sites during a fixed daily focus window."""


class DistractionBlocker:
    def __init__(self) -> None:
        self.blocked_sites: list[str] = []

    def set_blocked_sites(self, sites: list[str]) -> None:
        self.blocked_sites = sites

    def check_access(
        self,
        url: str,
        current_time: str,
        window_start: str = "10:30",
        window_end: str = "20:00",
    ) -> bool:
        if not url or not url.strip():
            raise ValueError("URL cannot be empty.")

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
            in_session = total_minutes >= start_m or total_minutes < end_m

        if in_session and url in self.blocked_sites:
            return True
        return False
