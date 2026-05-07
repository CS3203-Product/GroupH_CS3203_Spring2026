"""Tests for distraction blocker local ↔ UTC window conversion."""

from datetime import datetime

from zoneinfo import ZoneInfo

from src.productivity.blocker_schedule import (
    local_window_to_utc_hhmm_pair,
    utc_window_to_local_hhmm_pair,
)


def test_local_same_day_converts_to_utc() -> None:
    ref = datetime(2024, 6, 15, 12, 0, tzinfo=ZoneInfo("America/New_York"))
    start_utc, end_utc = local_window_to_utc_hhmm_pair(
        "10:30", "20:00", "America/New_York", ref=ref
    )
    assert start_utc == "14:30"
    assert end_utc == "00:00"


def test_local_overnight_end_on_next_local_day() -> None:
    ref = datetime(2024, 6, 15, 12, 0, tzinfo=ZoneInfo("America/New_York"))
    start_utc, end_utc = local_window_to_utc_hhmm_pair(
        "22:00", "06:00", "America/New_York", ref=ref
    )
    assert start_utc == "02:00"
    assert end_utc == "10:00"


def test_utc_pair_round_trips_to_local_overnight() -> None:
    ref_local = datetime(2024, 6, 15, 12, 0, tzinfo=ZoneInfo("America/New_York"))
    su, eu = local_window_to_utc_hhmm_pair(
        "22:00", "06:00", "America/New_York", ref=ref_local
    )
    ref_utc = datetime(2024, 6, 16, 8, 0, tzinfo=ZoneInfo("UTC"))
    sl, el = utc_window_to_local_hhmm_pair(su, eu, "America/New_York", ref=ref_utc)
    assert sl == "22:00"
    assert el == "06:00"
