"""Commute times by public transport from every zone to the places one can work (CORE-009, D-220).

Inputs: the last valid version of each CRTM GTFS feed (its reference weekday, as D-196), the
census sections (origins: their point on surface; sections hold similar populations, so the
zone value is the median of its sections) and the rail stations of `place_master` plus the
population centre of each zone (destinations, «hubs»). Walking is in a straight line times a
detour factor, at the 4 km/h of D-211. Output: `transit_hub` and `commute_time`.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from numpy.typing import NDArray
from pyproj import Transformer
from scipy.spatial import KDTree
from scipy.spatial.distance import cdist
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import GtfsFeedPipeline
from hi_domain.access.transit import (
    DETOUR,
    Access,
    ArriveByNetwork,
    FloatArray,
    Footpaths,
    StopTimes,
    latest_leave,
    walk_seconds,
    zone_medians,
)
from hi_features import walk
from hi_ingestion.bronze import REPO_ROOT
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.gtfs.feed import iter_stop_times, open_feed, read_tables
from hi_ingestion.pipelines.gtfs.service_day import parse_gtfs_time, reference_day

METHOD_VERSION = "commute-0.1"
FOOTPATH_M = 250  # changes on foot between stops
ACCESS_M = 1000  # home -> stop and stop -> destination, ~20 min on foot at most
TRANSFER_S = 120  # change at the same stop
# Residential streets of D-210: where people live along the walking network.
ORIGIN_HIGHWAYS = ("residential", "living_street", "unclassified", "pedestrian", "tertiary")
MAX_KMH = 120  # straight-line average speed above which a trip's times are not real
WINDOW_START = 5 * 3600 + 30 * 60
ARRIVE_BY = (8 * 3600 + 30 * 60, 8 * 3600 + 45 * 60, 9 * 3600)
STATION_MODES = ("metro", "cercanias", "metro_ligero")
MODE_WORD = {"metro": "metro", "cercanias": "Cercanías", "metro_ligero": "Metro Ligero"}
CODE_LENGTH = {"municipio": 5, "distrito": 7}
MADRID = "28079"

_VERSION = text(
    """
    SELECT id, bronze_manifest_path, version_label FROM dataset_version
     WHERE dataset_id = :dataset_id AND is_last_valid
    """
)
_SECTIONS = text(
    """
    SELECT code_official, ST_X(p) AS lon, ST_Y(p) AS lat
      FROM (SELECT code_official, ST_PointOnSurface(geom_4326) AS p
              FROM geo_admin_unit WHERE level = 'seccion_censal') s
     ORDER BY 1
    """
)
_ZONES = text(
    """
    SELECT admin_unit_id, code_official, level, name FROM geo_admin_unit
     WHERE level = 'municipio' OR (level = 'distrito' AND code_official LIKE :madrid)
     ORDER BY admin_unit_id
    """
)
_STATIONS = text(
    """
    SELECT canonical_name, subcategory, ST_X(geom_4326) AS lon, ST_Y(geom_4326) AS lat
      FROM place_master
     WHERE category = 'transport' AND status = 'ACTIVE' AND subcategory = ANY(:modes)
    """
)
_TO_METRES = Transformer.from_crs(4326, 25830, always_xy=True)


def _metres(lon: NDArray[np.float64], lat: NDArray[np.float64]) -> NDArray[np.float64]:
    x, y = _TO_METRES.transform(lon, lat)
    return np.c_[x, y]


@dataclass(frozen=True)
class FeedDay:
    dataset_id: str
    version_id: str
    version_label: str
    service_date: str
    events: pd.DataFrame  # trip_id, stop_id, time, boardable (prefixed with the dataset id)
    stops: pd.DataFrame  # stop_id, lon, lat
    cleaning: dict[str, int]  # what clean_trips changed (bad data)


def _bronze_zip(manifest_path: str) -> Path:
    manifest = Path(manifest_path)
    manifest = manifest if manifest.is_absolute() else REPO_ROOT / manifest
    content: dict[str, Any] = json.loads(manifest.read_text())
    inputs: list[dict[str, Any]] = content.get("inputs") or content["files"]
    primary = next(i for i in inputs if i.get("role", "primary") == "primary")
    path = Path(str(primary["path"]))
    return path if path.is_absolute() else REPO_ROOT / path


def _expand(calls: pd.DataFrame, frequencies: pd.DataFrame) -> pd.DataFrame:
    """Frequency-based trips are templates: repeat their offsets every headway."""
    templated = list(set(frequencies["trip_id"]))
    if not templated:
        return calls
    template = calls.loc[calls["trip_id"].isin(templated)]
    offset = template["time"] - template.groupby("trip_id")["time"].transform("min")
    template = template.assign(offset=offset)
    freq = frequencies.assign(
        start=frequencies["start_time"].map(parse_gtfs_time),
        end=frequencies["end_time"].map(parse_gtfs_time),
        headway=pd.to_numeric(frequencies["headway_secs"], errors="coerce"),
    ).dropna(subset=["start", "end", "headway"])
    freq = freq.loc[freq["headway"] > 0]
    starts = [
        (row.trip_id, f"{row.trip_id}@{s}", s)
        for row in freq.itertuples()
        for s in range(int(row.start), int(row.end), int(row.headway))
    ]
    runs = pd.DataFrame(starts, columns=["trip_id", "run", "start"])
    repeated = template.merge(runs, on="trip_id")
    repeated = repeated.assign(time=repeated["start"] + repeated["offset"], trip_id=repeated["run"])
    plain = calls.loc[~calls["trip_id"].isin(templated)]
    return pd.concat([plain, repeated[calls.columns]], ignore_index=True)


def _number(raw: object) -> float:
    try:
        return float(str(raw))
    except ValueError:
        return float("nan")


def _per_trip(trip: NDArray[np.str_]) -> tuple[NDArray[np.str_], NDArray[np.intp]]:
    codes, inverse = np.unique(trip, return_inverse=True)
    return codes, inverse


def _speeds(
    trip: NDArray[np.str_], route: NDArray[np.str_], timed_m: FloatArray, timed_s: FloatArray
) -> tuple[dict[str, float], float]:
    """Straight-line speed (m/s) of the timed part of each trip -> median per line and overall."""
    codes, inverse = _per_trip(trip)
    metres = np.zeros(len(codes))
    seconds = np.zeros(len(codes))
    np.maximum.at(metres, inverse, timed_m)
    np.maximum.at(seconds, inverse, timed_s)
    line = np.empty(len(codes), dtype=route.dtype)
    line[inverse] = route
    speed = np.divide(metres, seconds, out=np.full(len(codes), np.nan), where=seconds >= 60)
    ok = np.isfinite(speed) & (speed > 0) & (speed * 3.6 <= MAX_KMH)
    by_route = {str(r): float(np.median(speed[ok & (line == r)])) for r in set(line[ok].tolist())}
    overall = float(np.median(speed[ok])) if ok.any() else float("nan")
    return by_route, overall


def clean_trips(calls: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Make a day's calls usable for routing (D-220).

    `calls` holds trip_id, route_id, time and projected x, y, in travel order per trip.
    - A trip whose times go back is left out.
    - Stops with the same time as the stop before (only the first is a timepoint) get times
      interpolated by distance up to the next timepoint, as GTFS does with non-timepoint stops.
    - After a trip's last timepoint (CRTM bus feeds publish some trips with one time for every
      stop) times are estimated by distance at the median straight-line speed of the trips of
      the same line that do publish them, or of the whole feed if none does. Declared estimate.
    - A trip faster than MAX_KMH on average in a straight line is left out.
    """
    trip = calls["trip_id"].to_numpy().astype(str)
    route = calls["route_id"].to_numpy().astype(str)
    time = calls["time"].to_numpy(dtype=np.float64)
    n = len(time)
    new_trip = np.r_[True, trip[1:] != trip[:-1]]
    back = np.r_[False, (~new_trip[1:]) & (time[1:] < time[:-1])]
    back_trips = set(trip[back].tolist())
    hop = np.r_[0.0, np.hypot(np.diff(calls["x"].to_numpy()), np.diff(calls["y"].to_numpy()))]
    hop[new_trip] = 0.0
    trip_start = np.flatnonzero(new_trip)
    sizes = np.diff(np.r_[trip_start, n])
    dist = np.cumsum(hop) - np.repeat(np.cumsum(hop)[trip_start], sizes)
    start_time = np.repeat(time[trip_start], sizes)
    run_start = new_trip | np.r_[True, time[1:] != time[:-1]]
    run = np.cumsum(run_start) - 1
    first = np.flatnonzero(run_start)
    next_first = np.minimum(np.r_[first[1:], n], n - 1)
    has_next = np.r_[~new_trip[first[1:]], False]
    a, b = first[run], next_first[run]
    interpolate = (~run_start) & has_next[run]
    span = dist[b] - dist[a]
    share = np.where(interpolate & (span > 0), (dist - dist[a]) / np.where(span > 0, span, 1), 0.0)
    estimated = (~run_start) & ~has_next[run]
    timed = run_start  # timepoints: where the published time changes
    by_route, overall = _speeds(
        trip, route, np.where(timed, dist, 0.0), np.where(timed, time - start_time, 0.0)
    )
    speed = np.array([by_route.get(r, overall) for r in route], dtype=np.float64)
    no_times = {r for r in set(route[estimated].tolist()) if r not in by_route}
    time = np.where(interpolate, time[a] + share * (time[b] - time[a]), time)
    time = np.where(estimated, time[a] + (dist - dist[a]) / speed, time)
    usable = np.isfinite(time)
    out = calls.assign(time=np.round(np.where(usable, time, 0)).astype(np.int64)).loc[usable]
    codes, inverse = _per_trip(trip[usable])
    metres = np.bincount(inverse, weights=hop[usable], minlength=len(codes))
    earliest = np.full(len(codes), np.inf)
    latest = np.full(len(codes), -np.inf)
    np.minimum.at(earliest, inverse, time[usable])
    np.maximum.at(latest, inverse, time[usable])
    fast = metres / (latest - earliest + 60) * 3.6 > MAX_KMH
    fast_trips = set(codes[fast].tolist())
    out = out.loc[~out["trip_id"].isin(list(back_trips | fast_trips))]
    stats = {
        "trips_going_back": len(back_trips),
        "calls_interpolated": int(interpolate.sum()),
        "calls_estimated_by_speed": int(estimated.sum()),
        "trips_estimated_by_speed": len(set(trip[estimated].tolist())),
        "lines_without_any_time": len(no_times),
        "trips_too_fast": len(fast_trips - back_trips),
    }
    return out, stats


