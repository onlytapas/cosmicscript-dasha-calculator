"""Static tables for Vedic astrology."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Sign:
    index: int          # 0 = Aries
    name: str
    sanskrit: str
    lord: str
    element: str
    quality: str        # movable, fixed, dual


SIGNS = [
    Sign(0, "Aries", "Mesha", "Mars", "Fire", "movable"),
    Sign(1, "Taurus", "Vrishabha", "Venus", "Earth", "fixed"),
    Sign(2, "Gemini", "Mithuna", "Mercury", "Air", "dual"),
    Sign(3, "Cancer", "Karka", "Moon", "Water", "movable"),
    Sign(4, "Leo", "Simha", "Sun", "Fire", "fixed"),
    Sign(5, "Virgo", "Kanya", "Mercury", "Earth", "dual"),
    Sign(6, "Libra", "Tula", "Venus", "Air", "movable"),
    Sign(7, "Scorpio", "Vrishchika", "Mars", "Water", "fixed"),
    Sign(8, "Sagittarius", "Dhanu", "Jupiter", "Fire", "dual"),
    Sign(9, "Capricorn", "Makara", "Saturn", "Earth", "movable"),
    Sign(10, "Aquarius", "Kumbha", "Saturn", "Air", "fixed"),
    Sign(11, "Pisces", "Meena", "Jupiter", "Water", "dual"),
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada",
    "Uttara Bhadrapada", "Revati",
]

# Vimshottari lords in cycle order, starting from Ashwini.
DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}
DASHA_TOTAL_YEARS = 120
DASHA_YEAR_DAYS = 365.25
NAKSHATRA_SPAN = 360 / 27
NAVAMSA_SPAN = 30 / 9

# Display order and symbols for the chart.
PLANETS = [
    {"key": "Sun", "abbr": "Su", "symbol": "☉"},
    {"key": "Moon", "abbr": "Mo", "symbol": "☽"},
    {"key": "Mars", "abbr": "Ma", "symbol": "♂"},
    {"key": "Mercury", "abbr": "Me", "symbol": "☿"},
    {"key": "Jupiter", "abbr": "Ju", "symbol": "♃"},
    {"key": "Venus", "abbr": "Ve", "symbol": "♀"},
    {"key": "Saturn", "abbr": "Sa", "symbol": "♄"},
    {"key": "Rahu", "abbr": "Ra", "symbol": "☊"},
    {"key": "Ketu", "abbr": "Ke", "symbol": "☋"},
]

WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]   # Sunday first
WEEKDAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi", "Saptami", "Ashtami",
    "Navami", "Dashami", "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi",
]
YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda", "Sukarma", "Dhriti", "Shula",
    "Ganda", "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan",
    "Parigha", "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
]
KARANA_CYCLE = ["Bava", "Balava", "Kaulava", "Taitila", "Garaja", "Vanija", "Vishti"]
KARANA_FIXED = {0: "Kimstughna", 57: "Shakuni", 58: "Chatushpada", 59: "Naga"}
