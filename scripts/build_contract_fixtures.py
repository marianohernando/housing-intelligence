"""Build the API contract fixtures (data/fixtures/contracts/) from real local data.

These are FIXTURES, not product output: they let the web type and test its screens against real
zones and real indicator values before the engine routes exist. The per-zone lists and the
dataset list are exactly what the API services return today; the search result uses real zones,
rents, regional references and dataset versions from the local database (read-only), with an
illustrative % of fit until CORE-003 (see data/fixtures/contracts/README.md).

Usage: uv run python scripts/build_contract_fixtures.py
"""

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, create_engine, text

from hi_api.services.datasets import dataset_list
from hi_api.services.gaps import zone_gap_list, zone_ref
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.public import (
    Budget,
    BudgetKind,
    ConstraintCheck,
    ConstraintStatus,
    DatasetRef,
    Fact,
    FactKind,
    FactTopic,
    GapHighlight,
    IndicatorValue,
    RankedZone,
    RealityCheck,
    Relaxation,
    ScenarioState,
    SearchResult,
    ZoneGapList,
    ZoneMatch,
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


def gap_list(
    conn: Connection, code: str, level: TerritoryLevel = TerritoryLevel.MUNICIPIO
) -> ZoneGapList:
    """Exactly what GET /api/v1/gaps/{level}/{code} returns today."""
    gaps, warnings, _ = zone_gap_list(conn, level, code)
    assert not warnings, warnings  # noqa: S101 - a fixture must not hide a warning
    return gaps


def demo_scenario() -> ScenarioState:
    """The demo case: a couple with two children who work on the Castellana (golden_family)."""
    return ScenarioState.model_validate(
        {
            "budget": {"kind": "rent", "amount_eur": 1500},
            "household": {"adults": 2, "minors": 2, "minor_ages": [4, 8]},
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
            "priorities": ["colegios", "transporte", "salud"],
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
        explanation=f"Alquiler medio ≈ {es(estimate, 0)} €/mes por {SEARCH_AREA} m² "
        f"({es(float(rent_row.value))} €/m²)",
    )


def _match_pct(budget: ConstraintCheck, school_ratio: float) -> int:
    """Illustrative only (fixture): 60 % budget margin + 40 % schools against the region."""
    margin = max(0.0, 1 - (budget.value or SEARCH_BUDGET) / SEARCH_BUDGET)
    return round(100 * (0.6 * min(margin / 0.3, 1) + 0.4 * min(school_ratio / 1.5, 1)))


def _highlights(conn: Connection, code: str) -> list[GapHighlight]:
    gaps, _, _ = zone_gap_list(conn, TerritoryLevel.MUNICIPIO, code)
    return [GapHighlight(row=r.row, label=r.label, status=r.status) for r in gaps.rows[:3]]


def _ranked(
    conn: Connection, catalog: Catalog, code: str, rank: int, rows: dict[str, dict[str, Any]]
) -> RankedZone:
    budget = _budget_check(rows[RENT].get(code))
    school = rows[SCHOOLS][code]
    reference = regional_reference(conn, SCHOOLS)
    school_ratio = float(school.value) / reference
    school_text = (
        f"{es(float(school.value))} colegios públicos por cada 1.000 menores "
        f"(la región tiene {es(reference)})"
    )
    facts = [
        Fact(
            kind=FactKind.STRENGTH if budget.status is ConstraintStatus.PASS else FactKind.WEAKNESS,
            topic=FactTopic.COSTE,
            text=budget.explanation,
            confidence=budget.confidence,
            indicator=indicator(catalog, RENT, rows[RENT][code]),
        ),
        Fact(
            kind=FactKind.STRENGTH if school_ratio >= 1 else FactKind.WEAKNESS,
            topic=FactTopic.COLEGIOS,
            text=school_text,
            confidence=float(school.confidence),
            indicator=indicator(catalog, SCHOOLS, school),
        ),
        Fact(
            kind=FactKind.UNKNOWN,
            topic=FactTopic.COLEGIOS,
            text="Distancia a pie al colegio: aún sin calcular",
            confidence=0.0,
        ),
    ]
    return RankedZone(
        rank=rank,
        zone=municipio(conn, code),
        match_pct=_match_pct(budget, school_ratio),
        confidence=min(budget.confidence, float(school.confidence)),
        facts=facts,
        constraints=[budget],
        failed_constraints=["budget"] if budget.status is ConstraintStatus.FAIL else [],
        estimated_cost_eur=budget.value,
        gap_highlights=_highlights(conn, code),
    )


def _zone_match(conn: Connection, code: str, check: ConstraintCheck, school: Any) -> ZoneMatch:
    known = check.status is not ConstraintStatus.UNKNOWN
    ratio = float(school.value) / regional_reference(conn, SCHOOLS)
    return ZoneMatch(
        zone=municipio(conn, code),
        match_pct=_match_pct(check, ratio) if known else None,
        passes_all=check.status is ConstraintStatus.PASS,
        failed_constraints=["budget"] if check.status is ConstraintStatus.FAIL else [],
    )


def search_result(conn: Connection, catalog: Catalog) -> SearchResult:
    demo = demo_scenario()
    scenario = demo.model_copy(
        update={
            "budget": Budget(kind=BudgetKind.RENT, amount_eur=SEARCH_BUDGET),
            "min_floor_area_m2": SEARCH_AREA,
            "anchors": [demo.anchors[0].model_copy(update={"max_minutes": None})],
            "nearby": [demo.nearby[0].model_copy(update={"required": False})],
        }
    )
    rows = {f: feature_rows(conn, f) for f in (RENT, SCHOOLS)}
    codes = sorted(rows[SCHOOLS])
    checks = {code: _budget_check(rows[RENT].get(code)) for code in codes}
    passing = [c for c in codes if checks[c].status is ConstraintStatus.PASS]
    failing = [c for c in codes if checks[c].status is ConstraintStatus.FAIL]
    unknown = [c for c in codes if checks[c].status is ConstraintStatus.UNKNOWN]
    ranked = sorted(
        (_ranked(conn, catalog, c, 1, rows) for c in passing), key=lambda z: -z.match_pct
    )[:5]
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
    more = scenario.model_copy(
        update={"budget": Budget(kind=BudgetKind.RENT, amount_eur=SEARCH_BUDGET + 200)}
    )
    return SearchResult(
        scenario=scenario,
        results=results,
        near_misses=near_misses,
        all_zones=[_zone_match(conn, c, checks[c], rows[SCHOOLS][c]) for c in codes],
        reality_check=RealityCheck(
            zones_evaluated=len(codes),
            zones_passing=len(passing),
            zones_unknown=len(unknown),
            binding_constraint="budget",
            relaxations=sorted(
                [
                    Relaxation(
                        constraint_id="budget",
                        label="+200 €/mes",
                        zones_if_relaxed=len(passing) + len(plus),
                        added_zones=len(plus),
                        relaxed_scenario=more,
                    ),
                    Relaxation(
                        constraint_id="budget",
                        label="Sin límite de presupuesto",
                        zones_if_relaxed=len(passing) + len(failing),
                        added_zones=len(failing),
                        relaxed_scenario=scenario.model_copy(update={"budget": None}),
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
        write("zone_gap_list.centro", gap_list(conn, "2807901", TerritoryLevel.DISTRITO))
        write("search_result.familia_presupuesto", search_result(conn, catalog))
        write("dataset_list.all", dataset_list(conn, cm_only=False))


if __name__ == "__main__":
    main()
