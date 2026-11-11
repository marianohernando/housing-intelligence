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
