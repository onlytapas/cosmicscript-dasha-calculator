"""HTTP routes: the input form and the generated report."""

from flask import Blueprint, redirect, render_template, request, url_for

from numerology.report import build_report
from numerology.web.validation import parse_birth_date

bp = Blueprint("main", __name__)


@bp.get("/")
def home():
    return render_template("home.html", error=request.args.get("error", ""))


@bp.get("/report")
def report():
    try:
        birth = parse_birth_date(
            request.args.get("day", type=int),
            request.args.get("month", type=int),
            request.args.get("year", type=int),
        )
    except ValueError as exc:
        return redirect(url_for("main.home", error=str(exc)))

    data = build_report(birth.day, birth.month, birth.year, request.args.get("name", ""))
    return render_template("report.html", r=data)
