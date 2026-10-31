"""
Compares the engine with the numerologist's original Excel workbook.

The workbook stores its last computed values, so every cell that Excel worked
out for the sample date in Dasha!A2:C2 is checked against the engine. The test
is skipped when the workbook or openpyxl is not available.
"""

from pathlib import Path

import pytest

from numerology import engine

WORKBOOK = Path.home() / "Personal" / "dasha calculator.xlsx"
openpyxl = pytest.importorskip("openpyxl")

pytestmark = pytest.mark.skipif(not WORKBOOK.exists(), reason="Excel workbook not present")

GRID_CELLS = ["B", "C", "D"]          # columns of a 3x3 grid block in the Grids sheet
GRID_NUMBERS = [3, 1, 9, 6, 7, 5, 2, 8, 4]


@pytest.fixture(scope="module")
def excel():
    wb = openpyxl.load_workbook(WORKBOOK, data_only=True)
    dasha, grids = wb["Dasha"], wb["Grids"]
    day, month, year = dasha["A2"].value, dasha["B2"].value, dasha["C2"].value
    calc = engine.calc_root_and_destiny(day, month, year)
    birth = engine.safe_date(year, month, day)
    return {
        "dasha": dasha, "grids": grids, "day": day, "month": month, "year": year,
        "calc": calc, "birth": birth,
        "periods": engine.calc_dasha_periods(calc["root"], birth),
        "natal": engine.build_natal_grid(calc["grid_digits"]),
    }


def test_root_destiny_and_reduced_month(excel):
    d, calc = excel["dasha"], excel["calc"]
    assert (d["B9"].value, d["B10"].value, d["B4"].value) == (calc["root"], calc["destiny"], calc["reduced_month"])


def test_maha_dasha_rows(excel):
    d = excel["dasha"]
    for i, row in enumerate(range(11, 26)):
        p = excel["periods"][i]
        assert (d[f"E{row}"].value, d[f"F{row}"].value.date(), d[f"G{row}"].value.date(), d[f"H{row}"].value) == (
            p["number"], p["start"].date(), p["end"].date(), p["start_age"])


def test_antardasha_rows(excel):
    d, calc = excel["dasha"], excel["calc"]
    rows = 0
    for row in range(11, 111):
        y = d[f"I{row}"].value
        if y is None:
            break
        a = engine.calc_antardasha(y, excel["day"], excel["month"], calc["root"], calc["reduced_month"])
        assert (d[f"M{row}"].value, d[f"N{row}"].value, d[f"O{row}"].value, d[f"P{row}"].value, d[f"Q{row}"].value) == (
            a["day_name"], a["planet_number"], a["sum"], a["P"], a["antardasha_number"]), y
        rows += 1
    assert rows >= 50


def test_grid_digits_and_natal_grid(excel):
    g, gd = excel["grids"], excel["calc"]["grid_digits"]
    for col, key in zip("LMNOPQRS", ["B1", "B2", "Root", "Destiny", "M1", "M2", "Y1", "Y2"]):
        value = g[f"{col}3"].value
        assert ("" if value in (None, "") else int(value)) == ("" if gd[key] is None else gd[key]), key
    for cell, num in zip([f"{c}{r}" for r in (8, 9, 10) for c in GRID_CELLS], GRID_NUMBERS):
        assert (g[cell].value or "") == excel["natal"][num], num


def test_review_year_blocks(excel):
    g, calc = excel["grids"], excel["calc"]
    for base in (12, 20, 28, 36, 44, 52):
        year = g[f"B{base}"].value
        if year is None:
            continue
        bday = engine.safe_date(year, excel["month"], excel["day"])
        maha = engine.find_maha_dasha(excel["periods"], bday)
        antar = engine.calc_antardasha(year, excel["day"], excel["month"], calc["root"], calc["reduced_month"])
        assert (g[f"B{base + 1}"].value, g[f"D{base + 1}"].value) == (maha, antar["antardasha_number"]), year

        grid = engine.build_yearly_grid(excel["natal"], maha, antar["antardasha_number"])
        for cell, num in zip([f"{c}{base + 3 + r}" for r in range(3) for c in GRID_CELLS], GRID_NUMBERS):
            assert (g[cell].value or "") == grid[num], (year, num)

        prats = engine.calc_pratyantar_dasha(antar["antardasha_number"], bday, excel["day"], excel["month"], year)
        for j, col in enumerate("GHIJKLMNO"):
            assert (g[f"{col}{base + 3}"].value, g[f"{col}{base + 4}"].value.date(), g[f"{col}{base + 5}"].value.date()) == (
                prats[j]["number"], prats[j]["start"].date(), prats[j]["end"].date()), (year, j)
