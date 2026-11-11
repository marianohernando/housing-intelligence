"""Build the API contract fixtures (data/fixtures/contracts/) from real local data.

These are FIXTURES, not product output: they let the web type and test its screens against real
zones and real indicator values before the engine routes exist. Zones, indicator values,
regional references and dataset versions are read from the local database (read-only). The
classification cut-offs are the provisional ones of GAP-001 and the search score is
illustrative (see data/fixtures/contracts/README.md).

Usage: uv run python scripts/build_contract_fixtures.py
"""

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, create_engine, text

from hi_api.services.gaps import zone_gap_list, zone_ref
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.public import (
    ConstraintCheck,
    ConstraintStatus,
    DatasetRef,
    IndicatorValue,
    RankedZone,
    RealityCheck,
    Reason,
    ReasonKind,
    Relaxation,
    ScenarioState,
    SearchResult,
    ZoneGapList,
    ZoneRef,
)
from hi_domain.gaps import es_number
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.catalog.provenance import dataset_ref

OUT = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "contracts"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing"
)
REGION = "28"
SCHOOLS = "colegios_publicos_por_1000_menores"
RENT = "alquiler_m2_mensual"
SEARCH_BUDGET, SEARCH_AREA = 1200, 90


def es(value: float, decimals: int = 1) -> str:
    return es_number(value, decimals)


def municipio(conn: Connection, code: str) -> ZoneRef:
    return zone_ref(conn, TerritoryLevel.MUNICIPIO, code)


def feature_rows(conn: Connection, feature_id: str) -> dict[str, Any]:
    rows = conn.execute(
        text(
            "SELECT territory_code, value, confidence, null_reason, inputs FROM feature_value "
            "WHERE feature_id = :f AND territory_level = 'municipio'"
        ),
        {"f": feature_id},
    ).all()
    return {r.territory_code: r for r in rows}


def regional_reference(conn: Connection, feature_id: str) -> float:
    """The feature store's regional row: region total over region population (GAP-001)."""
    return float(
        conn.execute(
            text(
                "SELECT value FROM feature_value WHERE feature_id = :f "
                "AND territory_level = 'ccaa' AND territory_code = :region"
            ),
            {"f": feature_id, "region": REGION},
        ).scalar_one()
    )


def indicator(catalog: Catalog, feature_id: str, row: Any) -> IndicatorValue:
    spec = catalog.features[feature_id]
    return IndicatorValue(
        feature_id=feature_id,
        label=spec.human_name,
        value=None if row.value is None else round(float(row.value), 3),
        unit=spec.unit,
        confidence=float(row.confidence),
        null_reason=row.null_reason,
        level=TerritoryLevel.MUNICIPIO,
        datasets=sorted(row.inputs["dataset_versions"]),
    )


def refs(catalog: Catalog, versions: dict[str, str]) -> list[DatasetRef]:
    return [dataset_ref(catalog, d, v) for d, v in sorted(versions.items())]


def gap_list(conn: Connection, code: str) -> ZoneGapList:
    """Exactly what GET /api/v1/gaps/municipio/{code} returns today."""
    gaps, warnings, _ = zone_gap_list(conn, TerritoryLevel.MUNICIPIO, code)
    assert not warnings, warnings  # noqa: S101 - a fixture must not hide a warning
    return gaps


def demo_scenario() -> ScenarioState:
    """The demo case: a couple with two children who work on the Castellana (golden_family)."""
    return ScenarioState.model_validate(
        {
            "budget_monthly_eur": 1500,
            "household": {"adults": 2, "children": 2, "children_ages": [4, 8]},
            "anchors": [
                {
                    "kind": "work",
                    "label": "Paseo de la Castellana (Azca)",
                    "lon": -3.6930,
                    "lat": 40.4500,
                    "days_per_week": 4,
                    "max_minutes": 40,
                }
            ],
            "nearby": [{"need": "colegio", "max_walk_minutes": 10, "required": True}],
            "priorities": ["colegio", "coste", "trayecto"],
        }
    )


def _budget_check(rent_row: Any) -> ConstraintCheck:
    label = f"Alquiler hasta {es(SEARCH_BUDGET, 0)} €/mes para {SEARCH_AREA} m²"
    if rent_row is None or rent_row.value is None:
        return ConstraintCheck(
            constraint_id="budget",
            label=label,
            status=ConstraintStatus.UNKNOWN,
            threshold=SEARCH_BUDGET,
            unit="€/mes",
            confidence=0.0,
            explanation="No hay alquiler medio publicado para este municipio",
        )
    estimate = float(rent_row.value) * SEARCH_AREA
    return ConstraintCheck(
        constraint_id="budget",
        label=label,
        status=ConstraintStatus.PASS if estimate <= SEARCH_BUDGET else ConstraintStatus.FAIL,
        value=round(estimate),
        threshold=SEARCH_BUDGET,
        unit="€/mes",
        confidence=float(rent_row.confidence),
        explanation=f"Un piso de {SEARCH_AREA} m² cuesta unos {es(estimate, 0)} €/mes aquí "
        f"({es(float(rent_row.value))} €/m²)",
    )