def load_feed(engine: Engine, spec: GtfsFeedPipeline) -> FeedDay:
    with engine.connect() as conn:
        row = conn.execute(_VERSION, {"dataset_id": spec.dataset_id}).mappings().first()
    if row is None:
        msg = f"{spec.dataset_id} has no valid version: make ingest DATASET={spec.dataset_id}"
        raise LookupError(msg)
    archive = open_feed(_bronze_zip(str(row["bronze_manifest_path"])))
    tables = read_tables(archive)
    day = reference_day(tables, spec.reference_weekday)
    trips = set(tables.trips.loc[tables.trips["service_id"].isin(list(day.services)), "trip_id"])
    raw = pd.concat(list(iter_stop_times(archive, trips)), ignore_index=True)
    calls = pd.DataFrame(
        {
            "trip_id": raw["trip_id"],
            "stop_id": raw["stop_id"],
            "seq": pd.to_numeric(raw["stop_sequence"], errors="coerce"),
            "time": raw["departure_time"].map(parse_gtfs_time),
            "boardable": raw["pickup_type"].str.strip() != "1",
        }
    ).dropna(subset=["seq", "time"])
    line = dict(zip(tables.trips["trip_id"], tables.trips["route_id"], strict=True))
    calls = calls.assign(route_id=[line.get(t, t) for t in calls["trip_id"]])
    if spec.expand_frequencies:
        frequencies = tables.frequencies.loc[tables.frequencies["trip_id"].isin(list(trips))]
        calls = _expand(calls, frequencies)
    stop_lon = dict(zip(tables.stops["stop_id"], tables.stops["stop_lon"], strict=True))
    stop_lat = dict(zip(tables.stops["stop_id"], tables.stops["stop_lat"], strict=True))
    lon = np.array([_number(stop_lon.get(s)) for s in calls["stop_id"]], dtype=np.float64)
    lat = np.array([_number(stop_lat.get(s)) for s in calls["stop_id"]], dtype=np.float64)
    xy = _metres(lon, lat)
    calls = calls.assign(x=xy[:, 0], y=xy[:, 1]).dropna(subset=["x", "y"])
    calls, cleaning = clean_trips(calls.sort_values(["trip_id", "seq"], kind="stable"))
    calls = calls.loc[(calls["time"] >= WINDOW_START) & (calls["time"] <= max(ARRIVE_BY))]
    prefix = f"{spec.dataset_id}:"
    events = pd.DataFrame(
        {
            "trip_id": prefix + calls["trip_id"],
            "stop_id": prefix + calls["stop_id"],
            "time": calls["time"].astype("int64"),
            "boardable": calls["boardable"],
        }
    )
    stops = pd.DataFrame(
        {
            "stop_id": prefix + tables.stops["stop_id"],
            "lon": pd.to_numeric(tables.stops["stop_lon"], errors="coerce"),
            "lat": pd.to_numeric(tables.stops["stop_lat"], errors="coerce"),
        }
    ).dropna()
    return FeedDay(
        spec.dataset_id,
        str(row["id"]),
        str(row["version_label"]),
        day.service_date.isoformat(),
        events,
        stops,
        cleaning,
    )


