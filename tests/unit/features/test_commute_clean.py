"""GTFS calls made usable for routing without inventing times (CORE-009, D-220)."""

from collections.abc import Sequence

import pandas as pd

from hi_features.commute import clean_trips

M = 60


def calls(rows: Sequence[tuple[str, int, float]], route: str = "L1") -> pd.DataFrame:
    """(trip, time, x in metres); stops on a straight line, y = 0; one line unless a trip id
    says otherwise («L2/t»)."""
    return pd.DataFrame(
        {
            "trip_id": [r[0] for r in rows],
            "route_id": [r[0].split("/")[0] if "/" in r[0] else route for r in rows],
            "time": [r[1] for r in rows],
            "x": [r[2] for r in rows],
            "y": [0.0] * len(rows),
        }
    )


def test_stops_between_two_timepoints_are_interpolated_by_distance() -> None:
    out, stats = clean_trips(
        calls([("t", 0, 0), ("t", 0, 1000), ("t", 0, 2000), ("t", 9 * M, 3000)])
    )
    assert out["time"].tolist() == [0, 3 * M, 6 * M, 9 * M]
    assert stats["calls_interpolated"] == 2


def test_after_the_last_timepoint_times_follow_the_speed_of_the_line() -> None:
    """CRTM interurbanos: some trips give every stop the first stop's time."""
    timed = [("timed", 0, 0.0), ("timed", 10 * M, 6000.0)]  # 10 m/s
    flat = [("flat", 8 * 3600, x) for x in (0.0, 1000.0, 5000.0, 20000.0)]
    out, stats = clean_trips(calls(timed + flat))
    got = out.loc[out["trip_id"] == "flat", "time"].tolist()
    assert got == [8 * 3600, 8 * 3600 + 100, 8 * 3600 + 500, 8 * 3600 + 2000]
    assert stats["calls_estimated_by_speed"] == 3
    assert stats["trips_estimated_by_speed"] == 1
    assert stats["lines_without_any_time"] == 0


def test_a_line_without_any_time_takes_the_speed_of_the_feed() -> None:
    timed = [("L1/a", 0, 0.0), ("L1/a", 10 * M, 3000.0), ("L1/b", 0, 0.0), ("L1/b", 5 * M, 3000.0)]
    flat = [("L2/c", 0, 0.0), ("L2/c", 0, 1000.0)]
    out, stats = clean_trips(calls(timed + flat))
    assert out.loc[out["trip_id"] == "L2/c", "time"].tolist() == [0, 133]  # median 7.5 m/s
    assert stats["lines_without_any_time"] == 1


def test_a_trip_going_back_in_time_is_left_out() -> None:
    rows = [("bad", 10 * M, 0), ("bad", 5 * M, 1000), ("ok", 0, 0), ("ok", 3 * M, 1000)]
    out, stats = clean_trips(calls(rows))
    assert set(out["trip_id"]) == {"ok"}
    assert stats["trips_going_back"] == 1


def test_a_trip_faster_than_a_train_is_left_out() -> None:
    rows = [("fast", 0, 0), ("fast", 1 * M, 20000), ("bus", 0, 0), ("bus", 2 * M, 1000)]
    out, stats = clean_trips(calls(rows))
    assert set(out["trip_id"]) == {"bus"}
    assert stats["trips_too_fast"] == 1


def test_published_times_are_kept() -> None:
    rows = [("t", 0, 0), ("t", 2 * M, 700), ("t", 5 * M, 1500)]
    out, stats = clean_trips(calls(rows))
    assert out["time"].tolist() == [0, 2 * M, 5 * M]
    assert stats == {
        "trips_going_back": 0,
        "calls_interpolated": 0,
        "calls_estimated_by_speed": 0,
        "trips_estimated_by_speed": 0,
        "lines_without_any_time": 0,
        "trips_too_fast": 0,
    }
