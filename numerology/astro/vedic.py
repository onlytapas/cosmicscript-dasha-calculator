"""
Vedic chart arithmetic on sidereal longitudes: signs, nakshatras, navamsa,
whole-sign houses, panchang at birth and the Vimshottari Dasha tree.

Everything here is pure arithmetic on numbers the ephemeris already produced,
so it ports one-to-one to the browser build.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from numerology.astro.constants import (
    DASHA_LORDS, DASHA_TOTAL_YEARS, DASHA_YEAR_DAYS, DASHA_YEARS, KARANA_CYCLE, KARANA_FIXED,
    NAKSHATRA_SPAN, NAKSHATRAS, NAVAMSA_SPAN, SIGNS, TITHI_NAMES, YOGA_NAMES,
)


# --------------------------------------------------------------------------- #
# Position helpers
# --------------------------------------------------------------------------- #
def dms(degrees: float) -> dict:
    """Degrees within a sign as d, m, s and a formatted string."""
    total = round(degrees * 3600)
    d, rem = divmod(total, 3600)
    m, s = divmod(rem, 60)
    return {"d": d, "m": m, "s": s, "text": f"{d}°{m:02d}'{s:02d}\""}


def describe_longitude(lon: float) -> dict:
    """Sign, degrees in sign, nakshatra, pada and navamsa sign for a sidereal longitude."""
    lon %= 360
    sign_index = int(lon // 30)
    in_sign = lon - sign_index * 30
    nak_index = int(lon // NAKSHATRA_SPAN)
    in_nak = lon - nak_index * NAKSHATRA_SPAN
    pada = int(in_nak // (NAKSHATRA_SPAN / 4)) + 1
    navamsa_index = int(lon // NAVAMSA_SPAN) % 12
    return {
        "longitude": lon,
        "sign": SIGNS[sign_index].name,
        "sign_index": sign_index,
        "sign_lord": SIGNS[sign_index].lord,
        "degrees": dms(in_sign),
        "nakshatra": NAKSHATRAS[nak_index],
        "nakshatra_index": nak_index,
        "nakshatra_lord": DASHA_LORDS[nak_index % 9],
        "pada": pada,
        "navamsa_sign": SIGNS[navamsa_index].name,
        "navamsa_index": navamsa_index,
    }


def house_from(sign_index: int, lagna_sign_index: int) -> int:
    """Whole-sign house number (1–12) of a sign counted from the Lagna sign."""
    return (sign_index - lagna_sign_index) % 12 + 1


# --------------------------------------------------------------------------- #
# Panchang
# --------------------------------------------------------------------------- #
def panchang(sun_lon: float, moon_lon: float, local_weekday: int) -> dict:
    """Tithi, yoga, karana and vara from the Sun and Moon longitudes.

    ``local_weekday`` is 0 for Sunday. The vara is taken from the civil date;
    strictly it runs sunrise to sunrise, so a birth before sunrise belongs to
    the previous vara.
    """
    elongation = (moon_lon - sun_lon) % 360
    tithi_index = int(elongation // 12)                   # 0..29
    paksha = "Shukla" if tithi_index < 15 else "Krishna"
    within = tithi_index % 15
    if tithi_index == 14:
        tithi_name = "Purnima"
    elif tithi_index == 29:
        tithi_name = "Amavasya"
    else:
        tithi_name = TITHI_NAMES[within]
    yoga_index = int(((sun_lon + moon_lon) % 360) // NAKSHATRA_SPAN)
    karana_index = int(elongation // 6)                   # 0..59
    karana = KARANA_FIXED.get(karana_index) or KARANA_CYCLE[(karana_index - 1) % 7]
    from numerology.astro.constants import WEEKDAY_LORDS, WEEKDAY_NAMES
    return {
        "tithi": f"{paksha} {tithi_name}",
        "tithi_number": tithi_index + 1,
        "paksha": paksha,
        "yoga": YOGA_NAMES[yoga_index],
        "karana": karana,
        "vara": WEEKDAY_NAMES[local_weekday],
        "vara_lord": WEEKDAY_LORDS[local_weekday],
    }


# --------------------------------------------------------------------------- #
# Vimshottari Dasha
# --------------------------------------------------------------------------- #
def dasha_sequence(start_lord: str) -> list[str]:
    i = DASHA_LORDS.index(start_lord)
    return DASHA_LORDS[i:] + DASHA_LORDS[:i]


def vimshottari(moon_lon: float, birth_utc: datetime, levels: int = 3) -> dict:
    """Maha, Antar and Pratyantar dashas from the Moon's nakshatra at birth.

    The first Mahadasha is back-dated so that the portion already elapsed at
    birth (the balance) is shown as part of it, which is how most software
    presents it.
    """
    nak_index = int(moon_lon // NAKSHATRA_SPAN)
    fraction_elapsed = (moon_lon - nak_index * NAKSHATRA_SPAN) / NAKSHATRA_SPAN
    first_lord = DASHA_LORDS[nak_index % 9]
    first_years = DASHA_YEARS[first_lord]
    elapsed_days = fraction_elapsed * first_years * DASHA_YEAR_DAYS
    balance_days = first_years * DASHA_YEAR_DAYS - elapsed_days
    start = birth_utc - timedelta(days=elapsed_days)

    def periods(parent_lord: str, start_at: datetime, parent_days: float, depth: int) -> list[dict]:
        out = []
        t = start_at
        for lord in dasha_sequence(parent_lord):
            days = parent_days * DASHA_YEARS[lord] / DASHA_TOTAL_YEARS
            end = t + timedelta(days=days)
            item = {"lord": lord, "start": t, "end": end, "days": days}
            if depth < levels:
                item["sub"] = periods(lord, t, days, depth + 1)
            out.append(item)
            t = end
        return out

    mahas = []
    t = start
    for lord in dasha_sequence(first_lord):
        days = DASHA_YEARS[lord] * DASHA_YEAR_DAYS
        end = t + timedelta(days=days)
        item = {"lord": lord, "start": t, "end": end, "days": days, "years": DASHA_YEARS[lord]}
        if levels >= 2:
            item["sub"] = periods(lord, t, days, 2)
        mahas.append(item)
        t = end

    return {
        "nakshatra": NAKSHATRAS[nak_index],
        "nakshatra_lord": first_lord,
        "fraction_elapsed": fraction_elapsed,
        "balance_days": balance_days,
        "balance_years": balance_days / DASHA_YEAR_DAYS,
        "mahadashas": mahas,
    }


def running_periods(mahas: list[dict], at: datetime) -> list[dict]:
    """The chain of periods (maha, antar, pratyantar) containing ``at``."""
    chain = []
    level = mahas
    while level:
        current = next((p for p in level if p["start"] <= at < p["end"]), None)
        if current is None:
            break
        chain.append(current)
        level = current.get("sub", [])
    return chain