@dataclass(frozen=True)
class Timetable:
    network: ArriveByNetwork
    stop_xy: NDArray[np.float64]
    feeds: list[dict[str, str]]


def build_timetable(feeds: list[FeedDay]) -> Timetable:
    events = pd.concat([f.events for f in feeds], ignore_index=True)
    stops = pd.concat([f.stops for f in feeds], ignore_index=True).drop_duplicates("stop_id")
    stops = stops.loc[stops["stop_id"].isin(list(set(events["stop_id"])))].reset_index(drop=True)
    index = {stop_id: i for i, stop_id in enumerate(stops["stop_id"])}
    xy = _metres(stops["lon"].to_numpy(float), stops["lat"].to_numpy(float))
    pairs = KDTree(xy).query_pairs(FOOTPATH_M, output_type="ndarray")
    seconds = walk_seconds(np.hypot(*(xy[pairs[:, 0]] - xy[pairs[:, 1]]).T))
    footpaths = Footpaths(
        np.r_[pairs[:, 0], pairs[:, 1]].astype(np.int64),
        np.r_[pairs[:, 1], pairs[:, 0]].astype(np.int64),
        np.r_[seconds, seconds],
    )
    _, trip = np.unique(events["trip_id"].to_numpy(), return_inverse=True)
    stop_times = StopTimes(
        trip=trip.astype(np.int64),
        stop=np.array([index[s] for s in events["stop_id"]], dtype=np.int64),
        time=events["time"].to_numpy().astype(np.int64),
        boardable=events["boardable"].to_numpy().astype(bool),
        n_stops=len(stops),
    )
    feeds_used = [
        {
            "dataset_id": f.dataset_id,
            "dataset_version_id": f.version_id,
            "version_label": f.version_label,
            "service_date": f.service_date,
            **{k: str(v) for k, v in f.cleaning.items()},
        }
        for f in feeds
    ]
    return Timetable(ArriveByNetwork.build(stop_times, footpaths, TRANSFER_S), xy, feeds_used)


