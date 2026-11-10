"""GTFS service levels on a hand-built feed whose expected values are worked out by hand."""

import zipfile
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from hi_contracts.catalog.pipeline import GtfsFeedPipeline
from hi_ingestion.pipelines.gtfs.feed import GtfsFeedError, open_feed, read_tables
from hi_ingestion.pipelines.gtfs.parse import parse_feed
from hi_ingestion.pipelines.gtfs.service_day import parse_gtfs_time, reference_day

STOPS = """stop_id,stop_name,stop_lat,stop_lon,location_type,parent_station,wheelchair_boarding
STA,Estación Sol,40.4169,-3.7035,1,,1
P1,Andén 1,40.4168,-3.7034,0,STA,
P2,Andén 2,40.4170,-3.7036,0,STA,
E1,Acceso,40.4171,-3.7037,2,STA,
S3,Parada Mayor,40.4155,-3.7074,0,,2
S4,Parada sin subida,40.4150,-3.7080,0,,
"""
ROUTES = """route_id,route_short_name,route_type
R1,1,1
R2,,3
"""
TRIPS = """route_id,service_id,trip_id,direction_id
R1,WK,T1,0
R1,WK,T2,1
R2,WK,T3,0
R1,WK,T4,0
R1,WK,T5,1
R1,SA,T6,0
"""
STOP_TIMES = """trip_id,arrival_time,departure_time,stop_id,stop_sequence,pickup_type
T1,07:00:00,07:00:00,P1,1,
T1,07:05:00,07:05:00,S4,2,1
T1,07:10:00,07:10:00,S3,3,
T2,07:30:00,07:30:00,S3,1,
T2,07:40:00,07:40:00,P2,2,
T3,06:00:00,06:00:00,P2,1,
T3,06:05:00,06:05:00,S3,2,
T3,06:15:00,06:15:00,P1,3,
T4,00:30:00,00:30:00,P1,1,
T4,00:40:00,00:40:00,S3,2,
T5,x,x,S3,1,
T6,07:00:00,07:00:00,P1,1,
T6,07:10:00,07:10:00,S3,2,
"""
CALENDAR = (
    "service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date\n"
)
CALENDAR += """WK,1,1,1,1,1,0,0,20261102,20261130
SA,0,0,0,0,0,1,0,20261102,20261130
"""
CALENDAR_DATES = """service_id,date,exception_type
WK,20261110,2
"""
FREQUENCIES = """trip_id,start_time,end_time,headway_secs
T3,7:00:00,8:00:00,1200
"""
TABLES = {
    "stops": STOPS,
    "routes": ROUTES,
    "trips": TRIPS,
    "stop_times": STOP_TIMES,
    "calendar": CALENDAR,
    "calendar_dates": CALENDAR_DATES,
    "frequencies": FREQUENCIES,
}


def write_feed(path: Path, tables: dict[str, str], folder: str = "") -> Path:
    with zipfile.ZipFile(path, "w") as archive:
        for name, body in tables.items():
            archive.writestr(f"{folder}{name}.txt", "﻿" + body)
    return path


def _spec(**overrides: Any) -> GtfsFeedPipeline:
    return GtfsFeedPipeline.model_validate(
        {"kind": "gtfs_feed", "dataset_id": "crtm_gtfs_test", "mode": "metro", **overrides}
    )


def _rows(path: Path, **overrides: Any) -> dict[str, dict[str, Any]]:
    frame = parse_feed(path, _spec(**overrides))
    return {str(r["stop_id"]): r for r in frame.to_dict("records")}  # pyright: ignore[reportUnknownVariableType]


@pytest.fixture
def feed(tmp_path: Path) -> Path:
    return write_feed(tmp_path / "feed.zip", TABLES)


@given(st.integers(0, 47), st.integers(0, 59), st.integers(0, 59))
def test_gtfs_times_parse_past_midnight(hours: int, minutes: int, seconds: int) -> None:
    assert parse_gtfs_time(f"{hours}:{minutes:02d}:{seconds:02d}") == (
        hours * 3600 + minutes * 60 + seconds
    )


@pytest.mark.parametrize("raw", ["", "x", "7:05", "07:65:00", "07:00:61", "-1:00:00"])
def test_invalid_gtfs_times_are_none(raw: str) -> None:
    assert parse_gtfs_time(raw) is None


