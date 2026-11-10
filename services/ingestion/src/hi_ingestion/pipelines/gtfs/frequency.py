"""Boarding departures on the reference day -> service level per stop or parent station."""

from dataclasses import dataclass
from typing import Any, cast

import numpy as np
import pandas as pd

from hi_ingestion.pipelines.gtfs.feed import GtfsTables
from hi_ingestion.pipelines.gtfs.service_day import ServiceDay, parse_gtfs_time

STATION = "1"
# Departures before 04:00 are the previous night's service (some feeds write 00:30, not 24:30).
SERVICE_DAY_START = 4 * 3600
BOARDABLE_LOCATION_TYPES = ("", "0")
NO_PICKUP = "1"
WHEELCHAIR = {"1": "yes", "2": "no"}
SERVICE_KEYS = (
    "has_service",
    "departures_day",
    "departures_peak_per_hour",
    "headway_peak_min",
    "headway_basis",
    "first_departure",
    "last_departure",
    "routes",
    "n_routes",
)


@dataclass(frozen=True)
class PeakWindow:
    start: int  # seconds after the service day's midnight
    end: int

    @classmethod
    def from_clock(cls, start: str, end: str) -> "PeakWindow":
        return cls(_clock_seconds(start), _clock_seconds(end))

    @property
    def minutes(self) -> float:
        return (self.end - self.start) / 60


def _clock_seconds(value: str) -> int:
    hours, minutes = value.split(":")
    return int(hours) * 3600 + int(minutes) * 60


def clock(seconds: int) -> str:
    """Seconds -> 'HH:MM'; GTFS service days may run past 24:00 (e.g. '25:10')."""
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}"


def service_clock(seconds: pd.Series) -> pd.Series:
    """Late-night departures written as 00:xx move to 24:xx so first/last service read right."""
    return seconds.where(seconds >= SERVICE_DAY_START, seconds + 24 * 3600)


