"""Build small GTFS fixtures from the Bronze feeds (CRTM open data licence, attribution kept).

For each feed it keeps the reference day's trips that stop inside the admin_sample area (a few per
route), some trips elsewhere and, when the feed has one, a trip with a stop outside the region, so
publication, section assignment and quarantine are all exercised. Only the rows those trips need
are written. Usage: uv run python scripts/build_gtfs_fixtures.py
"""

import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry.base import BaseGeometry

from hi_contracts.catalog.pipeline import GtfsFeedPipeline
from hi_domain.geo.bounds import is_within_madrid
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.gtfs.feed import GtfsTables, iter_stop_times, open_feed, read_tables
from hi_ingestion.pipelines.gtfs.service_day import reference_day

REPO = Path(__file__).resolve().parents[1]
BRONZE = REPO / "data" / "bronze" / "datasets"
SECTIONS = REPO / "data" / "fixtures" / "golden" / "admin_sample" / "sections.gpkg"
OUT = REPO / "data" / "fixtures" / "golden" / "gtfs_sample"
TRIPS_PER_ROUTE_INSIDE = 3
TRIPS_ELSEWHERE = 4
FIXED_ZIP_TIME = (2026, 1, 1, 0, 0, 0)  # byte-identical fixtures across rebuilds


def _latest_zip(dataset_id: str) -> Path:
    return sorted((BRONZE / dataset_id).glob("*/*.zip"), key=lambda p: p.stat().st_mtime)[-1]


def _area() -> BaseGeometry:
    return gpd.read_file(SECTIONS).to_crs(25830).union_all()


def _coords(stops: pd.DataFrame) -> tuple[list[float], list[float]]:
    def num(values: list[str]) -> list[float]:
        out: list[float] = []
        for v in values:
            try:
                out.append(float(v))
            except ValueError:
                out.append(0.0)
        return out

    return num(stops["stop_lon"].tolist()), num(stops["stop_lat"].tolist())


def _stops_inside(stops: pd.DataFrame, area: BaseGeometry) -> set[str]:
    lon, lat = _coords(stops)
    points = gpd.GeoSeries.from_xy(lon, lat, crs=4326).to_crs(25830)
    return {s for s, p in zip(stops["stop_id"], points, strict=True) if area.contains(p)}


def _stops_outside_region(stops: pd.DataFrame) -> set[str]:
    lon, lat = _coords(stops)
    return {
        s for s, x, y in zip(stops["stop_id"], lon, lat, strict=True) if not is_within_madrid(x, y)
    }


def _pick_trips(tables: GtfsTables, stop_times: pd.DataFrame, area: BaseGeometry) -> list[str]:
    inside_stops = _stops_inside(tables.stops, area)
    trips = tables.trips.set_index("trip_id")
    inside = sorted(set(stop_times.loc[stop_times["stop_id"].isin(list(inside_stops)), "trip_id"]))
    picked: list[str] = []
    per_route: dict[str, int] = {}
    for trip in inside:
        route = str(trips.at[trip, "route_id"])
        if per_route.get(route, 0) < TRIPS_PER_ROUTE_INSIDE:
            picked.append(trip)
            per_route[route] = per_route.get(route, 0) + 1
    elsewhere = sorted(set(stop_times["trip_id"]) - set(inside))[:TRIPS_ELSEWHERE]
    outside_stops = list(_stops_outside_region(tables.stops))
    leaving = sorted(set(stop_times.loc[stop_times["stop_id"].isin(outside_stops), "trip_id"]))
    return sorted({*picked, *elsewhere, *leaving[:1]})


def _subset(
    tables: GtfsTables, stop_times: pd.DataFrame, trips: list[str]
) -> dict[str, pd.DataFrame]:
    kept_trips = tables.trips.loc[tables.trips["trip_id"].isin(trips)]
    kept_times = stop_times.loc[stop_times["trip_id"].isin(trips)]
    stop_ids = set(kept_times["stop_id"])
    parents = set(tables.stops.loc[tables.stops["stop_id"].isin(list(stop_ids)), "parent_station"])
    services = list(set(kept_trips["service_id"]))
    return {
        "stops": tables.stops.loc[tables.stops["stop_id"].isin(list(stop_ids | parents))],
        "routes": tables.routes.loc[
            tables.routes["route_id"].isin(list(set(kept_trips["route_id"])))
        ],
        "trips": kept_trips,
        "stop_times": kept_times,
        "calendar": tables.calendar.loc[tables.calendar["service_id"].isin(services)],
        "calendar_dates": tables.calendar_dates.loc[
            tables.calendar_dates["service_id"].isin(services)
        ],
        "frequencies": tables.frequencies.loc[tables.frequencies["trip_id"].isin(trips)],
    }


def build(spec: GtfsFeedPipeline, area: BaseGeometry) -> Path:
    with open_feed(_latest_zip(spec.dataset_id)) as archive:
        tables = read_tables(archive)
        day = reference_day(tables, spec.reference_weekday)
        day_trips = tables.trips.loc[tables.trips["service_id"].isin(sorted(day.services))]
        stop_times = pd.concat(list(iter_stop_times(archive, set(day_trips["trip_id"]))))
    trips = _pick_trips(tables, stop_times, area)
    target = OUT / f"{spec.dataset_id}.zip"
    with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as out:
        for name, frame in _subset(tables, stop_times, trips).items():
            entry = zipfile.ZipInfo(f"{name}.txt", date_time=FIXED_ZIP_TIME)
            out.writestr(entry, frame.to_csv(index=False), zipfile.ZIP_DEFLATED)
    print(f"{spec.dataset_id}: {len(trips)} trips, {target.stat().st_size} bytes")
    return target


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    area = _area()
    for spec in sorted(load_catalog().pipelines.values(), key=lambda s: s.dataset_id):
        if isinstance(spec, GtfsFeedPipeline):
            build(spec, area)


if __name__ == "__main__":
    main()
