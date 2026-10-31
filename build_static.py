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
from datetime import date
from pathlib import Path

from numerology import constants, interpretations, name_engine, name_interpretations

ROOT = Path(__file__).resolve().parent
PKG = ROOT / "numerology"
SRC = ROOT / "static_app"
DIST = ROOT / "docs"

# A minimal base so the Flask templates render as fragments inside the shell.
STATIC_BASE = "{% block content %}{% endblock %}"


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
        "TEMPLATES": {
            "base.html": STATIC_BASE,
            "home.html": (PKG / "templates" / "home.html").read_text(),
            "report.html": (PKG / "templates" / "report.html").read_text(),
            "name_report.html": (PKG / "templates" / "name_report.html").read_text(),
            "_grid.html": (PKG / "templates" / "_grid.html").read_text(),
            "_steps.html": (PKG / "templates" / "_steps.html").read_text(),
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
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="theme-color" content="#0a0612">
    <meta name="description" content="CosmicScript Vedic numerology Dasha calculator and report">
    <title>CosmicScript · Vedic Numerology</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Lora:ital,wght@0,400;0,500;0,600;1,400&family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&display=swap" rel="stylesheet">
    <style>
{parts['site_css']}
{parts['report_css']}
    </style>
    <style media="print">
{parts['print_css']}
    </style>
</head>
<body class="landing">
    <div class="cosmos" aria-hidden="true"></div>
    <div id="app"></div>
    <script>{parts['nunjucks']}</script>
    <script>window.COSMIC_DATA = {_js_json(data)};</script>
    <script>{parts['engine']}</script>
    <script>{parts['report']}</script>
    <script>{parts['name']}</script>
    <script>{parts['app']}</script>
</body>
</html>
"""
    DIST.mkdir(exist_ok=True)
    out = DIST / "index.html"
    out.write_text(html)
    return out


if __name__ == "__main__":
    path = build()
    print(f"built {path} ({path.stat().st_size // 1024} KB)")
