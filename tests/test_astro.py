"""
Vedic astrology: positions, chart arithmetic, panchang and Vimshottari Dasha.

Reference values for 29 January 1990, 10:30 IST, Kolkata were read from
prokerala.com's birth chart and Vimshottari Dasha pages (Lahiri ayanamsa).
"""

from datetime import datetime

import pytest

from numerology import create_app
from numerology.astro.places import find_place, place_from_coordinates, search_places
from numerology.astro.report import build_astro_report
from numerology.astro.vedic import describe_longitude, house_from, panchang, vimshottari

TODAY = datetime(2026, 10, 31)
KOLKATA = find_place("Kolkata, West Bengal, IN")

# planet -> (sign, degrees, minutes, nakshatra, nakshatra lord, retrograde)
PROKERALA_POSITIONS = {
    "Sun": ("Capricorn", 15, 18, "Shravana", "Moon", False),
    "Moon": ("Aquarius", 15, 34, "Shatabhisha", "Rahu", False),
    "Mercury": ("Sagittarius", 20, 23, "Purva Ashadha", "Venus", False),
    "Venus": ("Sagittarius", 29, 18, "Uttara Ashadha", "Sun", True),
    "Mars": ("Sagittarius", 6, 0, "Mula", "Ketu", False),
    "Jupiter": ("Gemini", 8, 14, "Ardra", "Rahu", True),
    "Saturn": ("Sagittarius", 25, 11, "Purva Ashadha", "Venus", False),
    "Rahu": ("Capricorn", 23, 14, "Shravana", "Moon", True),
    "Ketu": ("Cancer", 23, 14, "Ashlesha", "Mercury", True),
}


@pytest.fixture(scope="module")
def sample():
    return build_astro_report("Test", "male", 1990, 1, 29, 10, 30, KOLKATA, today=TODAY)


def test_place_lookup():
    assert KOLKATA.timezone == "Asia/Kolkata" and abs(KOLKATA.latitude - 22.56) < 0.05
    assert [p.label for p in search_places("kolk")] == ["Kolkata, West Bengal, IN"]
    assert search_places("") == []


def test_place_search_ignores_accents():
    # GeoNames spells it Kānchrāpāra; people type Kanchrapara.
    assert [p.label for p in search_places("kanchrapara")] == ["Kanchrapara, West Bengal, IN"]
    assert [p.label for p in search_places("Kanchrapara, West Bengal")] == ["Kanchrapara, West Bengal, IN"]
    assert find_place("Kānchrāpāra, West Bengal, IN") == find_place("Kanchrapara, West Bengal, IN") is not None
    assert all(p.name.isascii() for p in search_places("ali"))


def test_place_from_online_search():
    place = place_from_coordinates("Halisahar, West Bengal, IN", "22.9323", "88.4189", "Asia/Kolkata")
    assert (place.name, place.region, place.country, place.timezone) == ("Halisahar", "West Bengal", "IN", "Asia/Kolkata")
    assert place.label == "Halisahar, West Bengal, IN"
    for bad in (("x", "91", "0", "Asia/Kolkata"), ("x", "0", "181", "Asia/Kolkata"), ("x", "0", "0", "Not/AZone"),
                ("x", "nan", "0", "Asia/Kolkata"), ("x", None, "0", "Asia/Kolkata"), ("", "0", "0", "Asia/Kolkata")):
        assert place_from_coordinates(*bad) is None


def test_birth_moment_conversion(sample):
    assert sample["birth"]["utc"] == "29 Jan 1990 05:00" and sample["birth"]["utc_offset"] == 5.5
    assert sample["birth"]["weekday"] == "Monday"


@pytest.mark.parametrize("planet", sorted(PROKERALA_POSITIONS))
def test_positions_match_prokerala(sample, planet):
    sign, d, m, nak, lord, retro = PROKERALA_POSITIONS[planet]
    p = next(x for x in sample["positions"] if x["key"] == planet)
    assert (p["sign"], p["degrees"]["d"], p["degrees"]["m"]) == (sign, d, m)
    assert (p["nakshatra"], p["nakshatra_lord"], p["retrograde"]) == (nak, lord, retro)


def test_lagna_matches_prokerala(sample):
    lagna = sample["lagna"]
    assert (lagna["sign"], lagna["degrees"]["d"], lagna["degrees"]["m"], lagna["nakshatra"]) == ("Aries", 4, 22, "Ashwini")


