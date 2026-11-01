"""The Complete Reading combines the three reports without changing any of them."""

from datetime import datetime

import pytest

from numerology import create_app
from numerology.astro.places import find_place
from numerology.astro.report import build_astro_report
from numerology.complete_report import build_complete_report
from numerology.name_report import build_name_report
from numerology.report import build_report

TODAY = datetime(2026, 10, 31)
KOLKATA = "Kolkata, West Bengal, IN"


def test_parts_equal_the_single_reports():
    place = find_place(KOLKATA)
    c = build_complete_report("Asha Rao", "female", 29, 1, 1990, 10, 30, place, options=["Aasha Rao"], today=TODAY)
    assert c["name"] == "Asha Rao" and c["report_date"] == "31 October 2026"
    assert c["numerology"] == build_report(29, 1, 1990, "Asha Rao", today=TODAY)
    assert c["name_report"] == build_name_report("Asha Rao", "person", "Asha Rao", today=TODAY, birth=(29, 1, 1990), options=["Aasha Rao"])
    assert c["astro"] == build_astro_report("Asha Rao", "female", 1990, 1, 29, 10, 30, place, today=TODAY)


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_complete_route(client):
    url = f"/complete-report?name=Asha%20Rao&gender=female&day=29&month=1&year=1990&hour=10&minute=30&place={KOLKATA}&style=south"
    html = client.get(url).get_data(as_text=True)
    for text in ("Complete Reading", "Part I", "Part II", "Part III", "Maha Dasha", "Current name analysis", "Vimshottari Dasha", "south-grid"):
        assert text in html
    assert 'id="styleToggle" data-style="north"' in html


@pytest.mark.parametrize("query, message", [
    ("name=&day=29&month=1&year=1990&hour=10&minute=30&place=" + KOLKATA, "enter+a+name"),
    ("name=Asha&day=29&month=1&year=1990&hour=10&place=" + KOLKATA, "time+of+birth"),
    ("name=Asha&day=29&month=1&year=1990&hour=10&minute=30&place=Nowhere", "place+of+birth"),
])
def test_complete_route_sends_problems_back_to_the_form(client, query, message):
    response = client.get("/complete-report?" + query)
    location = response.headers["Location"]
    assert response.status_code == 302 and "tab=complete" in location and message in location
