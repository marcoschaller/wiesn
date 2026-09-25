# Munich Transit Reliability

How punctual is Munich's public transport? This project compares **planned** schedules (MVV GTFS)
with **actual** departures (MVG live data), collected over time.

## Data sources
| Source | What | License / status |
|---|---|---|
| [MVV GTFS (gesamt)](https://www.mvv-muenchen.de/service-hilfe/mvv-content-fuer-entwickler) | Static schedules: S-Bahn, U-Bahn, tram, bus (~2.2M stop_times) | CC BY, updated every 4–8 weeks |
| MVG JSON API (`mvg.de/api/bgw-pt/v3`) | Live departures, delays, cancellations, incidents | Unofficial & undocumented, poll politely |
| [Oktoberfest 1985–2025](https://opendata.muenchen.de/dataset/oktoberfest) | Visitors, duration, beer/Hendl prices & consumption, per-tent beer prices, food prices | dl-de/by-2.0. No 2020/2021 (COVID). Units: visitors in millions, visitors/day in thousands, beer in hectolitres |

Any other dataset on opendata.muenchen.de: `uv run python scripts/ingest_opendata.py <dataset-slug>`

## Quickstart
```bash
uv sync
uv run python scripts/ingest_gtfs.py        # download GTFS -> DuckDB (raw_gtfs.*)
uv run python scripts/poll_departures.py    # one live snapshot -> data/raw/departures/
uv run python scripts/explore.py            # first look at the data
uv run python scripts/find_station.py Giesing   # find more station IDs
```
## Data collection
Live departures are collected by a **GitHub Actions** workflow ([`.github/workflows/poll.yml`](.github/workflows/poll.yml))
every ~5 minutes and committed to `data/raw/departures/` as gzipped JSON lines (~15 KB per snapshot).
Scheduled runs can be delayed or skipped by GitHub, so always use the `_fetched_at` column, never the schedule.

Collect locally instead: `uv run python scripts/poll_departures.py --every 180`

## Layout
```
scripts/          ingestion + exploration
data/raw/gtfs/<date>/                     dated copies of the static feed
data/raw/departures/date=YYYY-MM-DD/*.jsonl.gz  raw live snapshots (append-only, committed)
data/warehouse.duckdb                      DuckDB warehouse
```

## Roadmap
- [x] Ingest static GTFS into DuckDB
- [x] Poll live departures into raw snapshots
- [x] Schedule the poller (GitHub Actions)
- [ ] dbt: staging -> dedup snapshots to one row per departure (last observation before departure) -> `fct_departures`
- [ ] Map MVG stations/lines to GTFS stops/routes
- [ ] Enrich with weather (DWD open data) and events (Oktoberfest, Allianz Arena matches)
- [ ] Data quality tests (Great Expectations / dbt tests)
- [ ] Dashboard (Streamlit / Evidence / Superset)