def test_houses_and_navamsa(sample):
    by_key = {p["key"]: p for p in sample["positions"]}
    assert by_key["Moon"]["house"] == 11 and by_key["Jupiter"]["house"] == 3 and by_key["Ketu"]["house"] == 4
    assert house_from(0, 0) == 1 and house_from(11, 0) == 12 and house_from(2, 5) == 10
    assert describe_longitude(315.5679)["navamsa_sign"] == "Aquarius"      # Moon
    assert describe_longitude(4.378)["navamsa_sign"] == "Taurus"           # Lagna 4°22' Aries -> 2nd navamsa
    assert sample["navamsa"]["lagna_sign"] == "Taurus"


def test_panchang_values(sample):
    assert sample["panchang"]["tithi"] == "Shukla Tritiya" and sample["panchang"]["vara"] == "Monday"
    assert sample["panchang"]["yoga"] == "Parigha" and sample["panchang"]["karana"] == "Garaja"
    full_moon = panchang(0, 179, 0)
    assert full_moon["tithi"] == "Shukla Purnima" and full_moon["tithi_number"] == 15
    assert panchang(10, 9, 3)["tithi"] == "Krishna Amavasya"
    assert panchang(0, 3, 0)["karana"] == "Kimstughna"


def test_vimshottari_matches_prokerala_within_two_days(sample):
    d = sample["dasha"]
    assert d["nakshatra"] == "Shatabhisha" and d["nakshatra_lord"] == "Rahu"
    lords = [m["lord"] for m in d["mahadashas"]]
    assert lords == ["Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun", "Moon", "Mars"]
    # prokerala: Rahu 21 Jan 1978 – 22 Jan 1996, Jupiter – 22 Jan 2012, Saturn – 21 Jan 2031
    expected = [("Rahu", "1978", "1996"), ("Jupiter", "1996", "2012"), ("Saturn", "2012", "2031"), ("Mercury", "2031", "2048")]
    for (lord, y1, y2), m in zip(expected, d["mahadashas"]):
        assert m["lord"] == lord and m["start"].endswith(y1) and m["end"].endswith(y2)
        assert m["start"].startswith(("21 Jan", "22 Jan", "23 Jan")) and m["end"].startswith(("21 Jan", "22 Jan", "23 Jan"))
    rahu_rahu = d["mahadashas"][0]["sub"][0]
    assert rahu_rahu["lord"] == "Rahu" and rahu_rahu["end"] in ("3 Oct 1980", "4 Oct 1980", "5 Oct 1980")
    assert len(d["mahadashas"][0]["sub"]) == 9 and len(d["mahadashas"][0]["sub"][0]["sub"]) == 9


def test_running_periods(sample):
    assert [p["lord"] for p in sample["now"]] == ["Saturn", "Rahu", "Saturn"]
    assert sample["now_text"] == "Saturn › Rahu › Saturn"
    current = [m for m in sample["dasha"]["mahadashas"] if m["is_current"]]
    assert len(current) == 1 and current[0]["lord"] == "Saturn"


def test_vimshottari_balance_arithmetic():
    v = vimshottari(0.0, datetime(2000, 1, 1), levels=1)      # start of Ashwini: full Ketu dasha ahead
    assert v["nakshatra_lord"] == "Ketu" and abs(v["balance_years"] - 7) < 1e-9
    v = vimshottari(13.3333333, datetime(2000, 1, 1), levels=1)  # end of Ashwini
    assert v["balance_years"] < 0.001


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()


def test_astro_routes(client):
    assert client.get("/places?q=kolk").get_json() == ["Kolkata, West Bengal, IN"]
    html = client.get("/astro-report?name=Test&gender=male&day=29&month=1&year=1990&hour=10&minute=30&place=Kolkata,%20West%20Bengal,%20IN&style=south").get_data(as_text=True)
    assert "Vedic Birth Chart" in html and "Shatabhisha" in html and "south-grid" in html
    html = client.get("/astro-report?day=29&month=1&year=1990&hour=10&minute=30&place=Kolkata,%20West%20Bengal,%20IN").get_data(as_text=True)
    assert "chart-north" in html
    response = client.get("/astro-report?day=29&month=1&year=1990&hour=10&minute=30&place=Nowhere")
    assert response.status_code == 302 and "tab=astro" in response.headers["Location"]
    html = client.get("/astro-report?day=29&month=1&year=1990&hour=10&minute=30&place=Halisahar,%20West%20Bengal,%20IN"
                      "&lat=22.9323&lon=88.4189&tz=Asia/Kolkata").get_data(as_text=True)
    assert "Vedic Birth Chart" in html and "Halisahar, West Bengal, IN" in html
