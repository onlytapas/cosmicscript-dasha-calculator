"""
The astrology page of the static build must match the Flask app.

The static build runs the Swiss Ephemeris as WebAssembly, so this test serves
the built site over HTTP, opens it in headless Chrome, and compares the JSON
the page computes with numerology.astro.report. Skipped without Chrome.
"""

import dataclasses
import html
import http.server
import json
import re
import shutil
import socket
import subprocess
import threading
from datetime import datetime
from functools import partial
from pathlib import Path

import pytest

import build_static
from numerology.astro.places import find_place
from numerology.astro.report import build_astro_report

CHROME = next((c for c in (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    shutil.which("google-chrome"), shutil.which("chromium"), shutil.which("chrome"),
) if c and Path(c).exists()), None)
pytestmark = pytest.mark.skipif(CHROME is None, reason="Chrome is not installed")

TODAY = datetime(2026, 10, 31)
CASES = [
    dict(name="Asha Rao", gender="female", day=29, month=1, year=1990, hour=10, minute=30, place="Kolkata, West Bengal, IN", style="north"),
    dict(name="Test", gender="male", day=15, month=8, year=1947, hour=0, minute=1, place="Delhi, Delhi, IN", style="south"),
    dict(name="Leap", gender="female", day=29, month=2, year=2004, hour=23, minute=45, place="London, GB", style="north"),
    dict(name="DST", gender="male", day=4, month=7, year=1985, hour=14, minute=20, place="New York City, US", style="south"),
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
        assert isinstance(b, dict) and set(a) == set(b), f"{where}: keys {sorted(set(a) ^ set(b))}"
        for k in a:
            assert_same(a[k], b[k], f"{where}.{k}")
    elif isinstance(a, list):
        assert isinstance(b, list) and len(a) == len(b), where
        for i, (x, y) in enumerate(zip(a, b)):
            assert_same(x, y, f"{where}[{i}]")
    elif isinstance(a, float):
        assert abs(a - b) < (1e-3 if where.endswith(".longitude") else 1e-6), f"{where}: python={a} js={b}"
    else:
        assert a == b, f"{where}: python={a!r} js={b!r}"


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    dist = tmp_path_factory.mktemp("site")
    build_static.DIST = dist
    build_static.build(version="test")
    handler = partial(http.server.SimpleHTTPRequestHandler, directory=str(dist))
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}/"
    server.shutdown()


def browser_json(site_url: str, case: dict) -> dict:
    """Load the page in headless Chrome; retry if the snapshot came before the ephemeris finished loading."""
    query = "&".join(f"{k}={v}" for k, v in case.items()).replace(" ", "%20")
    url = f"{site_url}#/astro-report?{query}&format=json&today=2026-10-31T00:00:00Z"
    text = ""
    for _ in range(3):
        out = subprocess.run(
            [CHROME, "--headless=new", "--disable-gpu", "--no-sandbox", "--virtual-time-budget=60000", "--dump-dom", url],
            capture_output=True, text=True, timeout=120,
        ).stdout
        match = re.search(r'<pre id="json">(.*?)</pre>', out, re.S)
        text = html.unescape(match.group(1)) if match else ""
        if text.startswith("{"):
            return json.loads(text)
    raise AssertionError("the page did not produce JSON: " + re.sub(r"<[^>]+>", " ", out)[-300:])


@pytest.mark.parametrize("case", CASES, ids=lambda c: c["name"])
def test_browser_matches_python(site, case):
    place = find_place(case["place"])
    assert place is not None
    expected = plain(build_astro_report(case["name"], case["gender"], case["year"], case["month"], case["day"],
                                        case["hour"], case["minute"], place, chart_style=case["style"], today=TODAY))
    assert_same(expected, browser_json(site, case))
