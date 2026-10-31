"""Bundled place list (from GeoNames) and a simple search over it."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

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


@lru_cache(maxsize=1)
def all_places() -> list[Place]:
    return [Place(*row) for row in json.loads(PLACES_FILE.read_text())]


def search_places(query: str, limit: int = 12) -> list[Place]:
    q = query.strip().lower()
    if not q:
        return []
    starts = [p for p in all_places() if p.name.lower().startswith(q)]
    contains = [p for p in all_places() if q in p.name.lower() and p not in starts]
    return (starts + contains)[:limit]


def find_place(label: str) -> Place | None:
    for p in all_places():
        if p.label == label:
            return p
    return None
