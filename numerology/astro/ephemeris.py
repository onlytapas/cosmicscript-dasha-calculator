"""
Thin wrapper over the Swiss Ephemeris (pyswisseph).

All longitudes returned here are sidereal, Lahiri ayanamsa, in degrees 0–360.
Rahu is the mean lunar node; Ketu is opposite it.
"""

from __future__ import annotations

from pathlib import Path

import swisseph as swe

# Swiss Ephemeris data files for 1800–2399 (the same files the browser build uses).
EPHE_PATH = Path(__file__).with_name("ephe")
swe.set_ephe_path(str(EPHE_PATH))

AYANAMSA_MODES = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "true_chitra": swe.SIDM_TRUE_CITRA,
}
BODIES = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE,
}
FLAGS = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED


def set_ayanamsa(mode: str = "lahiri") -> None:
    swe.set_sid_mode(AYANAMSA_MODES.get(mode, swe.SIDM_LAHIRI))


def ayanamsa(jd_ut: float) -> float:
    return swe.get_ayanamsa_ut(jd_ut)


def planet_longitudes(jd_ut: float) -> dict[str, dict]:
    """Sidereal longitude and daily speed for each body; Ketu derived from Rahu."""
    out = {}
    for name, body in BODIES.items():
        lon, lat, dist, speed = swe.calc_ut(jd_ut, body, FLAGS)[0][:4]
        out[name] = {"longitude": lon % 360, "speed": speed, "retrograde": speed < 0}
    rahu = out["Rahu"]
    out["Ketu"] = {"longitude": (rahu["longitude"] + 180) % 360, "speed": rahu["speed"], "retrograde": rahu["retrograde"]}
    return out


def ascendant(jd_ut: float, latitude: float, longitude: float) -> float:
    """Sidereal ascendant (Lagna) in degrees."""
    cusps, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b"W", swe.FLG_SIDEREAL)
    return ascmc[0] % 360
