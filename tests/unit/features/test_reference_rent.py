"""D-242: the Ministry's rent reference brought to the CM level (pure functions)."""

from datetime import date
from typing import Any

import pandas as pd
import pytest

from hi_features.methods import NewContractFactors, apply_new_contract_factors
from hi_features.reference_rent import (
    Calibration,
    FillConfidence,
    ReferenceRent,
    calibration,
    fill_rows,
    pick,
    pooled,
    references_by_typology,
    scale_quartiles_by_adjustment,
    values_at,
)

Y2024 = date(2024, 1, 1)
Y2023 = date(2023, 1, 1)
TYPOLOGIES = ["colectiva", "unifamiliar"]


def _obs(rows: list[tuple[str, date, dict[str, str], float | None]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"territory_code": c, "period_start": p, "dims": d, "value": v, "null_reason": None}
            for c, p, d, v in rows
        ]
    )


def _rent(code: str, typology: str, median: float, p25: float, p75: float, period: date = Y2024):
    return [
        (code, period, {"tipologia": typology, "estadistico": "mediana"}, median),
        (code, period, {"tipologia": typology, "estadistico": "p25"}, p25),
        (code, period, {"tipologia": typology, "estadistico": "p75"}, p75),
    ]


def _refs() -> tuple[dict[str, dict[str, ReferenceRent]], Any]:
    rent = _obs(
        [
            *_rent("28002", "colectiva", 9.0, 7.0, 11.0),
            *_rent("28002", "unifamiliar", 6.0, 4.0, 8.0),
            *_rent("28003", "unifamiliar", 5.5, 3.8, 7.1),
            ("28001", Y2024, {"tipologia": "colectiva", "estadistico": "mediana"}, None),
            *_rent("28002", "colectiva", 8.0, 6.0, 10.0, Y2023),  # an older year, left out
        ]
    )
    count = _obs(
        [
            ("28002", Y2024, {"tipologia": "colectiva"}, 509.0),
            ("28002", Y2024, {"tipologia": "unifamiliar"}, 53.0),
            ("28003", Y2024, {"tipologia": "unifamiliar"}, 12.0),
            ("28001", Y2024, {"tipologia": "colectiva"}, 0.0),
        ]
    )
    return references_by_typology(rent, count, "tipologia", "estadistico")


def test_references_keep_the_latest_year_and_only_published_medians() -> None:
    refs, period = _refs()
    assert period == Y2024
    assert set(refs) == {"28002", "28003"}  # La Acebeda publishes no median: no reference
    assert refs["28002"]["colectiva"] == ReferenceRent("colectiva", 9.0, 7.0, 11.0, 509.0)


def test_flats_first_and_houses_only_without_flats() -> None:
    refs, _ = _refs()
    flats = pick(refs["28002"], TYPOLOGIES)
    houses = pick(refs["28003"], TYPOLOGIES)
    assert flats is not None and flats.typology == "colectiva"
    assert houses is not None and houses.typology == "unifamiliar"


def test_calibration_is_the_median_of_the_ratios_and_needs_enough_zones() -> None:
    refs = {
        c: ReferenceRent("colectiva", m, None, None, 100.0)
        for c, m in (("a", 10.0), ("b", 10.0), ("c", 10.0))
    }
    scale = calibration({"a": 10.0, "b": 10.4, "c": 11.0}, refs, min_zones=3)
    assert scale.ratio == pytest.approx(1.04)
    assert (scale.zones, scale.low, scale.high) == (3, 1.0, 1.1)
    with pytest.raises(ValueError, match="2 zones with both figures, 3 needed"):
        calibration({"a": 10.0, "b": 10.4}, refs, min_zones=3)


def test_the_cm_figure_is_read_in_the_reference_year() -> None:
    cm = _obs(
        [
            ("28079", Y2024, {"tipo_vivienda": "viviendas_habituales"}, 15.1),
            ("28079", Y2024, {"tipo_vivienda": "viviendas_no_habituales"}, 26.0),
            ("28079", Y2023, {"tipo_vivienda": "viviendas_habituales"}, 14.3),
        ]
    )
    assert values_at(cm, {"tipo_vivienda": "viviendas_habituales"}, Y2024) == {"28079": 15.1}


