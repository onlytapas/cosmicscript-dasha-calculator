"""
Regression tests for the calculation engine.

The fixture was generated from the original single-file calculator before the
code was restructured. These tests guarantee the restructuring did not change
a single number or date.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path

import pytest

from numerology import engine
from numerology.constants import Planet

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "engine_snapshot.json").read_text())
TODAY = datetime.fromisoformat(FIXTURE["today"])


def normalise(obj):
    """Match the shape the original code produced (ISO dates, planet as name/symbol)."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, Planet):
        return {"name": obj.name, "symbol": obj.symbol}
    if isinstance(obj, dict):
        return {str(k): normalise(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [normalise(v) for v in obj]
    return obj


def report_for(key: str) -> dict:
    day, month, year = (int(part) for part in key.split("-"))
    report = normalise(engine.generate_full_report(day, month, year, today=TODAY))
    report["calc"].pop("dasha_steps")  # display-only addition, not in the original
    return report


@pytest.mark.parametrize("key", sorted(FIXTURE["full"]))
def test_full_report_matches_original(key):
    assert report_for(key) == FIXTURE["full"][key]


@pytest.mark.parametrize("key", sorted(FIXTURE["digests"]))
def test_report_digest_matches_original(key):
    digest = hashlib.sha256(json.dumps(report_for(key), sort_keys=True).encode()).hexdigest()
    assert digest == FIXTURE["digests"][key]


def test_digit_helpers():
    assert engine.digit_sum_once(1990) == 19
    assert engine.digit_sum_once(19) == 10
    assert engine.digit_sum_to_single(1990) == 1


def test_safe_date_clamps_invalid_days():
    assert engine.safe_date(2023, 2, 29) == datetime(2023, 2, 28)
    assert engine.safe_date(2023, 4, 31) == datetime(2023, 4, 30)
    assert engine.safe_date(2024, 2, 29) == datetime(2024, 2, 29)


def test_dasha_steps_are_consistent_with_results():
    calc = engine.calc_root_and_destiny(29, 1, 1990)
    steps = calc["dasha_steps"]
    assert steps["day_root"] == calc["root"] == 2
    assert steps["destiny"] == calc["destiny"] == 4
    assert steps["total"] == steps["day_root"] + steps["month_root"] + steps["year_root"]
