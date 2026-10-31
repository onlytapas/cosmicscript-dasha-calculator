"""Validation of the birth-date form."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Optional

MIN_YEAR = 1900
MAX_YEAR = 2099


@dataclass(frozen=True)
class BirthDate:
    day: int
    month: int
    year: int


def parse_birth_date(day: Optional[int], month: Optional[int], year: Optional[int]) -> BirthDate:
    """Return a validated BirthDate or raise ``ValueError`` with a user-facing message."""
    if day is None or month is None or year is None:
        raise ValueError("Please enter the day, month and year of birth.")
    if not 1 <= month <= 12:
        raise ValueError("Month must be between 1 and 12.")
    if not MIN_YEAR <= year <= MAX_YEAR:
        raise ValueError(f"Year must be between {MIN_YEAR} and {MAX_YEAR}.")
    try:
        date(year, month, day)
    except ValueError:
        raise ValueError("That day does not exist in the chosen month.") from None
    return BirthDate(day, month, year)


MAX_NAME_LENGTH = 80


def parse_name(name: Optional[str]) -> str:
    """Return a cleaned name for Chaldean analysis or raise ``ValueError``."""
    cleaned = " ".join((name or "").split())
    if not cleaned:
        raise ValueError("Please enter a name to analyse.")
    if len(cleaned) > MAX_NAME_LENGTH:
        raise ValueError(f"The name must be {MAX_NAME_LENGTH} characters or fewer.")
    if not any(ch.isascii() and ch.isalpha() for ch in cleaned):
        raise ValueError("The name must contain at least one letter from A to Z.")
    return cleaned