def boarding_events(stop_times: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """One day's stop_times -> departures a passenger can board, plus rows without a usable time.

    The last stop of a trip and stops flagged 'no pickup' are not departures.
    """
    frame = stop_times.assign(
        seq=pd.to_numeric(stop_times["stop_sequence"], errors="coerce"),
        dep=stop_times["departure_time"].map(parse_gtfs_time),
    )
    invalid = int(frame["dep"].isna().sum() + frame["seq"].isna().sum())
    frame = frame.dropna(subset=["seq", "dep"])
    trips = frame.groupby("trip_id")
    frame = frame.assign(
        trip_start=trips["dep"].transform("min"), last_seq=trips["seq"].transform("max")
    )
    keep = (frame["seq"] < frame["last_seq"]) & (frame["pickup_type"].str.strip() != NO_PICKUP)
    events = frame.loc[keep, ["trip_id", "stop_id", "dep", "trip_start"]]
    return events.astype({"dep": "int64", "trip_start": "int64"}), invalid


def _frequency_starts(frequencies: pd.DataFrame) -> pd.DataFrame:
    freq = frequencies.assign(
        start=frequencies["start_time"].map(parse_gtfs_time),
        end=frequencies["end_time"].map(parse_gtfs_time),
        headway=pd.to_numeric(frequencies["headway_secs"], errors="coerce"),
    ).dropna(subset=["start", "end", "headway"])
    freq = freq.loc[(freq["headway"] > 0) & (freq["end"] > freq["start"])]
    counts = np.ceil((freq["end"] - freq["start"]) / freq["headway"]).astype("int64").to_numpy()
    step = np.arange(counts.sum()) - np.repeat(np.cumsum(counts) - counts, counts)
    starts = np.repeat(freq["start"].to_numpy(), counts) + step * np.repeat(
        freq["headway"].to_numpy(), counts
    )
    return pd.DataFrame({"trip_id": np.repeat(freq["trip_id"].to_numpy(), counts), "start": starts})


def expand_frequencies(events: pd.DataFrame, frequencies: pd.DataFrame) -> pd.DataFrame:
    """Frequency-based trips are templates: repeat their stop offsets every headway."""
    columns = ["trip_id", "stop_id", "dep"]
    templated = list(set(frequencies["trip_id"]))
    if not templated:
        return cast(pd.DataFrame, events[columns])
    plain = events.loc[~events["trip_id"].isin(templated), columns]
    template = events.loc[events["trip_id"].isin(templated)]
    offsets = template.assign(offset=template["dep"] - template["trip_start"])
    starts = _frequency_starts(
        frequencies.loc[frequencies["trip_id"].isin(list(set(template["trip_id"])))]
    )
    repeated = offsets[["trip_id", "stop_id", "offset"]].merge(starts, on="trip_id")
    repeated = repeated.assign(dep=(repeated["start"] + repeated["offset"]).astype("int64"))
    return pd.concat([plain, repeated[columns]], ignore_index=True)


def _place_key(stop: dict[str, Any]) -> str:
    name = str(stop["stop_name"]).strip().lower()
    return f"{name}|{str(stop['stop_lat']).strip()}|{str(stop['stop_lon']).strip()}"


def _stations_by_place(stations: pd.DataFrame) -> dict[str, str]:
    """Name+position -> station id, only where that place holds exactly one station."""
    found: dict[str, list[str]] = {}
    for station in stations.to_dict("records"):
        found.setdefault(_place_key(station), []).append(str(station["stop_id"]))
    return {key: ids[0] for key, ids in found.items() if len(ids) == 1}


def station_groups(stops: pd.DataFrame) -> dict[str, str]:
    """Boardable stop -> its parent station, else itself.

    Some feeds omit parent_station on one platform of a transfer station (CRTM metro: 25
    stations). A platform without parent that sits exactly where a station of the same name
    is joins that station; otherwise the station would appear twice with half its service.
    """
    location = stops["location_type"].str.strip()
    stations = stops.loc[location == STATION]
    station_ids = set(stations["stop_id"])
    by_place = _stations_by_place(stations)
    groups: dict[str, str] = {}
    for stop in stops.loc[location.isin(BOARDABLE_LOCATION_TYPES)].to_dict("records"):
        stop_id, parent = str(stop["stop_id"]), str(stop["parent_station"]).strip()
        if parent in station_ids:
            groups[stop_id] = parent
        else:
            groups[stop_id] = by_place.get(_place_key(stop), stop_id)
    return groups


def _route_labels(tables: GtfsTables) -> dict[str, str]:
    short = tables.routes["route_short_name"].str.strip()
    labels = short.where(short != "", tables.routes["route_id"])
    return dict(zip(tables.routes["route_id"], labels, strict=True))


def _sorted_routes(labels: pd.Series) -> list[str]:
    unique = {str(v) for v in labels if str(v)}
    return sorted(unique, key=lambda r: (not r.isdigit(), int(r) if r.isdigit() else 0, r))


def _has_direction(trips: pd.DataFrame) -> bool:
    return "direction_id" in trips.columns and bool((trips["direction_id"].str.strip() != "").any())


def service_levels(
    events: pd.DataFrame, tables: GtfsTables, peak: PeakWindow
) -> tuple[pd.DataFrame, str]:
    """Departures per group (all routes and directions) and the busiest line at peak.

    Returns the levels and the headway basis: per route and direction when the feed declares
    direction_id, otherwise per route with both directions together.
    """
    has_direction = _has_direction(tables.trips)
    trip_cols = ["trip_id", "route_id", *(["direction_id"] if has_direction else [])]
    ev = events.merge(tables.trips[trip_cols], on="trip_id", how="left")
    groups, labels = station_groups(tables.stops), _route_labels(tables)
    dep = cast(pd.Series, ev["dep"])
    ev = ev.assign(
        group_id=ev["stop_id"].map(groups.get).fillna(ev["stop_id"]),
        route=ev["route_id"].map(labels.get).fillna(ev["route_id"]),
        direction=ev["direction_id"] if has_direction else "",
        in_peak=(dep >= peak.start) & (dep < peak.end),
        service_dep=service_clock(dep),
    )
    by_group = ev.groupby("group_id")
    peak_lines = ev.loc[ev["in_peak"]].groupby(["group_id", "route", "direction"]).size()
    best_line = peak_lines.groupby(level="group_id").max()
    levels = pd.DataFrame(
        {
            "departures_day": by_group.size(),
            "departures_peak": by_group["in_peak"].sum(),
            "first_dep": by_group["service_dep"].min(),
            "last_dep": by_group["service_dep"].max(),
            "routes": by_group["route"].agg(_sorted_routes),
        }
    )
    levels["best_line_peak"] = best_line.reindex(levels.index)
    return levels, "route_direction" if has_direction else "route"


def _level_attributes(level: dict[str, Any] | None, peak: PeakWindow, basis: str) -> dict[str, Any]:
    if level is None:
        return dict.fromkeys(SERVICE_KEYS) | {"has_service": "no", "departures_day": 0}
    best = level["best_line_peak"]
    return {
        "has_service": "yes",
        "departures_day": int(level["departures_day"]),
        "departures_peak_per_hour": round(int(level["departures_peak"]) * 60 / peak.minutes, 1),
        "headway_peak_min": round(peak.minutes / best, 1) if pd.notna(best) else None,
        "headway_basis": basis,
        "first_departure": clock(int(level["first_dep"])),
        "last_departure": clock(int(level["last_dep"])),
        "routes": level["routes"],
        "n_routes": len(level["routes"]),
    }


def stop_service_table(
    tables: GtfsTables, events: pd.DataFrame, peak: PeakWindow, day: ServiceDay, mode: str
) -> pd.DataFrame:
    """Every stop or parent station of the feed, served or not, with its service attributes."""
    groups = list(set(station_groups(tables.stops).values()))
    places = tables.stops.loc[tables.stops["stop_id"].isin(groups)]
    levels, basis = service_levels(events, tables, peak) if len(events) else (pd.DataFrame(), "")
    by_group: dict[str, dict[str, Any]] = levels.to_dict("index") if len(levels) else {}  # pyright: ignore[reportAssignmentType]
    rows: list[dict[str, Any]] = []
    for stop in places.to_dict("records"):
        rows.append(
            {
                "stop_id": stop["stop_id"],
                "stop_name": str(stop["stop_name"]).strip(),
                "stop_lat": stop["stop_lat"],
                "stop_lon": stop["stop_lon"],
                "mode": mode,
                **_level_attributes(by_group.get(stop["stop_id"]), peak, basis),
                "wheelchair_boarding": WHEELCHAIR.get(str(stop["wheelchair_boarding"]).strip()),
                "service_date": day.service_date.isoformat(),
                "feed_end_date": day.feed_end.isoformat(),
            }
        )
    return pd.DataFrame(rows, dtype=object)
