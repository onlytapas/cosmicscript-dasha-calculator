"""Turns a Chaldean name analysis into the view model for ``name_report.html``."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from numerology import name_interpretations as text
from numerology.constants import PLANETS
from numerology.name_engine import CHALDEAN_TABLE, analyse_name
from numerology.report import format_date_long

OWNER_TYPES = {"person": "a person", "business": "a business"}


def build_name_report(name: str, owner: str = "person", client_name: str = "",
                      today: Optional[datetime] = None) -> dict:
    today = today or datetime.now()
    owner = owner if owner in OWNER_TYPES else "person"
    a = analyse_name(name)
    grade = text.GRADES[a["graded_total"]]
    level = text.GRADE_LEVELS[grade["level"]]
    used = {l["char"] for w in a["words"] for l in w["letters"]}

    if a["total"] <= 52:
        compound = text.COMPOUND_MEANINGS[a["total"]]
    else:
        compound = (f"Totals above 52 take their character from the single digit they reduce to, "
                    f"here {a['name_number']}. The grade comes from the numerologist's table of totals.")

    return {
        "name": a["name"],
        "owner": owner,
        "owner_label": OWNER_TYPES[owner],
        "client_name": client_name.strip(),
        "report_date": format_date_long(today),
        "report_year": today.year,
        "words": a["words"],
        "letter_count": a["letter_count"],
        "total": a["total"],
        "total_expression": a["total_expression"],
        "steps": a["steps"],
        "name_number": a["name_number"],
        "planet": PLANETS[a["name_number"]],
        "graded_total": a["graded_total"],
        "graded_by_digits": a["graded_total"] != a["total"],
        "grade": {
            "level": grade["level"],
            "label": level["label"],
            "verdict": level["verdict"],
            "advice": level["advice"],
            "company": grade.get("company", False),
        },
        "compound_meaning": compound,
        "digit_meaning": text.NAME_NUMBER_MEANINGS[a["name_number"]],
        "table": [{"value": v, "letters": [{"char": c, "used": c in used} for c in letters]}
                  for v, letters in CHALDEAN_TABLE.items()],
    }
