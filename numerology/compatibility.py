"""
How one number sits with another, from the friendly / neutral / enemy tables.

The tables in ``interpretations`` are read from the point of view of the
*base* number (a Root or Destiny number): ``FRIENDLY_NUMBERS[base]`` lists the
numbers that are friendly to it, and so on. Nothing is inferred beyond what
the tables say: a number the table does not mention is reported as unlisted.
"""

from __future__ import annotations

from numerology import interpretations as text

# ``verb`` completes "Name number 5 ... Root number 1"; ``phrase`` completes "5 is ... the Root number 1".
RELATIONS = {
    "friendly": {"label": "Friendly", "verb": "is a friendly number for", "phrase": "friendly to"},
    "neutral": {"label": "Neutral", "verb": "is neutral towards", "phrase": "neutral to"},
    "enemy": {"label": "Challenging", "verb": "is a challenging (enemy) number for", "phrase": "challenging to"},
    "same": {"label": "Same number", "verb": "is the same number as", "phrase": "the same as"},
    "unlisted": {"label": "Not listed", "verb": "is not listed as friendly, neutral or challenging for",
                 "phrase": "not classified against"},
}

# Checked in this order; a number listed under more than one heading takes the first match.
_TABLES = (("friendly", text.FRIENDLY_NUMBERS), ("enemy", text.ENEMY_NUMBERS), ("neutral", text.NEUTRAL_NUMBERS))


def listed_numbers(table_entry: str) -> list[int]:
    """'2, 3, 9' -> [2, 3, 9]"""
    return [int(x) for x in table_entry.split(",") if x.strip()]


def number_relation(base: int, other: int) -> str:
    """'friendly' | 'neutral' | 'enemy' | 'same' | 'unlisted' for ``other`` seen from ``base``."""
    if base == other:
        return "same"
    for key, table in _TABLES:
        if other in listed_numbers(table[base]):
            return key
    return "unlisted"
