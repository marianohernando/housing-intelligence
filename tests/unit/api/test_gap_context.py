"""gap-0.4 (D-254): the housing row is context, never a verdict, and has no impact (no database).

Navas del Rey has 342 large homes per 100 large households against 436 in the other rural
municipios: with gap-0.3 that was a significant FALTA, though second homes inflate the stock.
"""

from typing import Any, cast

import pytest
from hypothesis import given
from hypothesis import strategies as st
from sqlalchemy import Connection

from hi_api.services import gap_impact as impact_service
from hi_api.services import gaps as gaps_service
from hi_api.services.gap_map import RowContext, _zone
from hi_api.services.gap_reference import References, context_verdict
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public import GapStatus
from hi_domain.gaps import JUDGED_ROWS, TerritoryType

RURAL = TerritoryType.RURAL
VILLAGE, OTHERS = "28094", "28001"  # 342 per 100 households, against 4.360 per 1.000
VERDICTS = {GapStatus.FALTA, GapStatus.JUSTO, GapStatus.CUBIERTO}


def _counts(numerator: float, denominator: float) -> dict[str, Any]:
    counts = {"numerator": numerator, "denominator": denominator}
    return {"value": 100 * numerator / denominator, "inputs": {"counts": counts}}


def _context(context_row: bool) -> RowContext:
    own = {VILLAGE: (342.0, 100.0), OTHERS: (4360.0, 1000.0)}
    refs = References(
        types={VILLAGE: RURAL, OTHERS: RURAL},
        sums={"f": {RURAL: [4702.0, 1100.0]}},
        own={"f": own},
    )
    region = _counts(4702.0, 1100.0)
    return RowContext("f", "higher_is_better", region, refs, True, context_row)


def _village() -> dict[str, Any]:
    return _counts(342.0, 100.0) | {
        "territory_code": VILLAGE,
        "admin_unit_id": f"ES.28.MUN.{VILLAGE}",
        "name": "Navas del Rey",
        "confidence": 0.8,
        "null_reason": None,
    }


def test_the_village_would_be_falta_if_the_row_were_judged() -> None:
    judged = _zone(_village(), _context(context_row=False))
    assert judged.status is GapStatus.FALTA
    assert judged.ratio_to_reference == pytest.approx(342 / 436, rel=1e-3)


def test_the_housing_row_shows_value_and_reference_with_no_verdict() -> None:
    zone = _zone(_village(), _context(context_row=True))
    assert zone.status is GapStatus.CONTEXTO
    assert zone.value == pytest.approx(342.0)
    assert zone.reference == pytest.approx(436.0)
    assert zone.ratio_to_reference is None
    assert zone.reliable and zone.comparison_group is None


def test_an_unknown_context_value_is_sin_datos() -> None:
    unknown = _village() | {"value": None, "null_reason": "SOURCE_MISSING"}
    assert _zone(unknown, _context(context_row=True)).status is GapStatus.SIN_DATOS


def test_the_zone_list_names_the_housing_row_as_context(monkeypatch: pytest.MonkeyPatch) -> None:
    """GET /gaps/{level}/{code}: the domain's name even if the registry still has the old one
    (no sync needed), value and reference in the explanation, no ratio and no verdict."""
    monkeypatch.setattr(gaps_service, "dataset_refs", lambda conn, versions: [])
    binding = {
        "row": "vivienda",
        "role": "primary",
        "label": "Vivienda para familias",  # the registry before a sync
        "phrase": "viviendas de más de 90 m² por cada 100 hogares de 4 o más personas",
    }
    feature = {
        "feature_id": "f",
        "human_name": "Viviendas grandes por cada 100 hogares grandes",
        "unit": "viviendas/100 hogares",
        "direction": "higher_is_better",
        "gap_row": binding,
        "formula": {"method": "metric_ratio", "per": 100},
    }
    context = _context(context_row=True)
    zone = gaps_service.ZoneContext(TerritoryLevel.MUNICIPIO, VILLAGE, context.references)
    main = gaps_service.Measured(feature, _village())
    row = gaps_service._gap_row(cast(Connection, None), main, context.region, [], zone)
    assert row.label == "Viviendas grandes por cada 100 hogares grandes (contexto)"
    assert row.status is GapStatus.CONTEXTO
    assert row.ratio_to_reference is None and row.reliable and row.comparison_group is None
    assert row.indicator.value == pytest.approx(342.0)
    assert row.reference == pytest.approx(436.0)
    assert row.explanation.startswith("342,0 viviendas de más de 90 m²")
    assert "436,0" in row.explanation and "Es un dato de contexto" in row.explanation


@given(st.one_of(st.none(), st.floats(min_value=0, max_value=1e6, allow_nan=False)))
def test_a_context_row_never_returns_a_verdict(value: float | None) -> None:
    verdict = context_verdict(value)
    assert verdict.status not in VERDICTS
    assert verdict.reliable and verdict.group is None


def test_the_impact_never_asks_for_the_housing_row(monkeypatch: pytest.MonkeyPatch) -> None:
    asked: list[GapRowKey] = []

    def impact_row(
        conn: Connection, row: GapRowKey, stamp: str, warnings: list[str]
    ) -> tuple[Any, list[Any]] | None:
        asked.append(row)
        return None

    monkeypatch.setattr(impact_service, "data_stamp", lambda conn: "2026-11-23 00:00:00")
    monkeypatch.setattr(impact_service, "_impact_row", impact_row)
    impact, _, _ = impact_service.gap_impact(cast(Connection, None))
    assert asked == JUDGED_ROWS
    assert GapRowKey.VIVIENDA not in asked
    assert impact.method.context_rows == [GapRowKey.VIVIENDA]