@dataclass(frozen=True)
class Origins:
    xy: NDArray[np.float64]
    zone: NDArray[np.int64]  # index into zone_ids
    zone_ids: list[str]
    access: Access


@dataclass(frozen=True)
class Hub:
    hub_id: str
    kind: str
    label: str
    subcategory: str | None
    admin_unit_id: str | None
    lon: float
    lat: float


def _zone_of_section(code: str, zones: dict[str, str]) -> str | None:
    if code.startswith(MADRID):
        return zones.get(code[: CODE_LENGTH["distrito"]])
    return zones.get(code[: CODE_LENGTH["municipio"]])


def street_points(engine: Engine, codes: list[str]) -> NDArray[np.float64]:
    """Where each census section lives: the node of its residential streets (D-210) closest to
    their length-weighted centre. A large rural section's point on surface can fall in the
    fields, kilometres from the village. NaN where the section has no such street."""
    version = walk.network_version(engine)
    origins = walk.origins(engine, version.path, ORIGIN_HIGHWAYS)
    network = walk.routable(version.path).network
    x, y = network.node_x[origins.node], network.node_y[origins.node]
    frame = pd.DataFrame({"section": origins.section, "x": x, "y": y, "w": origins.weight})
    frame = frame.loc[frame["section"] != ""]
    out = np.full((len(codes), 2), np.nan)
    position = {code: i for i, code in enumerate(codes)}
    for section, group in frame.groupby("section"):
        i = position.get(str(section))
        if i is None:
            continue
        w = group["w"].to_numpy(float)
        pts = group[["x", "y"]].to_numpy(float)
        centre = (pts * w[:, None]).sum(axis=0) / w.sum()
        out[i] = pts[int(np.argmin(np.hypot(*(pts - centre).T)))]
    return out