def _ranked(
    conn: Connection, catalog: Catalog, code: str, rank: int, rows: dict[str, dict[str, Any]]
) -> RankedZone:
    budget = _budget_check(rows[RENT].get(code))
    school = rows[SCHOOLS][code]
    reference = regional_reference(conn, SCHOOLS)
    school_ratio = float(school.value) / reference
    margin = max(0.0, 1 - (budget.value or SEARCH_BUDGET) / SEARCH_BUDGET)
    score = round(100 * (0.6 * min(margin / 0.3, 1) + 0.4 * min(school_ratio / 1.5, 1)), 1)
    school_text = (
        f"{es(float(school.value))} colegios públicos por cada 1.000 menores; "
        f"la región tiene {es(reference)}"
    )
    return RankedZone(
        rank=rank,
        zone=municipio(conn, code),
        score=score,
        confidence=min(budget.confidence, float(school.confidence)),
        constraints=[budget],
        reasons=[
            Reason(
                kind=ReasonKind.STRENGTH
                if budget.status is ConstraintStatus.PASS
                else ReasonKind.WEAKNESS,
                text=budget.explanation,
                indicator=indicator(catalog, RENT, rows[RENT][code]),
            ),
            Reason(
                kind=ReasonKind.STRENGTH if school_ratio >= 1 else ReasonKind.WEAKNESS,
                text=school_text,
                indicator=indicator(catalog, SCHOOLS, school),
            ),
            Reason(kind=ReasonKind.UNKNOWN, text="Distancia a pie al colegio: aún sin calcular"),
        ],
        estimated_rent_eur=budget.value,
        failed_constraints=["budget"] if budget.status is ConstraintStatus.FAIL else [],
    )


def search_result(conn: Connection, catalog: Catalog) -> SearchResult:
    scenario = demo_scenario().model_copy(
        update={
            "budget_monthly_eur": SEARCH_BUDGET,
            "min_floor_area_m2": SEARCH_AREA,
            "anchors": [demo_scenario().anchors[0].model_copy(update={"max_minutes": None})],
            "nearby": [demo_scenario().nearby[0].model_copy(update={"required": False})],
        }
    )
    rows = {f: feature_rows(conn, f) for f in (RENT, SCHOOLS)}
    codes = sorted(rows[SCHOOLS])
    checks = {code: _budget_check(rows[RENT].get(code)) for code in codes}
    passing = [c for c in codes if checks[c].status is ConstraintStatus.PASS]
    failing = [c for c in codes if checks[c].status is ConstraintStatus.FAIL]
    unknown = [c for c in codes if checks[c].status is ConstraintStatus.UNKNOWN]
    ranked = sorted((_ranked(conn, catalog, c, 1, rows) for c in passing), key=lambda z: -z.score)[
        :5
    ]
    results = [z.model_copy(update={"rank": i}) for i, z in enumerate(ranked, start=1)]
    near = sorted(failing, key=lambda c: checks[c].value or 0)[:3]
    near_misses = [_ranked(conn, catalog, c, i, rows) for i, c in enumerate(near, start=1)]
    plus = [c for c in failing if (checks[c].value or 0) <= SEARCH_BUDGET + 200]
    versions = {
        k: v
        for f in rows.values()
        for r in f.values()
        for k, v in r.inputs["dataset_versions"].items()
    }
    return SearchResult(
        scenario=scenario,
        zone_level=TerritoryLevel.MUNICIPIO,
        results=results,
        near_misses=near_misses,
        reality_check=RealityCheck(
            zones_evaluated=len(codes),
            zones_passing=len(passing),
            zones_unknown=len(unknown),
            binding_constraint="budget",
            relaxations=sorted(
                [
                    Relaxation(
                        constraint_id="budget",
                        label=f"Hasta {es(SEARCH_BUDGET + 200, 0)} €/mes (+200 €)",
                        relaxed_to=SEARCH_BUDGET + 200,
                        unit="€/mes",
                        zones_if_relaxed=len(passing) + len(plus),
                        added_zones=len(plus),
                    ),
                    Relaxation(
                        constraint_id="budget",
                        label="Sin límite de presupuesto",
                        relaxed_to=None,
                        zones_if_relaxed=len(passing) + len(failing),
                        added_zones=len(failing),
                    ),
                ],
                key=lambda r: -r.added_zones,
            ),
        ),
        datasets=refs(catalog, versions),
        methodology_version="search-fixture-illustrative",
    )


def write(name: str, payload: Any) -> None:
    path = OUT / f"{name}.fixture.json"
    path.write_text(
        json.dumps(payload.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n"
    )
    print("wrote", path.relative_to(OUT.parents[2]))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    catalog = load_catalog()
    with create_engine(DATABASE_URL).connect() as conn:
        write("scenario_state.familia_castellana", demo_scenario())
        write("zone_gap_list.madrid", gap_list(conn, "28079"))
        write("zone_gap_list.mostoles", gap_list(conn, "28092"))
        write("search_result.familia_presupuesto", search_result(conn, catalog))


if __name__ == "__main__":
    main()
