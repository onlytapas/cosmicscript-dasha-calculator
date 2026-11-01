"""
Turns a Chaldean name analysis into the view model for ``name_report.html``.

The report follows the numerologist's client format: client details, the name
matrix (one block per word), the current-name analysis, alignment of the name
number with the Root and Destiny numbers from the date of birth, and the
recommended name options. The letter-by-letter working is included for the
practitioner's view and hidden from the client's.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from numerology import name_interpretations as text
from numerology.compatibility import RELATIONS, number_relation
from numerology.constants import PLANETS
from numerology.engine import calc_root_and_destiny, digit_sum_to_single, safe_date
from numerology.name_engine import CHALDEAN_TABLE, analyse_name
from numerology.report import format_date_long

OWNER_TYPES = {"person": "a person", "business": "a business"}
SYSTEM_NAME = "Chaldean numerology"
MAX_OPTIONS = 2


def word_roles(count: int, owner: str) -> list[str]:
    """Labels for the words of a name: First / Middle / Last for a person, Word 1.. for a business."""
    if owner == "business":
        return ["Name" if count == 1 else f"Word {i + 1}" for i in range(count)]
    if count == 1:
        return ["Name"]
    return ["First name"] + ["Middle name"] * (count - 2) + ["Last name"]


def _grade(graded_total: int) -> dict:
    grade = text.GRADES[graded_total]
    level = text.GRADE_LEVELS[grade["level"]]
    return {
        "level": grade["level"],
        "label": level["label"],
        "verdict": level["verdict"],
        "advice": level["advice"],
        "company": grade.get("company", False),
    }


def _compound_meaning(total: int, name_number: int) -> str:
    if total <= 52:
        return text.COMPOUND_MEANINGS[total]
    return (f"Totals above 52 take their character from the single digit they reduce to, "
            f"here {name_number}. The grade comes from the numerologist's table of totals.")


def _relation(base_label: str, base: int, name_number: int) -> dict:
    key = number_relation(base, name_number)
    rel = RELATIONS[key]
    return {
        "key": key,
        "label": rel["label"],
        "phrase": rel["phrase"],
        "base_label": base_label,
        "base": base,
        "text": f"Name number {name_number} {rel['verb']} {base_label} {base}.",
    }


def _alignment(name_number: int, root: int, destiny: int) -> dict:
    """The name number seen from the Root and the Destiny, with a one-line summary."""
    with_root = _relation("Root number", root, name_number)
    with_destiny = _relation("Destiny number", destiny, name_number)
    keys = {with_root["key"], with_destiny["key"]}
    verdict = "enemy" if "enemy" in keys else "friendly" if keys == {"friendly"} else "neutral"
    summary = (f"Name number {name_number} is {with_root['phrase']} the Root number {root} "
               f"and {with_destiny['phrase']} the Destiny number {destiny}.")
    if verdict == "enemy":
        summary += " A name correction is worth considering."
    return {"root": with_root, "destiny": with_destiny, "verdict": verdict, "summary": summary}


def _name_summary(name: str, owner: str, birth: Optional[dict]) -> dict:
    """Everything the report shows about one spelling (the current name or an option)."""
    a = analyse_name(name)
    roles = word_roles(len(a["words"]), owner)
    summary = {
        "name": a["name"],
        "words": [dict(w, role=roles[i], number=digit_sum_to_single(w["total"])) for i, w in enumerate(a["words"])],
        "letter_count": a["letter_count"],
        "total": a["total"],
        "total_expression": a["total_expression"],
        "steps": a["steps"],
        "name_number": a["name_number"],
        "planet": PLANETS[a["name_number"]],
        "graded_total": a["graded_total"],
        "graded_by_digits": a["graded_total"] != a["total"],
        "grade": _grade(a["graded_total"]),
        "compound_meaning": _compound_meaning(a["total"], a["name_number"]),
        "digit_meaning": text.NAME_NUMBER_MEANINGS[a["name_number"]],
        "alignment": None,
    }
    if birth:
        summary["alignment"] = _alignment(a["name_number"], birth["root"], birth["destiny"])
    return summary


def _birth_numbers(day: int, month: int, year: int) -> dict:
    calc = calc_root_and_destiny(day, month, year)
    return {
        "date": format_date_long(safe_date(year, month, day)),
        "root": calc["root"],
        "destiny": calc["destiny"],
        "root_planet": PLANETS[calc["root"]],
        "destiny_planet": PLANETS[calc["destiny"]],
    }


def build_name_report(name: str, owner: str = "person", client_name: str = "",
                      today: Optional[datetime] = None, birth: Optional[tuple[int, int, int]] = None,
                      options: Optional[list[str]] = None) -> dict:
    """``birth`` is (day, month, year); ``options`` are the recommended spellings, if any."""
    today = today or datetime.now()
    owner = owner if owner in OWNER_TYPES else "person"
    birth_numbers = _birth_numbers(*birth) if birth else None
    current = _name_summary(name, owner, birth_numbers)
    used = {l["char"] for w in current["words"] for l in w["letters"]}

    return {
        **current,
        "owner": owner,
        "owner_label": OWNER_TYPES[owner],
        "title": "Business Name Numerology Report" if owner == "business" else "Personal Name Numerology Report",
        "system": SYSTEM_NAME,
        "client_name": client_name.strip(),
        "report_date": format_date_long(today),
        "report_year": today.year,
        "birth": birth_numbers,
        "options": [_name_summary(o, owner, birth_numbers) for o in (options or [])[:MAX_OPTIONS] if o.strip()],
        "table": [{"value": v, "letters": [{"char": c, "used": c in used} for c in letters]}
                  for v, letters in CHALDEAN_TABLE.items()],
    }
