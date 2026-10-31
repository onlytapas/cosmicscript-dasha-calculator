"""Chaldean name numerology: engine, grades and the report model."""

from datetime import datetime

import pytest

from numerology import create_app
from numerology.name_engine import LETTER_VALUES, analyse_name
from numerology.name_interpretations import COMPOUND_MEANINGS, GRADES, NAME_NUMBER_MEANINGS
from numerology.name_report import build_name_report
from numerology.web.validation import parse_name

TODAY = datetime(2026, 10, 31)


def test_letter_table_is_chaldean():
    assert LETTER_VALUES["A"] == 1 and LETTER_VALUES["F"] == 8 and LETTER_VALUES["Y"] == 1
    assert 9 not in LETTER_VALUES.values()
    assert sorted(LETTER_VALUES) == [chr(c) for c in range(ord("A"), ord("Z") + 1)]


@pytest.mark.parametrize("name, total, number", [
    ("RAM", 7, 7),                 # R2 A1 M4
    ("Asha Rao", 15, 6),           # A1 S3 H5 A1 = 10, R2 A1 O7 = 10 ... see below
    ("abc", 6, 6),
    ("Z", 7, 7),
])
def test_totals_and_reduction(name, total, number):
    a = analyse_name(name)
    if name == "Asha Rao":
        total, number = 20, 2
    assert a["total"] == total and a["name_number"] == number


def test_words_and_non_letters_are_handled():
    a = analyse_name("  Mr. O'Brien-Smith 2nd ")
    assert [w["text"] for w in a["words"]] == ["MR.", "O'BRIEN-SMITH", "2ND"]
    assert a["words"][2]["letters"] == [{"char": "N", "value": 5}, {"char": "D", "value": 4}]
    assert a["name"] == "MR. O'BRIEN-SMITH 2ND"


def test_reduction_steps_are_listed():
    a = analyse_name("Cosmicscript Numerology")
    assert a["total"] == sum(LETTER_VALUES[c] for c in "COSMICSCRIPTNUMEROLOGY")
    expected = a["total"]
    for step in a["steps"]:
        assert step["result"] == sum(int(d) for d in str(expected))
        expected = step["result"]
    assert a["name_number"] == expected <= 9


def test_totals_above_100_are_graded_by_digit_sum():
    a = analyse_name("P" * 13)      # 13 x 8 = 104
    assert a["total"] == 104 and a["graded_total"] == 5


def test_grade_table_covers_1_to_100_with_known_levels():
    assert sorted(GRADES) == list(range(1, 101))
    assert GRADES[23]["level"] == "very_good" and GRADES[37]["level"] == "excellent"
    assert GRADES[18]["level"] == "avoid" and GRADES[7]["company"] is True
    assert GRADES[9]["level"] == "caution" and GRADES[71]["level"] == "caution"
    assert set(COMPOUND_MEANINGS) == set(range(1, 53)) and set(NAME_NUMBER_MEANINGS) == set(range(1, 10))


def test_build_name_report_shape():
    r = build_name_report("Asha Rao", "business", "  Asha ", today=TODAY)
    assert r["name"] == "ASHA RAO" and r["client_name"] == "Asha" and r["owner_label"] == "a business"
    assert r["total"] == 20 and r["name_number"] == 2 and r["planet"].name == "Moon (Chandra)"
    assert r["grade"]["label"] == "Acceptable" and r["compound_meaning"].startswith("The awakening")
    assert [c["value"] for c in r["table"]] == list(range(1, 9))
    used = {l["char"] for col in r["table"] for l in col["letters"] if l["used"]}
    assert used == {"A", "S", "H", "R", "O"}


def test_name_validation_messages():
    assert parse_name("  Asha   Rao ") == "Asha Rao"
    with pytest.raises(ValueError, match="enter a name"):
        parse_name("   ")
    with pytest.raises(ValueError, match="at least one letter"):
        parse_name("123 !!")
    with pytest.raises(ValueError, match="80"):
        parse_name("A" * 81)


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_name_report_route(client):
    html = client.get("/name-report?name=Asha%20Rao&owner=person").get_data(as_text=True)
    assert "Name Numerology Report" in html and "ASHA RAO" in html and "The awakening" in html


def test_home_shows_name_tab_errors(client):
    response = client.get("/name-report?name=")
    assert response.status_code == 302 and "tab=name" in response.headers["Location"]
    html = client.get("/?tab=name&error=Please+enter+a+name").get_data(as_text=True)
    assert 'data-active-tab="name"' in html and "Please enter a name" in html
