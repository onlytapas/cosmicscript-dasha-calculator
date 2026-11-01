"""
Turns raw engine output into the view model rendered by ``report.html``.

Nothing here calculates numerology; it only formats, labels and explains the
values the engine already produced, so the report can walk the reader through
each step.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from numerology import interpretations as text
from numerology.constants import GRID_LAYOUT, MONTH_NAMES, MONTH_NAMES_SHORT, PLANETS
from numerology.engine import generate_full_report, safe_date


# --------------------------------------------------------------------------- #
# Small formatting helpers
# --------------------------------------------------------------------------- #
def format_date(d: datetime) -> str:
    """29 Jan 1990"""
    return f"{d.day} {MONTH_NAMES_SHORT[d.month - 1]} {d.year}"


def format_date_long(d: datetime) -> str:
    """29 January 1990"""
    return f"{d.day} {MONTH_NAMES[d.month - 1]} {d.year}"


def digits_added(n: int) -> str:
    """Render the digits of ``n`` as an addition, e.g. 1990 -> '1 + 9 + 9 + 0'."""
    return " + ".join(str(n))


def reduction_steps(value: int, results: list[int]) -> list[dict]:
    """Describe successive digit sums of ``value`` using the engine's own results.

    ``results`` holds the value after each application of ``digit_sum_once``;
    a step is only shown when there was something to add.
    """
    steps = []
    current = value
    for result in results:
        if current >= 10:
            steps.append({"expression": digits_added(current), "result": result})
        current = result
    return steps


def current_cycle_year(raw: dict, today: datetime) -> int:
    """The birthday-year (birthday to next birthday) that contains ``today``."""
    birthday_this_year = safe_date(today.year, raw["month"], raw["day"])
    return today.year if today >= birthday_this_year else today.year - 1


def age_on(date: datetime, birth: datetime) -> int:
    years = date.year - birth.year
    if (date.month, date.day) < (birth.month, birth.day):
        years -= 1
    return years


# --------------------------------------------------------------------------- #
# Section builders
# --------------------------------------------------------------------------- #
def _number_profile(number: int, interpretation: dict) -> dict:
    planet = PLANETS[number]
    return {
        "number": number,
        "planet": planet,
        "ruling_planet": interpretation["Ruling Planet"],
        "sections": [
            {"title": label, "body": body}
            for label, body in interpretation.items()
            if label != "Ruling Planet"
        ],
        "colours": text.FAVOURABLE_COLOURS[number],
        "days": text.FAVOURABLE_DAYS[number],
        "friendly": text.FRIENDLY_NUMBERS[number],
        "neutral": text.NEUTRAL_NUMBERS[number],
        "enemy": text.ENEMY_NUMBERS[number],
    }


def _calculation_steps(raw: dict) -> dict:
    s = raw["calc"]["dasha_steps"]
    return {
        "day": {
            "value": raw["day"],
            "steps": reduction_steps(raw["day"], [s["day_sum"], s["day_root"]]),
            "result": s["day_root"],
        },
        "month": {
            "value": raw["month"],
            "steps": reduction_steps(raw["month"], [s["month_sum"], s["month_root"]]),
            "result": s["month_root"],
        },
        "year": {
            "value": raw["year"],
            "steps": reduction_steps(raw["year"], [s["year_sum"], s["year_root"]]),
            "result": s["year_root"],
        },
        "destiny": {
            "parts": [s["day_root"], s["month_root"], s["year_root"]],
            "total": s["total"],
            "steps": reduction_steps(s["total"], [s["total_sum"], s["destiny"]]),
            "result": s["destiny"],
        },
    }


def _grid_sources(raw: dict) -> list[dict]:
    """Explain where each digit placed in the natal grid comes from."""
    g = raw["calc"]["grid_digits"]
    yy = raw["calc"]["year_digits"]["C4"]

    def digits(keys):
        return [g[k] for k in keys if g[k] is not None]

    root_note = ("already present in the day digits, so not added again"
                 if g["Root"] is None else "")
    return [
        {"label": "Day", "value": str(raw["day"]).zfill(2), "digits": digits(["B1", "B2"]),
         "note": "zeros are never placed"},
        {"label": "Month", "value": str(raw["month"]).zfill(2), "digits": digits(["M1", "M2"]),
         "note": "zeros are never placed"},
        {"label": "Year", "value": f"{raw['year']} → {yy}", "digits": digits(["Y1", "Y2"]),
         "note": "last two digits of the year"},
        {"label": "Root", "value": str(raw["calc"]["root"]), "digits": digits(["Root"]),
         "note": root_note},
        {"label": "Destiny", "value": str(raw["calc"]["destiny"]), "digits": digits(["Destiny"]),
         "note": ""},
    ]


def _grid_cells(grid: dict) -> list[list[dict]]:
    return [
        [{"position": n, "planet": PLANETS[n], "value": grid[n], "count": len(grid[n])} for n in row]
        for row in GRID_LAYOUT
    ]


def _maha_dasha(raw: dict, today: datetime) -> dict:
    periods = []
    for p in raw["dasha_periods"]:
        periods.append({
            "number": p["number"],
            "planet": PLANETS[p["number"]],
            "start": format_date(p["start"]),
            "end": format_date(p["end"]),
            "start_age": p["start_age"],
            "end_age": p["start_age"] + p["duration"],
            "duration": p["duration"],
            "is_current": p["start"] <= today <= p["end"],
            "is_past": p["end"] < today,
        })
    current = next((p for p in periods if p["is_current"]), None)

    # One timeline row per 1–9 cycle, covering roughly the first ninety years.
    rows: list[list[dict]] = []
    for p in periods:
        if not rows or p["number"] == 1:
            rows.append([])
        rows[-1].append(p)
    timeline = []
    for row in rows:
        if row[0]["start_age"] >= 80:
            break
        total_years = sum(p["duration"] for p in row)
        timeline.append({
            "start_age": row[0]["start_age"],
            "end_age": row[-1]["end_age"],
            "segments": [dict(p, width=round(100 * p["duration"] / total_years, 2)) for p in row],
        })
    return {"periods": periods, "current": current, "timeline": timeline}


def _antardasha(raw: dict, cycle_year: int) -> dict:
    root = raw["calc"]["root"]
    reduced_month = raw["calc"]["reduced_month"]
    rows = []
    for a in raw["antardasha_data"]:
        number = a["antardasha_number"]
        rows.append({
            "year": a["year"],
            "birthday": format_date(a["date"]),
            "weekday": a["day_name"],
            "weekday_planet": PLANETS[a["planet_number"]],
            "parts": [a["yy"], root, reduced_month, a["planet_number"]],
            "total": a["sum"],
            "steps": reduction_steps(a["sum"], [a["P"], number]),
            "number": number,
            "planet": PLANETS[number],
            "is_current": a["year"] == cycle_year,
        })
    return {
        "rows": rows,
        "root": root,
        "reduced_month": reduced_month,
        "current": next((r for r in rows if r["is_current"]), None),
    }


def _review_years(raw: dict, today: datetime, cycle_year: int) -> list[dict]:
    years = []
    for ry in raw["review_years"]:
        prats = []
        total_days = sum((p["end"] - p["start"]).days + 1 for p in ry["pratyantar"]) or 1
        for p in ry["pratyantar"]:
            days = (p["end"] - p["start"]).days + 1
            prats.append({
                "number": p["number"],
                "planet": p["planet"],
                "start": format_date(p["start"]),
                "end": format_date(p["end"]),
                "days": days,
                "width": round(100 * days / total_days, 2),
                "is_active": p["start"] <= today <= p["end"],
            })
        years.append({
            "year": ry["year"],
            "label": f"{ry['year']}–{ry['year'] + 1}",
            "maha": PLANETS.get(ry["maha_dasha"]) if ry["maha_dasha"] else None,
            "antar": PLANETS.get(ry["antar_dasha"]) if ry["antar_dasha"] else None,
            "cells": _grid_cells(ry["grid"]),
            "pratyantar": prats,
            "active_pratyantar": next((p for p in prats if p["is_active"]), None),
            "is_current": ry["year"] == cycle_year,
        })
    return years


# --------------------------------------------------------------------------- #
# Public entry point
# --------------------------------------------------------------------------- #
def build_report(day: int, month: int, year: int, client_name: str = "",
                 today: Optional[datetime] = None) -> dict:
    """Calculate everything for a birth date and shape it for the template."""
    today = (today or datetime.now()).replace(hour=0, minute=0, second=0, microsecond=0)
    raw = generate_full_report(day, month, year, today=today)
    root = raw["calc"]["root"]
    destiny = raw["calc"]["destiny"]
    birth = raw["birth_date"]

    cycle_year = current_cycle_year(raw, today)
    maha = _maha_dasha(raw, today)
    antar = _antardasha(raw, cycle_year)
    years = _review_years(raw, today, cycle_year)

    return {
        "client_name": client_name.strip(),
        "dob": format_date_long(birth),
        "dob_short": format_date(birth),
        "birth_weekday": birth.strftime("%A"),
        "age": age_on(today, birth),
        "report_date": format_date_long(today),
        "report_year": today.year,
        "root": _number_profile(root, text.ROOT_INTERPRETATIONS[root]),
        "destiny": _number_profile(destiny, text.DESTINY_INTERPRETATIONS[destiny]),
        "steps": _calculation_steps(raw),
        "grid": {
            "cells": _grid_cells(raw["natal_grid"]),
            "sources": _grid_sources(raw),
            "present": [n for n in range(1, 10) if raw["natal_grid"][n]],
            "missing": [n for n in range(1, 10) if not raw["natal_grid"][n]],
            "repeated": [n for n in range(1, 10) if len(raw["natal_grid"][n]) > 1],
        },
        "maha": maha,
        "antar": antar,
        "years": years,
        "now": {
            "maha": maha["current"],
            "antar": antar["current"],
            "pratyantar": next((y["active_pratyantar"] for y in years if y["active_pratyantar"]), None),
        },
        "planets": PLANETS,
    }
