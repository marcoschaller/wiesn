"""Poll MVG live departures for the configured stations and store raw snapshots.

Output: data/raw/departures/date=YYYY-MM-DD/<HHMMSS>.jsonl.gz  (one departure per line)

Usage:
    python scripts/poll_departures.py              # one snapshot
    python scripts/poll_departures.py --every 120  # poll every 2 min until Ctrl+C
"""
import argparse
import gzip
import json
import time
from datetime import datetime, timezone

import requests

from config import MVG_API, RAW_DEPARTURES, STATIONS

SESSION = requests.Session()
SESSION.headers["User-Agent"] = "munich-transit-portfolio-project (personal, low-volume)"


def fetch_station(global_id: str, limit: int = 40) -> list[dict]:
    resp = SESSION.get(
        f"{MVG_API}/departures",
        params={"globalId": global_id, "limit": limit},
        timeout=20,
    )
    resp.raise_for_status()
    return resp.json()


def snapshot() -> None:
    fetched_at = datetime.now(timezone.utc)
    out_dir = RAW_DEPARTURES / f"date={fetched_at:%Y-%m-%d}"
    out_dir.mkdir(parents=True, exist_ok=True)
    # gzip: ~350 KB -> ~15 KB per snapshot, keeps the git repo small
    out_file = out_dir / f"{fetched_at:%H%M%S}.jsonl.gz"

    total = 0
    with gzip.open(out_file, "wt", encoding="utf-8") as f:
        for gid, name in STATIONS.items():
            try:
                rows = fetch_station(gid)
            except requests.RequestException as e:
                print(f"  ! {name}: {e}")
                continue
            for r in rows:
                r["_fetched_at"] = fetched_at.isoformat()
                r["_station_query"] = gid
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            total += len(rows)
            time.sleep(0.5)  # be polite to an unofficial API
    print(f"{fetched_at:%Y-%m-%d %H:%M:%S}Z  {total} departures -> {out_file.name}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--every", type=int, help="poll interval in seconds (loop until Ctrl+C)")
    args = ap.parse_args()

    if args.every:
        while True:
            snapshot()
            time.sleep(args.every)
    else:
        snapshot()
