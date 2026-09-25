"""Download the MVV static GTFS feed and load it into DuckDB (schema: raw_gtfs).

Each run keeps a dated copy of the feed so schedule versions can be compared later.
"""
import io
import zipfile
from datetime import date

import duckdb
import requests

from config import GTFS_URL, RAW_GTFS, WAREHOUSE


def download_feed() -> tuple[str, "Path"]:
    version = date.today().isoformat()
    target = RAW_GTFS / version
    if target.exists() and any(target.glob("*.txt")):
        print(f"Feed for {version} already downloaded -> {target}")
        return version, target

    print(f"Downloading {GTFS_URL} ...")
    resp = requests.get(GTFS_URL, timeout=120)
    resp.raise_for_status()
    target.mkdir(parents=True, exist_ok=True)
    zipfile.ZipFile(io.BytesIO(resp.content)).extractall(target)
    print(f"Extracted {len(resp.content) / 1e6:.1f} MB -> {target}")
    return version, target


def load_to_duckdb(version: str, folder) -> None:
    WAREHOUSE.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(WAREHOUSE))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw_gtfs")
    for txt in sorted(folder.glob("*.txt")):
        table = txt.stem
        # all_varchar: keep raw layer lossless; typing happens in staging models.
        con.execute(
            f"""
            CREATE OR REPLACE TABLE raw_gtfs.{table} AS
            SELECT *, '{version}' AS _feed_version
            FROM read_csv('{txt.as_posix()}', header=true, all_varchar=true)
            """
        )
        n = con.execute(f"SELECT count(*) FROM raw_gtfs.{table}").fetchone()[0]
        print(f"  raw_gtfs.{table:<20} {n:>10,} rows")
    con.close()


if __name__ == "__main__":
    version, folder = download_feed()
    load_to_duckdb(version, folder)
