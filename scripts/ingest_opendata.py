"""Download CSV resources of an opendata.muenchen.de dataset and load them into DuckDB.

Usage:
    python scripts/ingest_opendata.py                 # default: oktoberfest
    python scripts/ingest_opendata.py <dataset-slug>  # any CKAN dataset on the portal

Tables land in schema raw_<slug>, named after the CSV file.
"""
import re
import sys
from datetime import date

import duckdb
import requests

from config import CKAN_API, RAW_OPENDATA, WAREHOUSE


def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


def ingest(dataset: str) -> None:
    meta = requests.get(f"{CKAN_API}/package_show", params={"id": dataset}, timeout=30)
    meta.raise_for_status()
    pkg = meta.json()["result"]
    print(f"{pkg['title']}  (license: {pkg.get('license_id')})")

    folder = RAW_OPENDATA / dataset / date.today().isoformat()
    folder.mkdir(parents=True, exist_ok=True)
    schema = f"raw_{slugify(dataset)}"

    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE))
    con.execute(f"CREATE SCHEMA IF NOT EXISTS {schema}")

    for res in pkg["resources"]:
        if res.get("format", "").upper() != "CSV":
            continue
        filename = res["url"].rsplit("/", 1)[-1]
        path = folder / filename
        resp = requests.get(res["url"], timeout=60)
        resp.raise_for_status()
        path.write_bytes(resp.content)

        table = slugify(path.stem)
        con.execute(
            f"""
            CREATE OR REPLACE TABLE {schema}.{table} AS
            SELECT * FROM read_csv('{path.as_posix()}', header=true, nullstr=['NA', ''])
            """
        )
        n = con.execute(f"SELECT count(*) FROM {schema}.{table}").fetchone()[0]
        print(f"  {schema}.{table:<55} {n:>6,} rows  <- {res['name']}")
    con.close()


if __name__ == "__main__":
    ingest(sys.argv[1] if len(sys.argv) > 1 else "oktoberfest")
