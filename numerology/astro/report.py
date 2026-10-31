"""Builds the view model for ``astro_report.html``."""

from __future__ import annotations

import math
from datetime import datetime
from typing import Optional

from numerology.astro import ephemeris
from numerology.astro.constants import PLANETS, SIGNS, WEEKDAY_NAMES
from numerology.astro.places import Place
from numerology.astro.timeutil import BirthMoment, birth_moment, utc_to_local
from numerology.astro.vedic import describe_longitude, dms, house_from, panchang, running_periods, vimshottari
from numerology.report import format_date, format_date_long

CHART_STYLES = ("north", "south")

# South Indian chart: fixed sign positions in a 4x4 grid (row, col) by sign index.
SOUTH_LAYOUT = {11: (0, 0), 0: (0, 1), 1: (0, 2), 2: (0, 3), 10: (1, 0), 3: (1, 3),
                9: (2, 0), 4: (2, 3), 8: (3, 0), 7: (3, 1), 6: (3, 2), 5: (3, 3)}


def format_time(d: datetime) -> str:
    return d.strftime("%H:%M")


def _chart(positions: dict, lagna_sign_index: int, key: str) -> dict:
    """Occupants per sign for the Rasi (key='sign_index') or Navamsa (key='navamsa_index')."""
    by_sign = {i: [] for i in range(12)}
    for p in PLANETS:
        pos = positions[p["key"]]
        by_sign[pos[key]].append({"abbr": p["abbr"], "key": p["key"], "retrograde": pos["retrograde"]})
    houses = []
    for h in range(12):
        sign_index = (lagna_sign_index + h) % 12
        houses.append({
            "house": h + 1,
            "sign_index": sign_index,
            "sign": SIGNS[sign_index].name,
            "sign_number": sign_index + 1,
            "planets": by_sign[sign_index],
        })
    # South Indian grid: 4x4 cells; the centre is one merged cell and the
    # three cells it covers are None so the template skips them.
    south = [[None] * 4 for _ in range(4)]
    for sign_index, (r, c) in SOUTH_LAYOUT.items():
        south[r][c] = {
            "sign_index": sign_index,
            "sign": SIGNS[sign_index].name,
            "sign_abbr": SIGNS[sign_index].name[:3],
            "planets": by_sign[sign_index],
            "is_lagna": sign_index == lagna_sign_index,
        }
    south[1][1] = {"center": True}
    return {"lagna_sign_index": lagna_sign_index, "lagna_sign": SIGNS[lagna_sign_index].name, "houses": houses, "south": south}


def _period_view(p: dict, tz: str, now_utc: datetime, depth: int) -> dict:
    view = {
        "lord": p["lord"],
        "start": format_date(utc_to_local(p["start"], tz)),
        "end": format_date(utc_to_local(p["end"], tz)),
        "days": math.floor(p["days"] + 0.5),   # half up, as the browser build rounds
        "is_current": p["start"] <= now_utc < p["end"],
        "is_past": p["end"] <= now_utc,
    }
    if "years" in p:
        view["years"] = p["years"]
    if "sub" in p:
        view["sub"] = [_period_view(s, tz, now_utc, depth + 1) for s in p["sub"]]
    return view


def build_astro_report(name: str, gender: str, year: int, month: int, day: int, hour: int, minute: int,
                       place: Place, chart_style: str = "north", ayanamsa_mode: str = "lahiri",
                       today: Optional[datetime] = None) -> dict:
    today = today or datetime.utcnow()
    chart_style = chart_style if chart_style in CHART_STYLES else "north"
    ephemeris.set_ayanamsa(ayanamsa_mode)
    moment: BirthMoment = birth_moment(year, month, day, hour, minute, place.timezone)

    raw = ephemeris.planet_longitudes(moment.jd_ut)
    lagna_lon = ephemeris.ascendant(moment.jd_ut, place.latitude, place.longitude)
    lagna = describe_longitude(lagna_lon)

    positions = {}
    for p in PLANETS:
        d = describe_longitude(raw[p["key"]]["longitude"])
        d.update({
            "key": p["key"], "abbr": p["abbr"], "symbol": p["symbol"],
            "retrograde": raw[p["key"]]["retrograde"],
            "house": house_from(d["sign_index"], lagna["sign_index"]),
        })
        positions[p["key"]] = d
    moon, sun = positions["Moon"], positions["Sun"]

    local_weekday = (moment.local.weekday() + 1) % 7
    dasha = vimshottari(moon["longitude"], moment.utc)
    chain = running_periods(dasha["mahadashas"], today)
    now = [{"lord": p["lord"], "start": format_date(utc_to_local(p["start"], place.timezone)),
            "end": format_date(utc_to_local(p["end"], place.timezone))} for p in chain]

    return {
        "name": name.strip(),
        "gender": gender,
        "birth": {
            "date": format_date_long(moment.local),
            "time": format_time(moment.local),
            "weekday": WEEKDAY_NAMES[local_weekday],
            "place": place.label,
            "latitude": place.latitude,
            "longitude": place.longitude,
            "timezone": place.timezone,
            "utc_offset": moment.utc_offset_hours,
            "utc": f"{format_date(moment.utc)} {format_time(moment.utc)}",
            "jd": round(moment.jd_ut, 5),
            "ayanamsa": dms(ephemeris.ayanamsa(moment.jd_ut)),
            "ayanamsa_name": ayanamsa_mode,
        },
        "report_date": format_date_long(today),
        "report_year": today.year,
        "chart_style": chart_style,
        "lagna": lagna,
        "moon": moon,
        "sun": sun,
        "positions": [positions[p["key"]] for p in PLANETS],
        "rasi": _chart(positions, lagna["sign_index"], "sign_index"),
        "navamsa": _chart(positions, lagna["navamsa_index"], "navamsa_index"),
        "panchang": panchang(sun["longitude"], moon["longitude"], local_weekday),
        "dasha": {
            "nakshatra": dasha["nakshatra"],
            "nakshatra_lord": dasha["nakshatra_lord"],
            "fraction_elapsed": round(dasha["fraction_elapsed"], 4),
            "balance_years": round(dasha["balance_years"], 2),
            "balance_text": _years_text(dasha["balance_days"]),
            "mahadashas": [_period_view(m, place.timezone, today, 1) for m in dasha["mahadashas"]],
        },
        "now": now,
        "now_text": " › ".join(p["lord"] for p in now),
        "now_last": now[-1] if now else None,
    }


def _years_text(days: float) -> str:
    years = int(days // 365.25)
    rem = days - years * 365.25
    months = int(rem // 30.4375)
    d = int(rem - months * 30.4375)
    return f"{years} years, {months} months, {d} days"
