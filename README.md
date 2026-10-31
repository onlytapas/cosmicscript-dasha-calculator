# CosmicScript · Vedic Numerology Dasha Calculator

Three calculators behind one purple-and-gold front page, each with a printable
client report:

* **Dasha calculator** (numerology): Root and Destiny numbers, natal grid, Maha
  Dasha, yearly Antardasha and Pratyantar periods, reproducing the original
  `dasha calculator.xlsx` spreadsheet exactly.
* **Name numerology**: Chaldean letter values, name total and grade.
* **Astrology**: Vedic birth chart from date, time and place: planetary
  positions (Swiss Ephemeris, Lahiri ayanamsa), Rasi and Navamsa charts in
  North or South Indian style, panchang at birth and the full Vimshottari
  Dasha tree (Maha, Antar, Pratyantar), verified against prokerala.com.

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

If either fails, a calculation has changed. `tests/test_astro.py` checks the
birth chart against reference values from prokerala.com, and
`tests/test_static_astro.py` runs the hosted build in headless Chrome and
compares it with Python (skipped when Chrome is absent).

Licences: Swiss Ephemeris (pyswisseph and the WebAssembly build) is AGPL/GPL,
which this public repository satisfies; place data is from GeoNames (CC BY 4.0).

## Layout

```
app.py                      entry point (waitress server)
numerology/
  constants.py              planets, grid layout, calendar lookups
  interpretations.py        report wording per number
  engine.py                 calculations (spreadsheet cell names kept)
  report.py                 engine output -> template view model
  name_engine.py, name_report.py, name_interpretations.py   Chaldean name numerology
  astro/                    Vedic astrology: ephemeris wrapper, vedic.py arithmetic,
                            places.json (GeoNames, CC BY 4.0), ephe/ Swiss Ephemeris files
  web/                      Flask app factory, routes, form validation
  templates/                base, home, report and partials
  static/css, static/js     deep purple & gold theme, print rules, toolbar
static_app/                 JavaScript ports + single-page shell; vendor/swisseph is the
                            WebAssembly Swiss Ephemeris (GPL/AGPL) loaded only for astrology
build_static.py             bundles everything into docs/index.html (GitHub Pages)
docs/index.html             the built single-file app, served by GitHub Pages
tests/                      regression and route tests
```
