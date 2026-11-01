"""
The Complete Reading: the numerology, name numerology and astrology reports for
one person, built by the same functions as the single reports so the numbers
cannot differ between them.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from numerology.astro.places import Place
from numerology.astro.report import build_astro_report
from numerology.name_report import build_name_report
from numerology.report import build_report, format_date_long


def build_complete_report(name: str, gender: str, day: int, month: int, year: int, hour: int, minute: int,
                          place: Place, chart_style: str = "north", options: Optional[list[str]] = None,
                          today: Optional[datetime] = None) -> dict:
    today = today or datetime.now()
    return {
        "name": name,
        "report_date": format_date_long(today),
        "report_year": today.year,
        "numerology": build_report(day, month, year, name, today=today),
        "name_report": build_name_report(name, "person", name, today=today, birth=(day, month, year), options=options),
        "astro": build_astro_report(name, gender, year, month, day, hour, minute, place, chart_style=chart_style, today=today),
    }
