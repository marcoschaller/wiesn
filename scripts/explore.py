"""First look at what we've collected: GTFS size + live delay snapshot stats."""
import duckdb

from config import RAW_DEPARTURES, WAREHOUSE

con = duckdb.connect(str(WAREHOUSE))

print("=== Static GTFS (MVV) ===")
print(con.sql("""
    SELECT route_type, count(*) AS routes
    FROM raw_gtfs.routes GROUP BY 1 ORDER BY 2 DESC
"""))
print(con.sql("""
    SELECT min(start_date) AS valid_from, max(end_date) AS valid_to
    FROM raw_gtfs.calendar
"""))

print("=== Live departures (MVG) ===")
glob = (RAW_DEPARTURES / "**" / "*.jsonl*").as_posix()
con.execute(f"""
    CREATE OR REPLACE TEMP VIEW departures AS
    SELECT
        _fetched_at::TIMESTAMPTZ                AS fetched_at,
        stationGlobalId                         AS station_id,
        transportType                           AS mode,
        label                                   AS line,
        destination,
        to_timestamp(plannedDepartureTime / 1000)  AS planned_at,
        to_timestamp(realtimeDepartureTime / 1000) AS realtime_at,
        realtime                                AS has_realtime,
        delayInMinutes                          AS delay_min,
        cancelled,
        infos
    FROM read_json_auto('{glob}', format='newline_delimited', union_by_name=true)
""")
print(con.sql("SELECT count(*) AS rows, count(DISTINCT fetched_at) AS snapshots FROM departures"))
print(con.sql("""
    SELECT mode,
           count(*)                                       AS departures,
           round(avg(CASE WHEN has_realtime THEN 1 ELSE 0 END), 2) AS share_realtime,
           round(avg(delay_min), 2)                       AS avg_delay_min,
           max(delay_min)                                 AS max_delay_min,
           sum(CASE WHEN cancelled THEN 1 ELSE 0 END)     AS cancelled
    FROM departures GROUP BY 1 ORDER BY 2 DESC
"""))
print(con.sql("""
    SELECT line, round(avg(delay_min), 1) AS avg_delay_min, count(*) AS n
    FROM departures WHERE has_realtime
    GROUP BY 1 HAVING n >= 3 ORDER BY 2 DESC LIMIT 10
"""))
