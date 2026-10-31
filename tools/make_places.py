"""
Builds numerology/astro/places.json from the GeoNames cities15000 dump.

    python3 tools/make_places.py /path/to/cities15000.txt

Keeps every Indian town with population 20,000 or more and every other city
with population 250,000 or more. Each entry is
[name, region, country code, latitude, longitude, IANA time zone].
GeoNames data is CC BY 4.0 (https://www.geonames.org).
"""

import csv
import json
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "numerology" / "astro" / "places.json"
ADMIN1_IN = {  # GeoNames admin1 codes for India -> state names
    "01": "Andaman and Nicobar", "02": "Andhra Pradesh", "03": "Assam", "05": "Chandigarh", "06": "Dadra and Nagar Haveli",
    "07": "Delhi", "09": "Gujarat", "10": "Haryana", "11": "Himachal Pradesh", "12": "Jammu and Kashmir", "13": "Kerala",
    "14": "Lakshadweep", "16": "Maharashtra", "17": "Manipur", "18": "Meghalaya", "19": "Karnataka", "20": "Nagaland",
    "21": "Odisha", "22": "Puducherry", "23": "Punjab", "24": "Rajasthan", "25": "Tamil Nadu", "26": "Tripura",
    "28": "West Bengal", "29": "Sikkim", "30": "Arunachal Pradesh", "31": "Mizoram", "32": "Daman and Diu", "33": "Goa",
    "34": "Bihar", "35": "Madhya Pradesh", "36": "Uttar Pradesh", "37": "Chhattisgarh", "38": "Jharkhand",
    "39": "Uttarakhand", "40": "Telangana", "41": "Ladakh",
}


def main(src: str) -> None:
    places = []
    with open(src, encoding="utf-8") as fh:
        for r in csv.reader(fh, delimiter="\t"):
            name, lat, lon, country, admin1, pop, tz = r[1], float(r[4]), float(r[5]), r[8], r[10], int(r[14]), r[17]
            if country == "IN" and pop >= 20000:
                region = ADMIN1_IN.get(admin1, "")
            elif country != "IN" and pop >= 250000:
                region = ""
            else:
                continue
            places.append([name, region, country, round(lat, 4), round(lon, 4), tz])
    places.sort(key=lambda p: (p[2] != "IN", p[0]))
    OUT.write_text(json.dumps(places, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(places)} places -> {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main(sys.argv[1])
