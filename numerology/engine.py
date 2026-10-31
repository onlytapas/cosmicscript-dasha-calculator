"""
Calculation engine for the Vedic Dasha numerology report.

Every formula here reproduces the ``dasha calculator.xlsx`` spreadsheet exactly.
The spreadsheet cell names (``B2``, ``J4``, ``A5`` and so on) are kept in the
returned dictionaries so that each displayed step can be traced back to the
sheet it came from. Do not "simplify" the arithmetic: the intermediate values
are part of the report.
"""

from __future__ import annotations

import calendar
from datetime import datetime, timedelta
from typing import Optional

from numerology.constants import (
    ANTARDASHA_YEARS_AFTER,
    ANTARDASHA_YEARS_BEFORE,
    DAY_NAMES,
    MAHA_DASHA_PERIODS_SHOWN,
    PLANETS,
    PRATYANTAR_DAYS_PER_UNIT,
    REVIEW_YEARS_AFTER,
    REVIEW_YEARS_BEFORE,
    WEEKDAY_PLANET,
)


# --------------------------------------------------------------------------- #
# Digit helpers
# --------------------------------------------------------------------------- #
def digit_sum_once(n: int) -> int:
    """Add the digits of ``n`` a single time (19 -> 10)."""
    return sum(int(d) for d in str(abs(int(n))))


def digit_sum_to_single(n: int) -> int:
    """Add the digits of ``n`` repeatedly until one digit remains (19 -> 1)."""
    n = abs(int(n))
    while n > 9:
        n = digit_sum_once(n)
    return n


def safe_date(year: int, month: int, day: int) -> datetime:
    """Build a date, clamping 29 Feb and the 31st to the last valid day."""
    if month == 2 and day == 29 and not calendar.isleap(year):
        day = 28
    if month in (4, 6, 9, 11) and day == 31:
        day = 30
    return datetime(year, month, day)


# --------------------------------------------------------------------------- #
# Root and Destiny (Grids sheet rows 2–5 and Dasha sheet A3:A7)
# --------------------------------------------------------------------------- #
def calc_root_and_destiny(day: int, month: int, year: int) -> dict:
    """Return the Root (Moolank), Destiny (Bhagyank) and the digits feeding the grid."""
    # Day decomposition (Grids row 2)
    A2 = day
    B2 = int(str(A2)[0]) if A2 >= 10 else 0
    C2 = int(str(A2)[-1])
    D2 = C2 + B2
    E2 = int(str(D2)[0]) if D2 >= 10 else 0
    G2 = int(str(D2)[-1])
    H2 = E2 + G2
    I2 = H2
    if H2 == day:
        I2 = 0
    elif day != 0 and H2 == day / 10:
        I2 = 0

    # Month decomposition (Grids row 3)
    A3 = month
    B3 = int(str(A3)[0]) if A3 >= 10 else 0
    C3 = int(str(A3)[-1])
    D3 = C3 + B3

    # Year decomposition (Grids row 4)
    year_str = str(year)
    first2 = year_str[:2]
    B4 = 1 if first2 == "19" else (2 if first2 == "20" else 9)
    C4str = str(int(year_str[-2:])).zfill(2)
    D4 = int(C4str[0])
    E4 = int(C4str[1])
    G4 = E4 + D4 + B4
    H4 = int(str(G4)[0]) if G4 >= 10 else 0
    I4 = int(str(G4)[-1])
    J4 = I4 + H4

    # Destiny (Grids row 5)
    A5 = H2 + D3 + J4

    # Root (Dasha sheet)
    dasha_A3 = digit_sum_once(day)
    dasha_A4 = digit_sum_once(dasha_A3)
    root = dasha_A4

    # Destiny (Dasha sheet)
    dasha_B3 = digit_sum_once(month)
    dasha_B4 = digit_sum_once(dasha_B3)
    dasha_C3 = digit_sum_once(year)
    dasha_C4 = digit_sum_once(dasha_C3)
    dasha_A5 = dasha_A4 + dasha_B4 + dasha_C4
    dasha_A6 = digit_sum_once(dasha_A5)
    dasha_A7 = digit_sum_once(dasha_A6)
    destiny = dasha_A7

    # Digits that populate the natal grid (Grids sheet L3:S3)
    grid_digits = {
        "B1": B2 if B2 != 0 else None,
        "B2": C2 if C2 != 0 else None,
        "Root": I2 if I2 > 0 else None,
        "Destiny": destiny,
        "M1": B3 if B3 > 0 else None,
        "M2": C3 if C3 > 0 else None,
        "Y1": D4 if D4 > 0 else None,
        "Y2": E4 if E4 > 0 else None,
    }

    return {
        "root": root,
        "destiny": destiny,
        "grid_digits": grid_digits,
        "reduced_month": dasha_B4,
        "day_digits": {"B2": B2, "C2": C2, "D2": D2, "E2": E2, "G2": G2, "H2": H2, "I2": I2},
        "month_digits": {"B3": B3, "C3": C3, "D3": D3},
        "year_digits": {
            "B4": B4, "C4": C4str, "D4": D4, "E4": E4,
            "G4": G4, "H4": H4, "I4": I4, "J4": J4,
        },
        "destiny_chain": {"A5": A5, "H2": H2, "D3": D3, "J4": J4},
        # Dasha-sheet working, exposed so the report can show each step.
        "dasha_steps": {
            "day_sum": dasha_A3, "day_root": dasha_A4,
            "month_sum": dasha_B3, "month_root": dasha_B4,
            "year_sum": dasha_C3, "year_root": dasha_C4,
            "total": dasha_A5, "total_sum": dasha_A6, "destiny": dasha_A7,
        },
    }


