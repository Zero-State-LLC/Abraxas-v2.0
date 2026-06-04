from __future__ import annotations

from datetime import datetime, timezone


def parse_iso_datetime(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def is_quiet_window(now: datetime, start_hour: int, end_hour: int) -> bool:
    if not 0 <= start_hour <= 23 or not 0 <= end_hour <= 23:
        raise ValueError("quiet_window_hours_out_of_range")

    hour = now.astimezone(timezone.utc).hour
    if start_hour == end_hour:
        return False
    if start_hour < end_hour:
        return start_hour <= hour < end_hour
    return hour >= start_hour or hour < end_hour


def operator_window_active(active_windows: list[dict[str, object]], domain: str, now: datetime) -> bool:
    for window in active_windows:
        if window.get("domain") not in (domain, "*"):
            continue
        if window.get("approved") is not True:
            continue
        start = parse_iso_datetime(str(window.get("start")))
        end = parse_iso_datetime(str(window.get("end")))
        if start <= now <= end:
            return True
    return False