def load_origins(engine: Engine, timetable: Timetable) -> tuple[Origins, pd.DataFrame]:
    with engine.connect() as conn:
        sections = pd.DataFrame(conn.execute(_SECTIONS).mappings().all())
        zones = pd.DataFrame(conn.execute(_ZONES, {"madrid": f"{MADRID}%"}).mappings().all())
    # Madrid is a zone and its 21 districts too: a section counts for both.
    by_code = dict(zip(zones["code_official"], zones["admin_unit_id"], strict=True))
    rows: list[tuple[int, str]] = []
    for i, code in enumerate(sections["code_official"]):
        district = _zone_of_section(code, by_code)
        if district is not None:
            rows.append((i, district))
        if code.startswith(MADRID) and MADRID in by_code:
            rows.append((i, by_code[MADRID]))
    zone_ids = sorted(zones["admin_unit_id"])
    zone_index = {z: k for k, z in enumerate(zone_ids)}
    origin_section = np.array([r[0] for r in rows], dtype=np.int64)
    origin_zone = np.array([zone_index[r[1]] for r in rows], dtype=np.int64)
    section_xy = _metres(sections["lon"].to_numpy(float), sections["lat"].to_numpy(float))
    on_streets = street_points(engine, sections["code_official"].tolist())
    found = ~np.isnan(on_streets[:, 0])
    section_xy[found] = on_streets[found]
    xy = section_xy[origin_section]
    near = KDTree(timetable.stop_xy).query_ball_point(xy, ACCESS_M)
    origin = np.repeat(np.arange(len(xy)), [len(n) for n in near]).astype(np.int64)
    stop = np.concatenate([np.asarray(n, dtype=np.int64) for n in near])
    seconds = walk_seconds(np.hypot(*(xy[origin] - timetable.stop_xy[stop]).T))
    access = Access(origin, stop, seconds, len(xy))
    return Origins(xy, origin_zone, zone_ids, access), zones


def _title(name: str) -> str:
    small = {"de", "del", "la", "las", "los", "el", "y"}
    words = name.lower().split()
    return " ".join(w if i and w in small else w[:1].upper() + w[1:] for i, w in enumerate(words))


def station_hubs(engine: Engine) -> list[Hub]:
    with engine.connect() as conn:
        rows = pd.DataFrame(
            conn.execute(_STATIONS, {"modes": list(STATION_MODES)}).mappings().all()
        )
    means = rows.groupby(["canonical_name", "subcategory"], as_index=False)[["lon", "lat"]].mean()
    hubs: list[Hub] = []
    for r in pd.DataFrame(means).to_dict("records"):
        name, mode = str(r["canonical_name"]), str(r["subcategory"])
        label = f"{_title(name)} ({MODE_WORD[mode]})"
        hub_id = f"estacion:{mode}:{name.lower()}"
        hubs.append(Hub(hub_id, "station", label, mode, None, float(r["lon"]), float(r["lat"])))
    return hubs


def zone_hubs(origins: Origins, zones: pd.DataFrame) -> list[Hub]:
    """The population centre of a zone: its section closest to all the others (medoid)."""
    names = dict(zip(zones["admin_unit_id"], zones["name"], strict=True))
    to_lonlat = Transformer.from_crs(25830, 4326, always_xy=True)
    hubs: list[Hub] = []
    for k, zone_id in enumerate(origins.zone_ids):
        xy = origins.xy[origins.zone == k]
        if len(xy) == 0:
            continue
        total = cdist(xy, xy).sum(axis=1)
        x, y = xy[int(np.argmin(total))]
        lon, lat = to_lonlat.transform(x, y)
        hubs.append(Hub(f"zona:{zone_id}", "zone", str(names[zone_id]), None, zone_id, lon, lat))
    return hubs


