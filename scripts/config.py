"""Shared paths and settings."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
RAW_GTFS = DATA / "raw" / "gtfs"
RAW_DEPARTURES = DATA / "raw" / "departures"
WAREHOUSE = DATA / "warehouse.duckdb"

# Official MVV static GTFS (CC BY). "gesamt" = whole MVV network incl. S-Bahn, U-Bahn, tram, bus.
GTFS_URL = "https://www.mvv-muenchen.de/fileadmin/mediapool/developer/opendata/gesamt_gtfs.zip"

# Unofficial MVG JSON API (used by mvg.de). Undocumented - poll politely.
MVG_API = "https://www.mvg.de/api/bgw-pt/v3"

# Key interchange stations (MVG globalId). Look up more via scripts/find_station.py
STATIONS = {
    "de:09162:2": "Marienplatz",
    "de:09162:1": "Karlsplatz (Stachus)",
    "de:09162:6": "Hauptbahnhof",
    "de:09162:5": "Ostbahnhof",
    "de:09162:10": "Pasing",
    "de:09162:50": "Sendlinger Tor",
    "de:09162:500": "Muenchner Freiheit",
    "de:09162:1130": "Harras",
    # Oktoberfest (Theresienwiese) catchment
    "de:09162:240": "Theresienwiese",
    "de:09162:250": "Schwanthalerhoehe",
    "de:09162:7": "Hackerbruecke",
    "de:09162:40": "Goetheplatz",
    "de:09162:30": "Poccistrasse",
    # Big-event venues (Allianz Arena, Olympiapark)
    "de:09162:470": "Froettmaning",
    "de:09162:350": "Olympiazentrum",
}

# Munich open data portal (CKAN)
CKAN_API = "https://opendata.muenchen.de/api/3/action"
RAW_OPENDATA = DATA / "raw" / "opendata"