SCALE = Calibration(1.04, 37, 0.97, 1.08)
CONFIDENCE = FillConfidence(0.7, 30, 0.4, {"unifamiliar": 0.5})


def test_fill_scales_median_and_quartiles_and_never_invents_a_zone() -> None:
    refs = {"28002": ReferenceRent("colectiva", 9.0, 7.0, 11.0, 509.0)}
    rows = fill_rows(refs, ["28001", "28002"], Y2024, SCALE, CONFIDENCE).to_dict("records")
    acebeda, ajalvir = rows
    assert pd.isna(acebeda["value"]) and acebeda["null_reason"] == "SOURCE_MISSING"  # never 0
    assert ajalvir["value"] == pytest.approx(9.36)
    assert ajalvir["confidence"] == 0.7
    reference = ajalvir["reference"]
    assert reference["quartiles"] == pytest.approx({"p25": 7.28, "p75": 11.44})
    assert reference["calibration"]["ratio"] == 1.04 and reference["contracts"] == 509.0


@pytest.mark.parametrize(
    ("ref", "confidence"),
    [
        (ReferenceRent("colectiva", 9.0, 7.0, 11.0, 30.0), 0.7),
        (ReferenceRent("colectiva", 9.0, 7.0, 11.0, 29.0), 0.4),  # fewer than 30 leases
        (ReferenceRent("unifamiliar", 6.0, 4.0, 8.0, 200.0), 0.5),  # houses
        (ReferenceRent("unifamiliar", 6.0, 4.0, 8.0, 12.0), 0.4),
    ],
)
def test_confidence_drops_with_few_leases_and_with_houses(
    ref: ReferenceRent, confidence: float
) -> None:
    assert CONFIDENCE.of(ref) == confidence


def test_the_new_lease_factor_moves_the_quartiles_with_the_value() -> None:
    refs = {"28002": ReferenceRent("colectiva", 10.0, 8.0, 12.0, 509.0)}
    filled = fill_rows(refs, ["28002"], Y2024, Calibration(1.0, 37, 1.0, 1.0), CONFIDENCE)
    factors = NewContractFactors({"28": 1.2}, Y2024)  # no own table: the region's factor
    row = scale_quartiles_by_adjustment(apply_new_contract_factors(filled, factors, "28")).to_dict(
        "records"
    )[0]
    assert row["value"] == pytest.approx(12.0)
    assert row["adjustment"]["factor_from"] == "28"
    assert row["reference"]["quartiles"] == pytest.approx({"p25": 9.6, "p75": 14.4})


def test_a_barrio_pools_its_sections_weighted_by_leases() -> None:
    """The mean of the sections' figures, weighted by their leases, for the first typology any
    of them publishes; a section outside every barrio is left out."""
    sections = {
        "s1": {"colectiva": ReferenceRent("colectiva", 20.0, 16.0, 24.0, 300.0)},
        "s2": {"colectiva": ReferenceRent("colectiva", 16.0, 12.0, 20.0, 100.0)},
        "s3": {"unifamiliar": ReferenceRent("unifamiliar", 9.0, 7.0, 11.0, 50.0)},
        "s4": {"colectiva": ReferenceRent("colectiva", 99.0, 90.0, 99.0, 999.0)},
        "s5": {"unifamiliar": ReferenceRent("unifamiliar", 8.0, 6.0, 10.0, 40.0)},
    }
    parents = {"s1": "B1", "s2": "B1", "s3": "B1", "s5": "B2"}
    barrios = pooled(sections, parents, TYPOLOGIES)
    assert barrios["B1"] == ReferenceRent("colectiva", 19.0, 15.0, 23.0, 400.0, sections=2)
    assert barrios["B2"].typology == "unifamiliar" and barrios["B2"].sections == 1
