"""% of residential street above a noise level (D-237): values, explicit unknowns, confidence."""

import math
from datetime import date

import numpy as np
import pandas as pd
import pytest

from hi_domain.access.graph import WalkNetwork
from hi_features import methods, noise
from hi_ingestion.catalog.loader import load_catalog

Y = date(2021, 1, 1)
NAN = float("nan")


def _rows(frame: pd.DataFrame) -> dict[str, dict[str, object]]:
    return {str(r["territory_code"]): r for r in frame.to_dict("records")}  # pyright: ignore[reportUnknownVariableType]


def _is_null(value: object) -> bool:
    return value is None or (isinstance(value, float) and math.isnan(value))


def _share(min_street_m: float = 250.0, min_covered_share: float = 0.5) -> pd.DataFrame:
    """Zone A: 400 m of street, 100 m above 65 dB, 100 m exactly at 65, 100 m quiet and 100 m
    off the map. Zone B: 300 m, only 100 m on the map. Zone C: no street. Zone D: 100 m, all
    loud. The last node lies in no zone."""
    settings = methods.StreetShareSettings(65.0, min_covered_share, 1.0, min_street_m)
    return methods.street_share_above(
        np.array(["A", "A", "A", "A", "B", "B", "D", ""]),
        np.array([100.0, 100.0, 100.0, 100.0, 100.0, 200.0, 100.0, 100.0]),
        np.array([70.0, 65.0, 40.0, NAN, 80.0, NAN, 66.0, 90.0]),
        ["A", "B", "C", "D"],
        Y,
        settings,
    )


def test_share_is_street_metres_above_the_level_over_those_on_the_map() -> None:
    row = _rows(_share())["A"]
    assert row["value"] == 100.0 * 100 / 300  # exactly 65 dB is not above 65 dB
    assert row["confidence"] == 0.75  # 300 of its 400 m are on the map
    assert row["period_start"] == Y


def test_a_zone_mostly_off_the_map_is_unknown_never_zero() -> None:
    rows = _rows(_share())
    for code in ("B", "C"):
        assert _is_null(rows[code]["value"])
        assert rows[code]["null_reason"] == "SOURCE_NO_COVERAGE"
        assert rows[code]["confidence"] == 0.0
    assert _rows(_share(min_covered_share=0.3))["B"]["value"] == 100.0


def test_little_street_keeps_low_confidence() -> None:
    row = _rows(_share())["D"]
    assert row["value"] == 100.0
    assert row["confidence"] == 0.5
    assert _rows(_share(min_street_m=50.0))["D"]["confidence"] == 1.0


def test_every_zone_gets_a_row_and_no_regional_reference() -> None:
    frame = _share()
    assert list(frame["territory_code"]) == ["A", "B", "C", "D"]
    assert bool(frame["territory_level"].isna().all())


def test_more_noise_never_lowers_the_share() -> None:
    settings = methods.StreetShareSettings(55.0, 0.5, 1.0, 0.0)
    rng = np.random.default_rng(7)
    weight = rng.uniform(1, 50, 200)
    zone = np.array(["A"] * 200)
    level = rng.uniform(30, 80, 200)
    quiet = methods.street_share_above(zone, weight, level, ["A"], Y, settings)
    loud = methods.street_share_above(zone, weight, level + 3.0, ["A"], Y, settings)
    assert loud["value"].iloc[0] >= quiet["value"].iloc[0]


def test_street_noise_is_context_for_madrid_only() -> None:
    """D-237: above 65 dB Ld and 55 dB Ln (RD 1367/2007's day and night objectives for residential
    areas, R-02), read every 10 m along the same streets as the walking features (R-03), only
    inside the municipio of Madrid; never scores."""
    catalog = load_catalog()
    walk = catalog.features["min_a_pie_parque"].formula.model_extra or {}
    for feature_id, layer, above in (
        ("pct_calle_ruido_dia", "ld", 65),
        ("pct_calle_ruido_noche", "ln", 55),
    ):
        spec = catalog.features[feature_id]
        formula = spec.formula.model_extra or {}
        assert spec.fit is None and spec.gap_row is None and not spec.models
        assert (formula["layer"], formula["above"]) == (layer, above)
        assert formula["coverage_prefix"] == "28079" and formula["sample_step_m"] == 10
        assert formula["origin_highways"] == walk["origin_highways"]
        assert set(formula["levels"]) == {"distrito", "barrio"}
        assert spec.null_policy.no_coverage == "unknown"
        pipeline = catalog.pipelines[formula["raster_dataset"]]
        assert pipeline.kind == "noise_raster" and layer in pipeline.layers


def _network() -> WalkNetwork:
    """FIXTURE: a residential street of 25 m (A-B), a footway of 30 m (B-C, not an origin) and a
    residential street of 4 m (C-D) whose end D lies in another section."""
    return WalkNetwork(
        node_id=np.arange(4, dtype=np.int64),
        node_x=np.array([0.0, 25.0, 55.0, 59.0]),
        node_y=np.zeros(4),
        edge_u=np.array([0, 1, 2], dtype=np.int64),
        edge_v=np.array([1, 2, 3], dtype=np.int64),
        edge_length_m=np.array([25.0, 30.0, 4.0]),
        edge_highway=np.array([0, 1, 0], dtype=np.int64),
        highways=("residential", "footway"),
    )


def test_streets_are_read_along_each_segment_not_at_the_crossings() -> None:
    """R-03 of PR #65: every 10 m at most, each piece weighing its share of `edge_length_m`."""
    sections = np.array(["S1", "S1", "S1", "S2"])
    samples = noise.street_samples(_network(), ["residential"], sections, 10.0)
    # 3 pieces of A-B, 1 of C-D
    assert samples.x.tolist() == pytest.approx([25 / 6, 12.5, 125 / 6, 57.0])
    assert samples.weight.tolist() == pytest.approx([25 / 3, 25 / 3, 25 / 3, 4.0])
    assert samples.weight.sum() == pytest.approx(29.0)  # a footway is not a street people live in
    # A piece takes the section of the nearer end; a middle exactly halfway takes the far end
    assert samples.section.tolist() == ["S1", "S1", "S1", "S2"]
    only = noise.street_samples(_network(), ["residential"], sections, 10.0, prefix="S2")
    assert only.weight.tolist() == [4.0]  # with a prefix, only segments with an end under it