# --------------------------------------------------------------------------- #
# Grids
# --------------------------------------------------------------------------- #
def build_natal_grid(grid_digits: dict) -> dict[int, str]:
    """Place each source digit in its Lo Shu cell; repeats concatenate ("11")."""
    all_digits = [d for d in grid_digits.values() if d is not None]
    grid = {i: "" for i in range(1, 10)}
    for d in all_digits:
        if 1 <= d <= 9:
            grid[d] += str(d)
    return grid


def build_yearly_grid(natal_grid: dict, maha_dasha: Optional[int], antar_dasha: Optional[int]) -> dict:
    """Natal grid plus the year's Maha Dasha and Antardasha numbers."""
    grid = dict(natal_grid)
    if maha_dasha and 1 <= maha_dasha <= 9:
        grid[maha_dasha] += str(maha_dasha)
    if antar_dasha and 1 <= antar_dasha <= 9:
        grid[antar_dasha] += str(antar_dasha)
    return grid


# --------------------------------------------------------------------------- #
# Maha Dasha
# --------------------------------------------------------------------------- #
def calc_dasha_periods(root: int, birth_date: datetime) -> list[dict]:
    """Life periods from birth: start at Root, cycle 1–9, each lasting its number in years."""
    periods = []
    num = root
    start_date = birth_date
    age = 0

    for _ in range(12):
        for _ in range(9):
            try:
                end_date = safe_date(
                    start_date.year + num,
                    start_date.month,
                    start_date.day,
                ) - timedelta(days=1)
            except Exception:
                break

            periods.append({
                "number": num,
                "start": start_date,
                "end": end_date,
                "start_age": age,
                "duration": num,
            })
            age += num
            start_date = end_date + timedelta(days=1)
            num = 1 if num + 1 > 9 else num + 1

    return periods


def find_maha_dasha(dasha_periods: list[dict], date: datetime) -> Optional[int]:
    """Number of the Maha Dasha running on ``date``."""
    for p in dasha_periods:
        if p["start"] <= date <= p["end"]:
            return p["number"]
    return None


