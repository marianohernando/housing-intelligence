"""Walking-access feature rows from per-node distances: values, explicit nulls and confidence."""

import math
from datetime import date

import numpy as np
import pandas as pd
import pytest

from hi_features import methods

Y = date(2026, 11, 1)
SPEED = 75.0  # m/min (4.5 km/h)


def _rows(frame: pd.DataFrame) -> dict[str, dict[str, object]]:
    return {str(r["territory_code"]): r for r in frame.to_dict("records")}  # pyright: ignore[reportUnknownVariableType]


def _is_null(value: object) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def _access(statistic: str, min_street_m: float = 250.0) -> pd.DataFrame:
    """Zone A: 3 nodes (75 m, 150 m and 1,500 m away), 100 m of street each. Zone B: 1 node no
    destination can reach. Zone C: no origin street at all. The last node lies in no zone."""
    settings = methods.WalkSettings(statistic, SPEED, 10.0, 1.0, min_street_m)
    return methods.walk_access(
        np.array(["A", "A", "A", "B", ""]),
        np.full(5, 100.0),
        np.array([75.0, 150.0, 1500.0, np.inf, 10.0]),
        ["A", "B", "C"],
        Y,
        settings,
    )


def test_median_minutes_is_the_street_weighted_median() -> None:
    rows = _rows(_access("median_minutes"))
    assert rows["A"]["value"] == 2.0  # 150 m at 75 m/min
    assert rows["A"]["confidence"] == 1.0


def test_share_within_counts_street_length_up_to_the_window() -> None:
    rows = _rows(_access("share_within"))
    assert rows["A"]["value"] == pytest.approx(100.0 * 2 / 3)  # 75 m and 150 m are within 750 m


def test_unreachable_and_streetless_zones_are_explicit_nulls_never_zero() -> None:
    for statistic in ("median_minutes", "share_within"):
        rows = _rows(_access(statistic))
        assert _is_null(rows["B"]["value"]) and rows["B"]["null_reason"] == "UNKNOWN"
        assert _is_null(rows["C"]["value"])
        assert rows["C"]["null_reason"] == "SOURCE_NO_COVERAGE"
        assert rows["B"]["confidence"] == rows["C"]["confidence"] == 0.0


def test_thin_street_coverage_caps_confidence() -> None:
    rows = _rows(_access("median_minutes", min_street_m=1000.0))
    assert rows["A"]["confidence"] == 0.5


def test_regional_reference_pools_every_node_inside_a_zone() -> None:
    frame = _access("median_minutes")
    region = frame.loc[frame["territory_level"] == methods.REGION_LEVEL]
    assert region["territory_code"].tolist() == [methods.REGION_CODE]
    assert region["value"].tolist() == [2.0]  # A's 3 reachable nodes; B unreachable, "" outside
    assert float(region["confidence"].iloc[0]) == 0.75  # 300 of 400 m of street reachable


def test_unknown_statistic_is_rejected() -> None:
    with pytest.raises(ValueError, match="mean_minutes"):
        methods.WalkSettings("mean_minutes", SPEED, 10.0, 1.0, 250.0)


def test_a_park_is_reached_at_its_edge_points_any_other_place_at_its_point() -> None:
    """D-222: a destination that keeps the points of its edge is reached at any of them."""
    rows = [
        {"x": 0.0, "y": 0.0, "attributes": {"edge_points_25830": [[10.0, 0.0], [0.0, 10.0]]}},
        {"x": 5.0, "y": 5.0, "attributes": {}},
        {"x": 7.0, "y": 7.0, "attributes": None},
    ]
    x, y = methods.destination_points(rows)
    assert list(zip(x.tolist(), y.tolist(), strict=True)) == [
        (10.0, 0.0),
        (0.0, 10.0),
        (5.0, 5.0),
        (7.0, 7.0),
    ]
    empty_x, empty_y = methods.destination_points([])
    assert len(empty_x) == len(empty_y) == 0


def test_a_node_takes_the_zone_of_its_section_by_prefix_or_by_barrio() -> None:
    """Municipio and district are prefixes of the section code; a barrio is not (section
    2807905013 lies in barrio 28079051), so it comes from the section's parent (D-232)."""
    from hi_features import walk

    section = np.array(["2807905013", "2807920001", "2800101001", ""])
    assert walk.zone_of_node(section, "distrito").tolist() == ["2807905", "2807920", "2800101", ""]
    parents = {"2807905013": "28079051", "2807920001": "28079201"}
    barrios = walk.zone_of_node(section, "barrio", parents)
    assert barrios.tolist() == ["28079051", "28079201", "", ""]  # outside Madrid: no barrio
    with pytest.raises(ValueError, match="barrio"):
        walk.zone_of_node(section, "barrio")


def test_a_barrio_median_is_over_its_streets_not_a_median_of_section_medians() -> None:
    """Barrio X has two sections: one with 3 nodes at 100 m, one with 1 node at 1,000 m. The
    street-weighted median is 100 m (1.3 min at 75 m/min); a median of the two section
    medians would be 550 m."""
    from hi_features import walk

    section = np.array(["S1", "S1", "S1", "S2"])
    zones = walk.zone_of_node(section, "barrio", {"S1": "X", "S2": "X"})
    settings = methods.WalkSettings("median_minutes", SPEED, 10.0, 1.0, 0.0)
    frame = methods.walk_access(
        zones, np.full(4, 100.0), np.array([100.0, 100.0, 100.0, 1000.0]), ["X"], Y, settings
    )
    assert _rows(frame)["X"]["value"] == pytest.approx(100.0 / SPEED)
