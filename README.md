# CosmicScript · Vedic Numerology Dasha Calculator

Four readings from one front page, in the Sage & Clay theme with a light and
a dark mode (the switch is top right; the choice is remembered on the device).
The client's details are entered once, and only the fields the chosen reading
needs are shown: first, middle (optional) and last name, date of birth, and for
astrology also gender, time and place of birth.

* **Numerology**: Root and Destiny numbers, natal grid, Maha Dasha, yearly
  Antardasha and Pratyantar periods, reproducing the original
  `dasha calculator.xlsx` spreadsheet exactly.
* **Name Numerology**: Chaldean letter values, name total and grade, the name
  matrix, and alignment of the name number with the Root and Destiny numbers.
  Suggested spellings for name correction are typed inside the report.
* **Astrology · Kundli**: Vedic birth chart from date, time and place: planetary
  positions (Swiss Ephemeris, Lahiri ayanamsa), Rasi and Navamsa charts in
  North or South Indian style (switch in the toolbar), panchang at birth and the
  full Vimshottari Dasha tree, verified against prokerala.com.
* **Complete Reading**: all three in one report, built by the same functions as
  the single reports.

Every report has two views, switched from the toolbar: the **full view** for
the practitioner, with all the working, and the **client view**, which hides
everything marked `pro-only` in the templates so the client sees only the
readings. The chosen view is kept in the URL (`view=client`), and "Save HTML"
in the client view leaves the working out of the saved file.

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
  compatibility.py          friendly / neutral / challenging number lookup
  complete_report.py        the three reports together
  astro/                    Vedic astrology: ephemeris wrapper, vedic.py arithmetic,
                            places.json (GeoNames, CC BY 4.0), ephe/ Swiss Ephemeris files
  web/                      Flask app factory, routes, form validation
  templates/                base, home, report and partials
  static/css, static/js     Sage & Clay theme (light and dark), print rules, front page, toolbar
static_app/                 JavaScript ports + single-page shell; vendor/swisseph is the
                            WebAssembly Swiss Ephemeris (GPL/AGPL) loaded only for astrology
build_static.py             bundles everything into docs/index.html (GitHub Pages)
docs/index.html             the built single-file app, served by GitHub Pages
tests/                      regression and route tests
```
