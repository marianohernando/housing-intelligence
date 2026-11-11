"""Read the GTFS tables the service-level pipeline needs from a feed zip."""

import zipfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import pandas as pd

STOP_TIMES_CHUNK = 500_000
STOP_TIMES_COLUMNS = ["trip_id", "departure_time", "stop_id", "stop_sequence", "pickup_type"]
OPTIONAL_STOP_COLUMNS = ["location_type", "parent_station", "wheelchair_boarding"]


class GtfsFeedError(ValueError):
    """The file is not a usable GTFS feed (bad zip, missing table or column)."""


@dataclass(frozen=True)
class GtfsTables:
    stops: pd.DataFrame
    routes: pd.DataFrame
    trips: pd.DataFrame
    calendar: pd.DataFrame
    calendar_dates: pd.DataFrame
    frequencies: pd.DataFrame


def _members(archive: zipfile.ZipFile) -> dict[str, str]:
    """Table name -> member path; some CRTM feeds nest the files in a folder."""
    return {PurePosixPath(n).name: n for n in archive.namelist() if n.endswith(".txt")}


def _read(
    archive: zipfile.ZipFile, members: dict[str, str], table: str, required: list[str]
) -> pd.DataFrame:
    member = members.get(f"{table}.txt")
    if member is None:
        return pd.DataFrame(columns=required)
    with archive.open(member) as fh:
        frame = pd.read_csv(fh, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    frame.columns = [c.strip() for c in frame.columns]
    missing = [c for c in required if c not in frame.columns]
    if missing and len(frame):
        msg = f"{table}.txt lacks columns {missing}"
        raise GtfsFeedError(msg)
    for column in missing:
        frame[column] = ""
    return frame


def open_feed(path: Path) -> zipfile.ZipFile:
    try:
        return zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as exc:
        msg = f"{path.name} is not a readable GTFS zip: {exc}"
        raise GtfsFeedError(msg) from exc


def read_tables(archive: zipfile.ZipFile) -> GtfsTables:
    members = _members(archive)
    for table in ("stops", "routes", "trips", "stop_times"):
        if f"{table}.txt" not in members:
            msg = f"feed lacks {table}.txt"
            raise GtfsFeedError(msg)
    if "calendar.txt" not in members and "calendar_dates.txt" not in members:
        raise GtfsFeedError("feed lacks calendar.txt and calendar_dates.txt")
    stops = _read(archive, members, "stops", ["stop_id", "stop_name", "stop_lat", "stop_lon"])
    for column in OPTIONAL_STOP_COLUMNS:
        if column not in stops.columns:
            stops[column] = ""
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    return GtfsTables(
        stops=stops,
        routes=_read(archive, members, "routes", ["route_id", "route_short_name"]),
        trips=_read(archive, members, "trips", ["route_id", "service_id", "trip_id"]),
        calendar=_read(
            archive, members, "calendar", ["service_id", *weekdays, "start_date", "end_date"]
        ),
        calendar_dates=_read(
            archive, members, "calendar_dates", ["service_id", "date", "exception_type"]
        ),
        frequencies=_read(
            archive, members, "frequencies", ["trip_id", "start_time", "end_time", "headway_secs"]
        ),
    )


def iter_stop_times(archive: zipfile.ZipFile, trip_ids: set[str]) -> Iterator[pd.DataFrame]:
    """Stream stop_times keeping only the given trips (the reference day's), to bound memory."""
    member = _members(archive)["stop_times.txt"]
    with archive.open(member) as fh:
        header = pd.read_csv(fh, nrows=0, encoding="utf-8-sig").columns
    columns = [c.strip() for c in header]
    missing = [c for c in STOP_TIMES_COLUMNS if c != "pickup_type" and c not in columns]
    if missing:
        msg = f"stop_times.txt lacks columns {missing}"
        raise GtfsFeedError(msg)
    usecols = [c for c in STOP_TIMES_COLUMNS if c in columns]
    with archive.open(member) as fh:
        reader = pd.read_csv(
            fh,
            dtype=str,
            keep_default_na=False,
            encoding="utf-8-sig",
            usecols=lambda c: c.strip() in usecols,
            chunksize=STOP_TIMES_CHUNK,
        )
        for chunk in reader:
            chunk.columns = [c.strip() for c in chunk.columns]
            if "pickup_type" not in chunk.columns:
                chunk["pickup_type"] = ""
            yield chunk.loc[chunk["trip_id"].isin(trip_ids)]
