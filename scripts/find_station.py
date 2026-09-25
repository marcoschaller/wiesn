"""Look up MVG station globalIds by name.  Usage: python scripts/find_station.py Giesing"""
import sys

import requests

from config import MVG_API

query = " ".join(sys.argv[1:]) or "Marienplatz"
resp = requests.get(
    f"{MVG_API}/locations",
    params={"query": query, "locationTypes": "STATION"},
    timeout=20,
)
resp.raise_for_status()
for loc in resp.json()[:10]:
    print(f"{loc['globalId']:<16} {loc['name']}, {loc['place']:<12} {','.join(loc['transportTypes'])}")
