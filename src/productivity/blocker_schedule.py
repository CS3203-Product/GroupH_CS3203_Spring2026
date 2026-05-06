"""12-hour (AM/PM) helpers and validation for distraction blocker schedule."""

from __future__ import annotations

import re

_HHMM = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def is_valid_hhmm(s: str) -> bool:
    return bool(s and _HHMM.match(s.strip()))


def hhmm_to_ampm_parts(hhmm: str) -> tuple[int, int, str]:
    """Convert 24h ``HH:MM`` to display hour (1–12), minute, ``AM`` or ``PM``."""
    h, mi = map(int, hhmm.strip().split(":"))
    is_pm = h >= 12
    h12 = h % 12
    if h12 == 0:
        h12 = 12
    return h12, mi, ("PM" if is_pm else "AM")


def ampm_parts_to_hhmm(hour12: int, minute: int, period: str) -> str:
    """Build 24h ``HH:MM`` from 12-hour clock parts."""
    period = period.upper().strip()
    if period not in ("AM", "PM"):
        raise ValueError("period must be AM or PM")
    if not (1 <= hour12 <= 12):
        raise ValueError("hour must be 1–12")
    if not (0 <= minute <= 59):
        raise ValueError("minute must be 0–59")
    if period == "AM":
        h24 = 0 if hour12 == 12 else hour12
    else:
        h24 = 12 if hour12 == 12 else hour12 + 12
    return f"{h24:02d}:{minute:02d}"
