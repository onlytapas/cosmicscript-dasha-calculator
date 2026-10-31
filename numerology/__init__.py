"""
CosmicScript Vedic Numerology Dasha Calculator.

Package layout:

* ``constants``        — planets, grid layout and calendar lookups.
* ``interpretations`` — report wording keyed by number.
* ``engine``          — the calculations (Root, Destiny, grids, dashas).
* ``report``          — turns engine output into a template-ready view model.
* ``web``             — the Flask application and routes.
"""

from numerology.web import create_app

__all__ = ["create_app"]
