"""
Builds the single-file, no-server version of the calculator: docs/index.html.

The file bundles the same templates, stylesheets, interpretations and planet
tables the Flask app uses, plus the JavaScript port of the engine, so the two
versions cannot drift apart. Publish docs/index.html to any static host.

    python3 build_static.py
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import shutil
from datetime import date
from pathlib import Path

from numerology import constants, interpretations, name_engine, name_interpretations
from numerology.astro import constants as astro_constants
from numerology.astro.places import PLACES_FILE

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "numerology"
SRC = ROOT / "static_app"
DIST = ROOT / "docs"

# A minimal base so the Flask templates render as fragments inside the shell.
STATIC_BASE = "{% block content %}{% endblock %}"

TEMPLATE_FILES = (
    "home.html", "report.html", "name_report.html", "astro_report.html", "complete_report.html",
    "_numerology_body.html", "_name_body.html", "_astro_body.html",
    "_toolbar.html", "_mode.html", "_chart.html", "_grid.html", "_steps.html",
)


def build_data(version: str = "") -> dict:
    """Everything the JavaScript side needs, taken straight from the Python modules."""
    return {
        "VERSION": version,
        "PLANETS": {n: dataclasses.asdict(p) for n, p in constants.PLANETS.items()},
        "WEEKDAY_PLANET": constants.WEEKDAY_PLANET,
        "DAY_NAMES": constants.DAY_NAMES,
        "MONTH_NAMES": constants.MONTH_NAMES,
        "MONTH_NAMES_SHORT": constants.MONTH_NAMES_SHORT,
        "GRID_LAYOUT": constants.GRID_LAYOUT,
        "CONFIG": {
            "MAHA_DASHA_PERIODS_SHOWN": constants.MAHA_DASHA_PERIODS_SHOWN,
            "ANTARDASHA_YEARS_BEFORE": constants.ANTARDASHA_YEARS_BEFORE,
            "ANTARDASHA_YEARS_AFTER": constants.ANTARDASHA_YEARS_AFTER,
            "REVIEW_YEARS_BEFORE": constants.REVIEW_YEARS_BEFORE,
            "REVIEW_YEARS_AFTER": constants.REVIEW_YEARS_AFTER,
            "PRATYANTAR_DAYS_PER_UNIT": constants.PRATYANTAR_DAYS_PER_UNIT,
        },
        "INTERPRETATIONS": {
            "ROOT_INTERPRETATIONS": interpretations.ROOT_INTERPRETATIONS,
            "DESTINY_INTERPRETATIONS": interpretations.DESTINY_INTERPRETATIONS,
            "FAVOURABLE_COLOURS": interpretations.FAVOURABLE_COLOURS,
            "FAVOURABLE_DAYS": interpretations.FAVOURABLE_DAYS,
            "FRIENDLY_NUMBERS": interpretations.FRIENDLY_NUMBERS,
            "NEUTRAL_NUMBERS": interpretations.NEUTRAL_NUMBERS,
            "ENEMY_NUMBERS": interpretations.ENEMY_NUMBERS,
        },
        "NAME": {
            "LETTER_VALUES": name_engine.LETTER_VALUES,
            "CHALDEAN_TABLE": name_engine.CHALDEAN_TABLE,
            "MAX_GRADED_TOTAL": name_engine.MAX_GRADED_TOTAL,
            "GRADES": name_interpretations.GRADES,
            "GRADE_LEVELS": name_interpretations.GRADE_LEVELS,
            "COMPOUND_MEANINGS": name_interpretations.COMPOUND_MEANINGS,
            "NAME_NUMBER_MEANINGS": name_interpretations.NAME_NUMBER_MEANINGS,
        },
        "ASTRO": {
            "SIGNS": [dataclasses.asdict(x) for x in astro_constants.SIGNS],
            "NAKSHATRAS": astro_constants.NAKSHATRAS,
            "DASHA_LORDS": astro_constants.DASHA_LORDS,
            "DASHA_YEARS": astro_constants.DASHA_YEARS,
            "DASHA_TOTAL_YEARS": astro_constants.DASHA_TOTAL_YEARS,
            "DASHA_YEAR_DAYS": astro_constants.DASHA_YEAR_DAYS,
            "NAKSHATRA_SPAN": astro_constants.NAKSHATRA_SPAN,
            "NAVAMSA_SPAN": astro_constants.NAVAMSA_SPAN,
            "PLANETS": astro_constants.PLANETS,
            "WEEKDAY_LORDS": astro_constants.WEEKDAY_LORDS,
            "WEEKDAY_NAMES": astro_constants.WEEKDAY_NAMES,
            "TITHI_NAMES": astro_constants.TITHI_NAMES,
            "YOGA_NAMES": astro_constants.YOGA_NAMES,
            "KARANA_CYCLE": astro_constants.KARANA_CYCLE,
            "KARANA_FIXED": astro_constants.KARANA_FIXED,
            "PLACES_RAW": json.loads(PLACES_FILE.read_text()),
        },
        "TEMPLATES": {
            "base.html": STATIC_BASE,
            **{name: (PKG / "templates" / name).read_text() for name in TEMPLATE_FILES},
        },
    }


def _js_json(obj) -> str:
    """JSON that is safe to embed inside a <script> element."""
    return json.dumps(obj, ensure_ascii=False).replace("</", "<\\/")


def build(version: str | None = None) -> Path:
    css = PKG / "static" / "css"
    parts = {
        "site_css": (css / "site.css").read_text(),
        "report_css": (css / "report.css").read_text(),
        "print_css": (css / "print.css").read_text(),
        "nunjucks": (SRC / "vendor" / "nunjucks.min.js").read_text(),
        "engine": (SRC / "engine.js").read_text(),
        "report": (SRC / "report.js").read_text(),
        "name": (SRC / "name_engine.js").read_text(),
        "astro": (SRC / "astro.js").read_text(),
        "theme": (PKG / "static" / "js" / "theme.js").read_text(),
        "home": (PKG / "static" / "js" / "home.js").read_text(),
        "toolbar": (PKG / "static" / "js" / "report.js").read_text(),
        "app": (SRC / "app.js").read_text(),
    }
    if version is None:
        digest = hashlib.sha256("".join(parts.values()).encode() + _js_json(build_data()).encode()).hexdigest()[:6]
        version = f"{date.today():%Y.%m.%d}-{digest}"
    data = build_data(version)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="theme-color" content="#f2eee4">
    <meta name="description" content="CosmicScript numerology, name numerology and Vedic astrology readings">
    <title>CosmicScript · Numerology and Astrology</title>
    <script>{parts['theme']}</script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,300;1,9..144,400&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
{parts['site_css']}
{parts['report_css']}
    </style>
    <style media="print">
{parts['print_css']}
    </style>
</head>
<body class="landing">
    <div class="aurora" aria-hidden="true"><div class="blob b1"></div><div class="blob b2"></div><div class="blob b3"></div></div>
    <div class="grain" aria-hidden="true"></div>
    <div id="app"></div>
    <script>{parts['nunjucks']}</script>
    <script>window.COSMIC_DATA = {_js_json(data)};</script>
    <script>{parts['engine']}</script>
    <script>{parts['report']}</script>
    <script>{parts['name']}</script>
    <script>{parts['astro']}</script>
    <script>{parts['home']}</script>
    <script>{parts['toolbar']}</script>
    <script>{parts['app']}</script>
</body>
</html>
"""
    DIST.mkdir(exist_ok=True)
    out = DIST / "index.html"
    out.write_text(html)
    vendor = DIST / "vendor" / "swisseph"
    if vendor.exists():
        shutil.rmtree(vendor)
    shutil.copytree(SRC / "vendor" / "swisseph", vendor)
    return out


if __name__ == "__main__":
    path = build()
    print(f"built {path} ({path.stat().st_size // 1024} KB)")