# --------------------------------------------------------------------------- #
# Antardasha (one number per birthday year)
# --------------------------------------------------------------------------- #
def calc_antardasha(year: int, birth_day: int, birth_month: int, root: int, reduced_month: int) -> dict:
    """Year number = last two digits of year + Root + reduced month + birthday-weekday planet."""
    date = safe_date(year, birth_month, birth_day)
    weekday = date.weekday()           # Python: 0 = Monday
    js_weekday = (weekday + 1) % 7     # Sheet: 0 = Sunday
    day_name = DAY_NAMES[js_weekday]
    planet_number = WEEKDAY_PLANET[js_weekday]

    yy = int(str(year)[-2:])
    total = yy + root + reduced_month + planet_number
    P = digit_sum_once(total)
    Q = digit_sum_once(P)

    return {
        "year": year,
        "date": date,
        "day_name": day_name,
        "planet_number": planet_number,
        "yy": yy,
        "sum": total,
        "P": P,
        "antardasha_number": Q,
    }


# --------------------------------------------------------------------------- #
# Pratyantar Dasha (nine sub-periods inside a birthday year)
# --------------------------------------------------------------------------- #
def calc_pratyantar_dasha(antar_num: int, year_start: datetime, birth_day: int,
                          birth_month: int, review_year: int) -> list[dict]:
    """Sub-periods start at the year's Antardasha number; each lasts 8 × number days."""
    periods = []
    num = antar_num
    start_date = year_start
    year_end_date = safe_date(review_year + 1, birth_month, birth_day) - timedelta(days=1)

    for i in range(9):
        duration = PRATYANTAR_DAYS_PER_UNIT * num
        end_date = start_date + timedelta(days=duration)
        if i == 8:
            end_date = min(end_date, year_end_date)

        periods.append({
            "number": num,
            "start": start_date,
            "end": end_date,
            "planet": PLANETS[num],
        })

        start_date = end_date + timedelta(days=1)
        num = 1 if num + 1 > 9 else num + 1

    return periods


# --------------------------------------------------------------------------- #
# Full report
# --------------------------------------------------------------------------- #
def generate_full_report(day: int, month: int, year: int, today: Optional[datetime] = None) -> dict:
    """Run every calculation for a birth date and return the raw results.

    ``today`` fixes the reference date (defaults to now) so the output is
    reproducible in tests.
    """
    today = today or datetime.now()
    calc = calc_root_and_destiny(day, month, year)
    natal_grid = build_natal_grid(calc["grid_digits"])
    birth_date = safe_date(year, month, day)
    dasha_periods = calc_dasha_periods(calc["root"], birth_date)
    current_year = today.year

    antardasha_data = []
    for y in range(current_year - ANTARDASHA_YEARS_BEFORE, current_year + ANTARDASHA_YEARS_AFTER):
        try:
            antardasha_data.append(
                calc_antardasha(y, day, month, calc["root"], calc["reduced_month"])
            )
        except Exception:
            pass

    review_years = []
    for i in range(-REVIEW_YEARS_BEFORE, REVIEW_YEARS_AFTER):
        ry = current_year + i
        try:
            ry_bday = safe_date(ry, month, day)
            maha = find_maha_dasha(dasha_periods, ry_bday)
            ae = next((a for a in antardasha_data if a["year"] == ry), None)
            antar_num = ae["antardasha_number"] if ae else None
            y_grid = build_yearly_grid(natal_grid, maha, antar_num)
            prat = calc_pratyantar_dasha(antar_num, ry_bday, day, month, ry) if antar_num else []
            review_years.append({
                "year": ry,
                "maha_dasha": maha,
                "antar_dasha": antar_num,
                "grid": y_grid,
                "pratyantar": prat,
            })
        except Exception:
            pass

    return {
        "day": day,
        "month": month,
        "year": year,
        "birth_date": birth_date,
        "calc": calc,
        "natal_grid": natal_grid,
        "dasha_periods": dasha_periods[:MAHA_DASHA_PERIODS_SHOWN],
        "antardasha_data": antardasha_data,
        "review_years": review_years,
        "current_year": current_year,
    }
