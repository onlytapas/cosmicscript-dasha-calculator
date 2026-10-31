"""
Chaldean name numerology.

Letters carry the values 1 to 8 (Chaldean has no 9). The values of every
letter in the name are added to give the name total (the "compound" number),
which is then reduced digit by digit to the single name number. The total is
graded from a table of 1 to 100; a total above 100 is graded by the sum of its
digits, matching the reference calculator the numerologist uses.
"""

from __future__ import annotations

from numerology.engine import digit_sum_once

LETTER_VALUES: dict[str, int] = {
    "A": 1, "I": 1, "J": 1, "Q": 1, "Y": 1,
    "B": 2, "K": 2, "R": 2,
    "C": 3, "G": 3, "L": 3, "S": 3,
    "D": 4, "M": 4, "T": 4,
    "E": 5, "H": 5, "N": 5, "X": 5,
    "U": 6, "V": 6, "W": 6,
    "O": 7, "Z": 7,
    "F": 8, "P": 8,
}

# Letters grouped by value, in the order the traditional table lists them.
CHALDEAN_TABLE: dict[int, list[str]] = {
    1: ["A", "I", "J", "Q", "Y"],
    2: ["B", "K", "R"],
    3: ["C", "G", "L", "S"],
    4: ["D", "M", "T"],
    5: ["E", "H", "N", "X"],
    6: ["U", "V", "W"],
    7: ["O", "Z"],
    8: ["F", "P"],
}

MAX_GRADED_TOTAL = 100


def reduction_steps(total: int) -> list[dict]:
    """Successive digit sums until one digit remains, e.g. 32 -> [3 + 2 = 5]."""
    steps = []
    current = total
    while current > 9:
        result = digit_sum_once(current)
        steps.append({"expression": " + ".join(str(current)), "result": result})
        current = result
    return steps


def analyse_name(name: str) -> dict:
    """Letter values, word totals, the name total, its reduction and the graded total."""
    words = []
    for raw_word in name.upper().split():
        letters = [{"char": ch, "value": LETTER_VALUES[ch]} for ch in raw_word if ch in LETTER_VALUES]
        if letters:
            words.append({
                "text": raw_word,
                "letters": letters,
                "expression": " + ".join(str(l["value"]) for l in letters),
                "total": sum(l["value"] for l in letters),
            })

    total = sum(w["total"] for w in words)
    if total == 0:
        raise ValueError("The name must contain at least one letter from A to Z.")

    steps = reduction_steps(total)
    name_number = steps[-1]["result"] if steps else total
    graded_total = digit_sum_once(total) if total > MAX_GRADED_TOTAL else total

    return {
        "name": " ".join(w["text"] for w in words),
        "words": words,
        "letter_count": sum(len(w["letters"]) for w in words),
        "total": total,
        "total_expression": " + ".join(str(w["total"]) for w in words),
        "steps": steps,
        "name_number": name_number,
        "graded_total": graded_total,
    }
