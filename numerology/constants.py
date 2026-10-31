"""Static lookup tables shared by the engine and the report."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Planet:
    """A ruling planet attached to a number from 1 to 9."""

    number: int
    name: str
    short_name: str
    symbol: str
    colour: str
    keywords: str


PLANETS: dict[int, Planet] = {
    1: Planet(1, "Sun (Surya)", "Sun", "☉", "#F2C14E", "Leadership, authority, originality"),
    2: Planet(2, "Moon (Chandra)", "Moon", "☽", "#B9C3D6", "Emotion, intuition, nurturing"),
    3: Planet(3, "Jupiter (Guru)", "Jupiter", "♃", "#F39C3B", "Wisdom, expansion, teaching"),
    4: Planet(4, "Rahu", "Rahu", "☊", "#8F80FF", "Ambition, unconventionality, change"),
    5: Planet(5, "Mercury (Budh)", "Mercury", "☿", "#4CCB7A", "Communication, commerce, intellect"),
    6: Planet(6, "Venus (Shukra)", "Venus", "♀", "#F26FB0", "Love, beauty, comfort"),
    7: Planet(7, "Ketu", "Ketu", "☋", "#B583F0", "Spirituality, detachment, insight"),
    8: Planet(8, "Saturn (Shani)", "Saturn", "♄", "#5BA3E0", "Discipline, patience, karma"),
    9: Planet(9, "Mars (Mangal)", "Mars", "♂", "#F05A4F", "Energy, courage, action"),
}

# Planet number ruling each weekday, indexed with Sunday = 0.
WEEKDAY_PLANET: dict[int, int] = {0: 1, 1: 2, 2: 9, 3: 5, 4: 3, 5: 6, 6: 8}

DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

MONTH_NAMES_SHORT = [m[:3] for m in MONTH_NAMES]

# Lo Shu grid positions, read row by row.
GRID_LAYOUT: list[list[int]] = [[3, 1, 9], [6, 7, 5], [2, 8, 4]]

# How many Maha Dasha periods the report lists (three full cycles of 1–9).
MAHA_DASHA_PERIODS_SHOWN = 27

# Antardasha table spans these offsets around the current year.
ANTARDASHA_YEARS_BEFORE = 5
ANTARDASHA_YEARS_AFTER = 15

# Yearly review cards span these offsets around the current year.
REVIEW_YEARS_BEFORE = 1
REVIEW_YEARS_AFTER = 8

# Each Pratyantar sub-period lasts this many days multiplied by its number.
PRATYANTAR_DAYS_PER_UNIT = 8
