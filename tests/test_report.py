"""Tests for the view model and the web routes."""

from datetime import datetime

import pytest

from numerology import create_app
from numerology.report import build_report, reduction_steps
from numerology.web.validation import parse_birth_date

TODAY = datetime(2026, 10, 31)


def test_reduction_steps_show_only_real_additions():
    assert reduction_steps(29, [11, 2]) == [
        {"expression": "2 + 9", "result": 11},
        {"expression": "1 + 1", "result": 2},
    ]
    assert reduction_steps(5, [5, 5]) == []


def test_build_report_core_numbers_and_explanations():
    r = build_report(29, 1, 1990, "  Asha Rao ", today=TODAY)
    assert r["client_name"] == "Asha Rao"
    assert r["root"]["number"] == 2 and r["destiny"]["number"] == 4
    assert r["dob"] == "29 January 1990" and r["birth_weekday"] == "Monday" and r["age"] == 36
    assert r["steps"]["destiny"]["parts"] == [2, 1, 10]
    assert [s["title"] for s in r["root"]["sections"]][:2] == ["Personality & Core Traits", "Strengths"]
    assert r["grid"]["present"] and r["grid"]["missing"]
    assert r["now"]["maha"]["is_current"] and r["now"]["antar"]["year"] == 2026
    assert len(r["maha"]["periods"]) == 27 and len(r["years"]) == 9
    assert r["maha"]["timeline"][0]["start_age"] == 0 and r["maha"]["timeline"][-1]["end_age"] >= 89
    for row in r["maha"]["timeline"]:
        assert abs(sum(p["width"] for p in row["segments"]) - 100) < 0.5


def test_now_markers_follow_the_birthday_year():
    r = build_report(28, 12, 1995, "", today=TODAY)
    assert r["antar"]["current"]["year"] == 2025
    assert [y["year"] for y in r["years"] if y["is_current"]] == [2025]
    assert r["now"]["pratyantar"] is not None and r["now"]["pratyantar"]["is_active"]


def test_parse_birth_date_messages():
    assert parse_birth_date(29, 2, 2004).day == 29
    with pytest.raises(ValueError, match="does not exist"):
        parse_birth_date(31, 4, 2000)
    with pytest.raises(ValueError, match="Year"):
        parse_birth_date(1, 1, 1850)
    with pytest.raises(ValueError, match="Month"):
        parse_birth_date(1, 13, 2000)
    with pytest.raises(ValueError, match="enter"):
        parse_birth_date(None, 1, 2000)


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_home_page_renders(client):
    html = client.get("/").get_data(as_text=True)
    for label in ("Complete Reading", "Numerology", "Name Numerology", "Astrology · Kundli", "First name", "Middle name", "Last name"):
        assert label in html
    assert 'value="complete" checked' in html and "Suggested name" not in html


@pytest.mark.parametrize("tab, reading", [("dasha", "numerology"), ("numerology", "numerology"), ("name", "name"), ("astro", "astro"), ("x", "complete")])
def test_home_preselects_the_reading(client, tab, reading):
    html = client.get(f"/?tab={tab}").get_data(as_text=True)
    assert f'value="{reading}" checked' in html


def test_report_page_renders(client):
    html = client.get("/report?day=29&month=1&year=1990&name=Asha").get_data(as_text=True)
    assert "Vedic Numerology Report" in html
    assert "prepared for <strong>Asha</strong>" in html
    assert "2 + 9" in html and "Maha Dasha" in html


def test_invalid_date_redirects_with_message(client):
    response = client.get("/report?day=31&month=4&year=2000")
    assert response.status_code == 302 and "tab=numerology" in response.headers["Location"]
    assert "does+not+exist" in response.headers["Location"] or "does%20not%20exist" in response.headers["Location"]
