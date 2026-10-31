"""Local birth time to Universal Time and Julian Day."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import swisseph as swe


@dataclass(frozen=True)
class BirthMoment:
    local: datetime          # naive, as entered
    utc: datetime            # naive UTC
    utc_offset_hours: float  # e.g. 5.5 for IST
    jd_ut: float
    timezone: str


def birth_moment(year: int, month: int, day: int, hour: int, minute: int, tz_name: str) -> BirthMoment:
    local = datetime(year, month, day, hour, minute)
    aware = local.replace(tzinfo=ZoneInfo(tz_name))
    offset = aware.utcoffset() or timedelta(0)
    utc = (aware - offset).replace(tzinfo=None)
    jd = swe.julday(utc.year, utc.month, utc.day, utc.hour + utc.minute / 60 + utc.second / 3600)
    return BirthMoment(local, utc, offset.total_seconds() / 3600, jd, tz_name)


def jd_to_datetime(jd: float) -> datetime:
    y, m, d, h = swe.revjul(jd)
    return datetime(y, m, d) + timedelta(hours=h)


def utc_to_local(utc: datetime, tz_name: str) -> datetime:
    return utc.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(tz_name)).replace(tzinfo=None)
