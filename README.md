# CosmicScript · Vedic Numerology Dasha Calculator

A small Flask application that turns a date of birth into a printable Vedic
numerology report: Root and Destiny numbers with interpretations, the natal
grid, Maha Dasha periods, yearly Antardasha numbers and Pratyantar sub-periods.
The formulas reproduce the original `dasha calculator.xlsx` spreadsheet.

## Run

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py            # opens http://localhost:8800
python app.py --port 9000 --no-browser
```

## Test

```bash
pip install pytest
pytest
```

Two safety nets guard the calculations:

* `tests/fixtures/engine_snapshot.json` holds results captured from the original
  single-file calculator for hundreds of birth dates.
* `tests/test_excel.py` opens `~/Personal/dasha calculator.xlsx` (if present,
  with `openpyxl` installed) and compares every value Excel computed for its
  sample date with the engine, cell by cell.

If either fails, a calculation has changed.

## Layout

```
app.py                      entry point (waitress server)
numerology/
  constants.py              planets, grid layout, calendar lookups
  interpretations.py        report wording per number
  engine.py                 calculations (spreadsheet cell names kept)
  report.py                 engine output -> template view model
  web/                      Flask app factory, routes, form validation
  templates/                base, home, report and partials
  static/css, static/js     deep purple & gold theme, print rules, toolbar
static_app/                 JavaScript port of engine + report, single-page shell
build_static.py             bundles everything into docs/index.html (GitHub Pages)
docs/index.html             the built single-file app, served by GitHub Pages
tests/                      regression and route tests
```
