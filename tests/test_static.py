"""
The static (no server) build must produce exactly what the Flask app produces.

Runs static_app/engine.js and report.js under Node for many birth dates and
compares the resulting report model with numerology.report.build_report.
"""

import dataclasses
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest

import build_static
from numerology.name_report import build_name_report
from numerology.report import build_report

NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node is not installed")

TODAY = datetime(2026, 10, 31)
DATES = [
    (d, m, y)
    for y in (1900, 1947, 1965, 1972, 1981, 1990, 1999, 2000, 2004, 2012, 2020, 2024)
    for m, d in ((1, 1), (1, 29), (2, 29), (6, 10), (9, 30), (10, 11), (12, 20), (12, 31))
    if not (m == 2 and d == 29 and (y % 4 or (y % 100 == 0 and y % 400)))
]


NAMES = [
    ("person", "Asha Rao"), ("business", "CosmicScript"), ("person", "Mr. O'Brien-Smith 2nd"),
    ("person", "Z"), ("business", "PPPPPPPPPPPPP"), ("person", "Jean-Luc Picard"), ("person", "Ravi Shankar Prasad"),
]


def plain(obj):
    if dataclasses.is_dataclass(obj):
        return dataclasses.asdict(obj)
    if isinstance(obj, dict):
        return {str(k): plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [plain(v) for v in obj]
    return obj


def assert_same(a, b, where=""):
    if isinstance(a, dict):
        assert isinstance(b, dict) and set(a) == set(b), where
        for k in a:
            assert_same(a[k], b[k], f"{where}.{k}")
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), where
        for i, (x, y) in enumerate(zip(a, b)):
            assert_same(x, y, f"{where}[{i}]")
    elif isinstance(a, float) and where.endswith(".width"):
        assert abs(a - b) < 0.011, where   # rounding of a percentage only
    else:
        assert a == b, f"{where}: python={a!r} js={b!r}"


@pytest.fixture(scope="module")
def js_reports(tmp_path_factory):
    data_file = tmp_path_factory.mktemp("static") / "data.json"
    data_file.write_text(json.dumps(build_static.build_data()))
    keys = [f"{d:02d}-{m:02d}-{y}" for d, m, y in DATES] + [f"name:{o}:{n}" for o, n in NAMES]
    result = subprocess.run(
        [NODE, str(Path(__file__).parent / "js_harness.js"), str(data_file), TODAY.strftime("%Y-%m-%d"), *keys],
        capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("date", DATES, ids=lambda d: f"{d[0]:02d}-{d[1]:02d}-{d[2]}")
def test_javascript_matches_python(js_reports, date):
    day, month, year = date
    expected = plain(build_report(day, month, year, "Test Person", today=TODAY))
    assert_same(expected, js_reports[f"{day:02d}-{month:02d}-{year}"])


def test_bundle_builds(tmp_path, monkeypatch):
    monkeypatch.setattr(build_static, "DIST", tmp_path)
    out = build_static.build(version="test")
    html = out.read_text()
    assert "window.COSMIC_DATA" in html and "createEngine" in html and "nunjucks" in html
    assert "ROOT_INTERPRETATIONS" in html and "report.html" in html
    assert out.stat().st_size < 600_000


@pytest.mark.parametrize("owner_name", NAMES, ids=lambda p: p[1])
def test_javascript_name_report_matches_python(js_reports, owner_name):
    owner, name = owner_name
    expected = plain(build_name_report(name, owner, "Client", today=TODAY))
    assert_same(expected, js_reports[f"name:{owner}:{name}"])
