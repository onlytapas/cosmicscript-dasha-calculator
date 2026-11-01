"""Chaldean name numerology: engine, grades and the report model."""

from datetime import datetime

import pytest

from numerology import create_app
from numerology.compatibility import number_relation
from numerology.name_engine import LETTER_VALUES, analyse_name
from numerology.name_interpretations import COMPOUND_MEANINGS, GRADES, NAME_NUMBER_MEANINGS
from numerology.name_report import build_name_report, word_roles
from numerology.web.validation import parse_name, parse_optional_birth_date, parse_optional_name

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
    assert r["title"] == "Business Name Numerology Report" and r["system"] == "Chaldean numerology"
    assert r["total"] == 20 and r["name_number"] == 2 and r["planet"].name == "Moon (Chandra)"
    assert r["grade"]["label"] == "Acceptable" and r["compound_meaning"].startswith("The awakening")
    assert [(w["role"], w["total"], w["number"]) for w in r["words"]] == [("Word 1", 10, 1), ("Word 2", 10, 1)]
    assert r["birth"] is None and r["alignment"] is None and r["options"] == []
    assert [c["value"] for c in r["table"]] == list(range(1, 9))
    used = {l["char"] for col in r["table"] for l in col["letters"] if l["used"]}
    assert used == {"A", "S", "H", "R", "O"}


@pytest.mark.parametrize("count, owner, roles", [
    (1, "person", ["Name"]),
    (2, "person", ["First name", "Last name"]),
    (4, "person", ["First name", "Middle name", "Middle name", "Last name"]),
    (1, "business", ["Name"]),
    (3, "business", ["Word 1", "Word 2", "Word 3"]),
])
def test_word_roles(count, owner, roles):
    assert word_roles(count, owner) == roles


@pytest.mark.parametrize("base, other, relation", [
    (1, 2, "friendly"), (1, 5, "neutral"), (1, 4, "enemy"), (1, 1, "same"), (1, 7, "unlisted"),
    (9, 1, "friendly"), (9, 8, "enemy"), (4, 9, "neutral"), (8, 7, "enemy"),
])
def test_number_relation_reads_the_tables_from_the_base_number(base, other, relation):
    assert number_relation(base, other) == relation


def test_report_aligns_name_number_with_root_and_destiny():
    # 29 Jan 1990: Root 2, Destiny 4. ASHA RAO -> 20 -> 2.
    r = build_name_report("Asha Rao", "person", "", today=TODAY, birth=(29, 1, 1990), options=["Aasha Rao", "  "])
    assert r["birth"]["date"] == "29 January 1990" and r["birth"]["root"] == 2 and r["birth"]["destiny"] == 4
    assert r["birth"]["root_planet"].short_name == "Moon" and r["birth"]["destiny_planet"].short_name == "Rahu"
    assert r["alignment"]["root"]["key"] == "same" and r["alignment"]["destiny"]["key"] == "neutral"
    assert r["alignment"]["verdict"] == "neutral"
    assert r["alignment"]["summary"] == "Name number 2 is the same as the Root number 2 and neutral to the Destiny number 4."
    assert [w["role"] for w in r["words"]] == ["First name", "Last name"]

    assert len(r["options"]) == 1
    option = r["options"][0]
    assert option["name"] == "AASHA RAO" and option["total"] == 21 and option["name_number"] == 3
    assert option["grade"]["level"] == "very_good"
    assert option["alignment"]["root"]["key"] == "friendly" and option["alignment"]["destiny"]["key"] == "neutral"
    assert option["alignment"]["verdict"] == "neutral"


def test_challenging_name_recommends_a_correction():
    # 8 Jan 1990: Root 8, Destiny 1. RAVI KUMAR -> 25 -> 7, an enemy of 8.
    r = build_name_report("Ravi Kumar", "person", "", today=TODAY, birth=(8, 1, 1990))
    assert r["alignment"]["root"]["key"] == "enemy" and r["alignment"]["verdict"] == "enemy"
    assert r["alignment"]["summary"].endswith("A name correction is worth considering.")


def test_optional_fields_validation():
    assert parse_optional_birth_date(None, None, None) is None
    assert parse_optional_birth_date(29, 1, 1990).year == 1990
    with pytest.raises(ValueError, match="day, month and year"):
        parse_optional_birth_date(29, None, 1990)
    assert parse_optional_name("  ") == "" and parse_optional_name(" Aasha  Rao ") == "Aasha Rao"
    with pytest.raises(ValueError, match="at least one letter"):
        parse_optional_name("123")


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
    assert "Personal Name Numerology Report" in html and "ASHA RAO" in html and "The awakening" in html
    assert "Name and birth alignment" in html and 'class="sec pro-only"' in html
    assert 'id="viewToggle"' in html and "client-view" not in html


def test_name_report_route_with_birth_options_and_client_view(client):
    url = "/name-report?name=Asha%20Rao&day=29&month=1&year=1990&option1=Aasha%20Rao&option2=&view=client"
    html = client.get(url).get_data(as_text=True)
    assert '<body class="report client-view">' in html
    assert "29 January 1990" in html and "Compatibility analysis" in html and "Option 1" in html and "AASHA RAO" in html
    assert "Name number 2 is the same as the Root number 2" in html


def test_name_report_route_rejects_partial_birth_date(client):
    response = client.get("/name-report?name=Asha&day=29&year=1990")
    assert response.status_code == 302 and "tab=name" in response.headers["Location"]


def test_home_shows_name_tab_errors(client):
    response = client.get("/name-report?name=")
    assert response.status_code == 302 and "tab=name" in response.headers["Location"]
    html = client.get("/?tab=name&error=Please+enter+a+name").get_data(as_text=True)
    assert 'value="name" checked' in html and "Please enter a name" in html


def test_name_report_has_suggested_spellings_box(client):
    html = client.get("/name-report?name=Asha%20Rao&day=29&month=1&year=1990").get_data(as_text=True)
    assert "data-option-form" in html and 'class="sec pro-only"' in html
    html = client.get("/name-report?name=Asha%20Rao&day=29&month=1&year=1990&option1=Aasha%20Rao").get_data(as_text=True)
    assert 'value="AASHA RAO"' in html and "Option 1" in html
