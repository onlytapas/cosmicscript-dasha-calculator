"""HTTP routes: the input form and the generated report."""

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from numerology.astro.places import find_place, place_from_coordinates, search_places
from numerology.astro.report import build_astro_report
from numerology.complete_report import build_complete_report
from numerology.name_report import build_name_report
from numerology.report import build_report
from numerology.web.validation import (parse_birth_date, parse_birth_time, parse_name, parse_optional_birth_date,
                                       parse_optional_name)

bp = Blueprint("main", __name__)


# Readings on the front page; "dasha" is the older name of the numerology reading.
READINGS = {"complete": "complete", "numerology": "numerology", "dasha": "numerology", "name": "name", "astro": "astro"}


@bp.get("/")
def home():
    reading = READINGS.get(request.args.get("tab", ""), "complete")
    return render_template("home.html", error=request.args.get("error", ""), reading=reading)


@bp.get("/report")
def report():
    try:
        birth = parse_birth_date(
            request.args.get("day", type=int),
            request.args.get("month", type=int),
            request.args.get("year", type=int),
        )
    except ValueError as exc:
        return redirect(url_for("main.home", error=str(exc), tab="numerology"))

    data = build_report(birth.day, birth.month, birth.year, request.args.get("name", ""))
    return render_template("report.html", r=data, view=request.args.get("view", ""))


@bp.get("/name-report")
def name_report():
    try:
        name = parse_name(request.args.get("name"))
        birth = parse_optional_birth_date(
            request.args.get("day", type=int),
            request.args.get("month", type=int),
            request.args.get("year", type=int),
        )
        options = [parse_optional_name(request.args.get(key)) for key in ("option1", "option2")]
    except ValueError as exc:
        return redirect(url_for("main.home", error=str(exc), tab="name"))

    data = build_name_report(
        name, request.args.get("owner", "person"), request.args.get("client", ""),
        birth=(birth.day, birth.month, birth.year) if birth else None, options=options,
    )
    return render_template("name_report.html", r=data, view=request.args.get("view", ""))


@bp.get("/places")
def places():
    return jsonify([p.label for p in search_places(request.args.get("q", ""))])


def _birth_details():
    """Date, time and place of birth from the query string; raises ValueError with a message for the client."""
    birth = parse_birth_date(
        request.args.get("day", type=int),
        request.args.get("month", type=int),
        request.args.get("year", type=int),
    )
    time = parse_birth_time(request.args.get("hour", type=int), request.args.get("minute", type=int))
    label = request.args.get("place", "")
    place = find_place(label) or place_from_coordinates(label, request.args.get("lat"), request.args.get("lon"), request.args.get("tz"))
    if place is None:
        raise ValueError("Please choose the place of birth from the list of suggestions.")
    return birth, time, place


@bp.get("/astro-report")
def astro_report():
    try:
        birth, time, place = _birth_details()
    except ValueError as exc:
        return redirect(url_for("main.home", error=str(exc), tab="astro"))

    data = build_astro_report(
        request.args.get("name", ""), request.args.get("gender", ""),
        birth.year, birth.month, birth.day, time.hour, time.minute, place,
        chart_style=request.args.get("style", "north"),
    )
    return render_template("astro_report.html", r=data, view=request.args.get("view", ""))


@bp.get("/complete-report")
def complete_report():
    try:
        name = parse_name(request.args.get("name"))
        birth, time, place = _birth_details()
        options = [parse_optional_name(request.args.get(key)) for key in ("option1", "option2")]
    except ValueError as exc:
        return redirect(url_for("main.home", error=str(exc), tab="complete"))

    data = build_complete_report(
        name, request.args.get("gender", ""), birth.day, birth.month, birth.year, time.hour, time.minute, place,
        chart_style=request.args.get("style", "north"), options=options,
    )
    return render_template("complete_report.html", c=data, view=request.args.get("view", ""))
