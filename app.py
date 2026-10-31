"""
CosmicScript Vedic Numerology Dasha Calculator.

Run with ``python app.py`` and the report form opens in your browser at
http://localhost:8800. Use ``--port`` to change the port and ``--no-browser``
to skip opening it.
"""

import argparse
import threading
import webbrowser

from waitress import serve

from numerology import create_app

DEFAULT_PORT = 8800


def main() -> None:
    parser = argparse.ArgumentParser(description="Vedic Numerology Dasha Calculator")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"port (default {DEFAULT_PORT})")
    parser.add_argument("--no-browser", action="store_true", help="do not open the browser")
    args = parser.parse_args()

    url = f"http://localhost:{args.port}"
    print(f"CosmicScript Dasha Calculator running at {url}  (Ctrl+C to stop)")
    if not args.no_browser:
        threading.Timer(1.0, lambda: webbrowser.open(url)).start()

    serve(create_app(), host="127.0.0.1", port=args.port)


if __name__ == "__main__":
    main()
