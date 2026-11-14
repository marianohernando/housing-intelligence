"""% of residential street above a noise level (D-237): values, explicit unknowns, confidence."""

import math
from datetime import date

import numpy as np
import pandas as pd

from hi_features import methods
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
    """D-237: above 65 dB Lden and 55 dB Ln (RD 1367/2007's objectives for residential areas), on
    the same streets as the walking features, only inside the municipio of Madrid; never scores."""
    catalog = load_catalog()
    walk = catalog.features["min_a_pie_parque"].formula.model_extra or {}
    for feature_id, layer, above in (
        ("pct_calle_ruido_dia", "lden", 65),
        ("pct_calle_ruido_noche", "ln", 55),
    ):
        spec = catalog.features[feature_id]
        formula = spec.formula.model_extra or {}
        assert spec.fit is None and spec.gap_row is None and not spec.models
        assert (formula["layer"], formula["above"]) == (layer, above)
        assert formula["coverage_prefix"] == "28079"
        assert formula["origin_highways"] == walk["origin_highways"]
        assert set(formula["levels"]) == {"distrito", "barrio"}
        assert spec.null_policy.no_coverage == "unknown"
        pipeline = catalog.pipelines[formula["raster_dataset"]]
        assert pipeline.kind == "noise_raster" and layer in pipeline.layers
