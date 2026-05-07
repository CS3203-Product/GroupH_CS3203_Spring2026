"""12-hour (AM/PM) helpers and validation for distraction blocker schedule."""

from __future__ import annotations

import re
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

_HHMM = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def resolve_time_zone(name: str) -> ZoneInfo:
    """Best-effort IANA zone from the browser; invalid or empty → UTC."""
    n = (name or "").strip()
    if not n:
        return ZoneInfo("UTC")
    try:
        return ZoneInfo(n)
    except Exception:
        return ZoneInfo("UTC")


def _hhmm_to_minutes(hhmm: str) -> int:
    h, m = map(int, hhmm.strip().split(":"))
    return h * 60 + m


def local_window_to_utc_hhmm_pair(
    start_hhmm: str,
    end_hhmm: str,
    tz_name: str,
    ref: datetime | None = None,
) -> tuple[str, str]:
    """Convert a local daily window to UTC ``HH:MM`` pair (end may be the next local day)."""
    tz = resolve_time_zone(tz_name)
    if ref is None:
        ref_local = datetime.now(tz)
    else:
        ref_local = (
            ref.replace(tzinfo=timezone.utc).astimezone(tz)
            if ref.tzinfo is None
            else ref.astimezone(tz)
        )
    start_date: date = ref_local.date()
    sm = _hhmm_to_minutes(start_hhmm)
    em = _hhmm_to_minutes(end_hhmm)
    end_date = start_date + timedelta(days=1) if sm > em else start_date

    sh, smin = map(int, start_hhmm.strip().split(":"))
    eh, emin = map(int, end_hhmm.strip().split(":"))
    start_dt = datetime.combine(start_date, time(sh, smin), tzinfo=tz)
    end_dt = datetime.combine(end_date, time(eh, emin), tzinfo=tz)
    return (
        start_dt.astimezone(timezone.utc).strftime("%H:%M"),
        end_dt.astimezone(timezone.utc).strftime("%H:%M"),
    )


def utc_window_to_local_hhmm_pair(
    start_utc_hhmm: str,
    end_utc_hhmm: str,
    tz_name: str,
    ref: datetime | None = None,
) -> tuple[str, str]:
    """Map stored UTC window to local ``HH:MM`` pair for display (handles UTC overnight wrap)."""
    tz = resolve_time_zone(tz_name)
    if ref is None:
        ref_utc = datetime.now(timezone.utc)
    else:
        ref_utc = (
            ref.replace(tzinfo=timezone.utc)
            if ref.tzinfo is None
            else ref.astimezone(timezone.utc)
        )
    d = ref_utc.date()
    su_h, su_m = map(int, start_utc_hhmm.strip().split(":"))
    eu_h, eu_m = map(int, end_utc_hhmm.strip().split(":"))
    sm = su_h * 60 + su_m
    em = eu_h * 60 + eu_m
    end_d = d + timedelta(days=1) if sm > em else d

    start_dt = datetime.combine(d, time(su_h, su_m), tzinfo=timezone.utc)
    end_dt = datetime.combine(end_d, time(eu_h, eu_m), tzinfo=timezone.utc)
    return (
        start_dt.astimezone(tz).strftime("%H:%M"),
        end_dt.astimezone(tz).strftime("%H:%M"),
    )


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