def test_reference_day_is_the_median_weekday_and_skips_holidays(feed: Path) -> None:
    with open_feed(feed) as archive:
        day = reference_day(read_tables(archive), "tuesday")
    # Tuesdays 3, 17 and 24 Nov run 5 weekday trips; 10 Nov is a holiday (service removed).
    assert day.candidate_days == 3
    assert day.service_date == date(2026, 11, 17)
    assert day.services == frozenset({"WK"})
    assert day.active_trips == 5
    assert day.feed_end == date(2026, 11, 30)


def test_no_service_on_the_weekday_is_an_error(tmp_path: Path) -> None:
    path = write_feed(tmp_path / "f.zip", TABLES)
    with open_feed(path) as archive:
        tables = read_tables(archive)
    with pytest.raises(GtfsFeedError, match="no sunday"):
        reference_day(tables, "sunday")


def test_station_aggregates_platforms_and_expands_frequencies(feed: Path) -> None:
    rows = _rows(feed)
    assert set(rows) == {"STA", "S3", "S4"}  # entrance E1 and platforms are not places
    station = rows["STA"]
    # T1 07:00 at P1, T3 every 20 min from 07:00 at P2 (3 runs), T4 00:30 at P1.
    assert station["departures_day"] == 5
    assert station["departures_peak_per_hour"] == 2.0
    assert station["headway_peak_min"] == 40.0  # busiest line in the peak: R2, 3 runs in 120'
    assert station["headway_basis"] == "route_direction"
    assert station["first_departure"] == "07:00"
    assert station["last_departure"] == "24:30"  # 00:30 is the previous night's service
    assert station["routes"] == ["1", "R2"]
    assert station["n_routes"] == 2
    assert station["wheelchair_boarding"] == "yes"
    assert station["service_date"] == "2026-11-17"


def test_last_stop_and_no_pickup_are_not_departures(feed: Path) -> None:
    rows = _rows(feed)
    # S3: T2 07:30 plus T3 at 07:05, 07:25, 07:45; T1 and T4 end there.
    assert rows["S3"]["departures_day"] == 4
    assert rows["S3"]["wheelchair_boarding"] == "no"
    assert rows["S4"]["has_service"] == "no"
    assert rows["S4"]["departures_day"] == 0
    assert rows["S4"]["headway_peak_min"] is None
    assert rows["S4"]["routes"] is None


def test_frequencies_can_be_declared_informative(feed: Path) -> None:
    rows = _rows(feed, expand_frequencies=False)
    assert rows["STA"]["departures_day"] == 3  # T3 counted once, at 06:00
    assert rows["S3"]["departures_day"] == 2


def test_feed_stats_and_invalid_times(feed: Path) -> None:
    frame = parse_feed(feed, _spec())
    assert set(frame["invalid_stop_times"]) == {1}  # T5 has no usable time
    assert set(frame["reference_trips"]) == {5}
    assert set(frame["reference_candidate_days"]) == {3}


def test_nested_folder_and_missing_direction(tmp_path: Path) -> None:
    trips = TRIPS.replace(",direction_id", "").replace(",0\n", "\n").replace(",1\n", "\n")
    path = write_feed(tmp_path / "n.zip", {**TABLES, "trips": trips}, folder="google_transit_X/")
    rows = _rows(path)
    assert rows["STA"]["headway_basis"] == "route"
    assert rows["STA"]["departures_day"] == 5


def test_bad_zip_and_missing_tables_fail_loudly(tmp_path: Path) -> None:
    broken = tmp_path / "broken.zip"
    broken.write_bytes(b"not a zip")
    with pytest.raises(GtfsFeedError, match="not a readable GTFS zip"):
        parse_feed(broken, _spec())
    tables = {k: v for k, v in TABLES.items() if k != "stops"}
    with pytest.raises(GtfsFeedError, match=r"stops\.txt"):
        parse_feed(write_feed(tmp_path / "nostops.zip", tables), _spec())


def test_peak_window_must_be_ordered() -> None:
    with pytest.raises(ValidationError, match="peak_end"):
        _spec(peak_start="09:00", peak_end="07:00")


def test_published_columns_have_no_nan(feed: Path) -> None:
    frame = parse_feed(feed, _spec())
    served = frame.loc[frame["has_service"] == "yes"]
    values = [v for row in served.to_dict("records") for v in row.values()]
    assert not any(isinstance(v, float) and pd.isna(v) for v in values)