def hub_minutes(timetable: Timetable, origins: Origins, hub: Hub) -> pd.DataFrame:
    """Minutes from each zone to the hub: per section, the median over the arrival times of
    (arrival - latest leave time, or walking all the way if shorter); per zone, the median of
    its sections (unreachable sections count as the slowest)."""
    hub_xy = _metres(np.array([hub.lon]), np.array([hub.lat]))[0]
    egress = np.asarray(KDTree(timetable.stop_xy).query_ball_point(hub_xy, ACCESS_M), np.int64)
    egress_s = walk_seconds(np.hypot(*(timetable.stop_xy[egress] - hub_xy).T))
    walk_only = walk_seconds(np.hypot(*(origins.xy - hub_xy).T)).astype(np.float64)
    per_arrival = []
    for arrive_by in ARRIVE_BY:
        latest = timetable.network.latest_departures(egress, egress_s, arrive_by)
        leave = latest_leave(latest, origins.access)
        per_arrival.append(np.minimum(arrive_by - leave, walk_only))
    section_s = np.median(np.vstack(per_arrival), axis=0)
    section_s[section_s > arrive_window()] = np.inf
    medians, sections, reached = zone_medians(section_s, origins.zone, len(origins.zone_ids))
    frame = pd.DataFrame(
        {
            "hub_id": hub.hub_id,
            "origin_admin_unit_id": origins.zone_ids,
            "minutes": np.where(np.isfinite(medians), np.round(medians / 60, 1), np.nan),
            "sections": sections,
            "sections_reached": reached,
        }
    )
    return frame.loc[frame["sections"] > 0]  # a zone without sections has no value


def arrive_window() -> int:
    """Longest trip the timetable window can hold for the earliest arrival time."""
    return min(ARRIVE_BY) - WINDOW_START


def gtfs_specs(catalog: Catalog) -> list[GtfsFeedPipeline]:
    return [p for p in catalog.pipelines.values() if isinstance(p, GtfsFeedPipeline)]


@dataclass(frozen=True)
class CommuteMatrix:
    hubs: list[Hub]
    times: pd.DataFrame
    inputs: dict[str, Any]


def compute_commutes(engine: Engine, catalog: Catalog) -> CommuteMatrix:
    specs = sorted(gtfs_specs(catalog), key=lambda s: s.dataset_id)
    feeds = [load_feed(engine, spec) for spec in specs]
    timetable = build_timetable(feeds)
    origins, zones = load_origins(engine, timetable)
    hubs = station_hubs(engine) + zone_hubs(origins, zones)
    frames = [hub_minutes(timetable, origins, hub) for hub in hubs]
    inputs = {
        "feeds": timetable.feeds,
        "arrive_by": [f"{t // 3600:02d}:{t % 3600 // 60:02d}" for t in ARRIVE_BY],
        "window_start": f"{WINDOW_START // 3600:02d}:{WINDOW_START % 3600 // 60:02d}",
        "walk_km_h": 4,
        "detour": DETOUR,
        "footpath_m": FOOTPATH_M,
        "access_m": ACCESS_M,
        "transfer_s": TRANSFER_S,
    }
    return CommuteMatrix(hubs, pd.concat(frames, ignore_index=True), inputs)


_DELETE = text("DELETE FROM transit_hub")
_INSERT_HUB = text(
    """
    INSERT INTO transit_hub (hub_id, kind, label, subcategory, admin_unit_id, geom_4326,
                             method_version, inputs)
    VALUES (:hub_id, :kind, :label, :subcategory, :admin_unit_id,
            ST_SetSRID(ST_MakePoint(:lon, :lat), 4326), :method_version, CAST(:inputs AS jsonb))
    """
)
_INSERT_TIME = text(
    """
    INSERT INTO commute_time (hub_id, origin_admin_unit_id, minutes, sections, sections_reached)
    VALUES (:hub_id, :origin_admin_unit_id, :minutes, :sections, :sections_reached)
    """
)


def persist(engine: Engine, matrix: CommuteMatrix) -> int:
    """Replace the whole matrix in one transaction (it is recomputed as a unit)."""
    inputs = json.dumps(matrix.inputs)
    hub_rows = [
        {**h.__dict__, "method_version": METHOD_VERSION, "inputs": inputs} for h in matrix.hubs
    ]
    time_rows = [
        {**r, "minutes": None if pd.isna(r["minutes"]) else float(r["minutes"])}
        for r in matrix.times.to_dict("records")
    ]
    with engine.begin() as conn:
        conn.execute(_DELETE)
        conn.execute(_INSERT_HUB, hub_rows)
        conn.execute(_INSERT_TIME, time_rows)
    return len(time_rows)
