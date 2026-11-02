"""Bundled place list (from GeoNames) and a simple search over it.

GeoNames spells many Indian towns with accents (Kānchrāpāra, Alīgarh); they are folded to
plain letters so the names match what people type.
"""

from __future__ import annotations

import json
import math
import unicodedata
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

PLACES_FILE = Path(__file__).with_name("places.json")


@dataclass(frozen=True)
class Place:
    name: str
    region: str
    country: str
    latitude: float
    longitude: float
    timezone: str

    @property
    def label(self) -> str:
        parts = [self.name] + ([self.region] if self.region else []) + [self.country]
        return ", ".join(parts)


def fold(text: str) -> str:
    """Drop accents: 'Kānchrāpāra' -> 'Kanchrapara'."""
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


@lru_cache(maxsize=1)
def all_places() -> list[Place]:
    return [Place(fold(name), fold(region), *rest) for name, region, *rest in json.loads(PLACES_FILE.read_text())]


def search_places(query: str, limit: int = 12) -> list[Place]:
    q = fold(query).split(",")[0].strip().lower()
    if not q:
        return []
    starts = [p for p in all_places() if p.name.lower().startswith(q)]
    contains = [p for p in all_places() if q in p.name.lower() and p not in starts]
    return (starts + contains)[:limit]


def find_place(label: str) -> Place | None:
    label = fold(label)
    for p in all_places():
        if p.label == label:
            return p
    return None


def place_from_coordinates(label: str, latitude, longitude, timezone: str) -> Place | None:
    """A place found by the online search, which sends its coordinates and time zone along with the label."""
    try:
        lat, lon, tz = float(latitude), float(longitude), str(timezone)
        ZoneInfo(tz)
    except (TypeError, ValueError, KeyError, OSError):
        return None
    if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    parts = [x.strip() for x in fold(label).split(",") if x.strip()]
    if not parts:
        return None
    country = parts[-1] if len(parts) > 1 else ""
    return Place(parts[0], ", ".join(parts[1:-1]), country, round(lat, 4), round(lon, 4), tz)
