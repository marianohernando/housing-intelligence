"""Build the API contract fixtures (data/fixtures/contracts/) from real local data.

These are FIXTURES, not product output: they let the web type and test its screens against real
zones and real indicator values. Each one is exactly what the API service returns today on the
local database (read-only): the per-zone lists, the row maps, the people search (CORE-003,
`fit-0.1`) and the dataset list (see data/fixtures/contracts/README.md).

Usage: uv run python scripts/build_contract_fixtures.py
"""

import json
import os
from pathlib import Path
from typing import Any

from sqlalchemy import Connection, create_engine

from hi_api.services.datasets import dataset_list
from hi_api.services.gap_map import gap_row_map
from hi_api.services.gaps import missing_row_warnings, zone_gap_list
from hi_api.services.places import places_geojson
from hi_api.services.search import search
from hi_contracts.catalog.enums import GapRowKey, PlaceCategory, TerritoryLevel
from hi_contracts.public import GapRowMap, ScenarioState, SearchResult, ZoneGapList
from hi_contracts.public.places import PlaceCollection

OUT = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "contracts"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://housing:housing@localhost:5440/housing"
)


def gap_list(
    conn: Connection, code: str, level: TerritoryLevel = TerritoryLevel.MUNICIPIO
) -> ZoneGapList:
    """Exactly what GET /api/v1/gaps/{level}/{code} returns today."""
    gaps, warnings, _ = zone_gap_list(conn, level, code)
    pending = missing_row_warnings({r.row for r in gaps.rows}, level)
    assert warnings == pending, warnings  # noqa: S101 - only the rows not computed yet
    return gaps


def row_map(conn: Connection, level: TerritoryLevel, row: GapRowKey) -> GapRowMap:
    """Exactly what GET /api/v1/gaps?level=&row= returns today."""
    gap_map, warnings, _ = gap_row_map(conn, level, row)
    assert not warnings, warnings  # noqa: S101 - every zone classified
    return gap_map


def demo_scenario() -> ScenarioState:
    """The demo case: a couple with two children who work on the Castellana (golden_family).
    The place of work is a preference: travel times are not computed yet (D-215)."""
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
                    "max_minutes": None,  # a preference until CORE-009 (D-215)
                }
            ],
            "nearby": [{"need": "colegio", "max_walk_minutes": 10, "required": True}],
            "priorities": ["colegios", "transporte", "salud"],
        }
    )


def search_result(conn: Connection) -> SearchResult:
    """Exactly what POST /api/v1/search returns today for the demo case."""
    result, warnings, _ = search(conn, demo_scenario())
    assert not warnings, warnings  # noqa: S101 - every zone scored, no trip limit
    return result


def colegios_chamartin(conn: Connection) -> PlaceCollection:
    """places-1 (D-216): the colegios of a district, with ownership and the rows that count them."""
    result = places_geojson(
        conn,
        PlaceCategory.EDUCATION,
        "ES.28.DIS.2807905",
        [
            "COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA",
            "CENTRO PRIVADO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA",
        ],
    )
    return PlaceCollection.model_validate(
        {**result.collection, "total": result.total, "page": result.page, "pages": result.pages}
    )


def write(name: str, payload: Any) -> None:
    path = OUT / f"{name}.fixture.json"
    path.write_text(
        json.dumps(payload.model_dump(mode="json"), indent=2, ensure_ascii=False) + "\n"
    )
    print("wrote", path.relative_to(OUT.parents[2]))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    with create_engine(DATABASE_URL).connect() as conn:
        write("scenario_state.familia_castellana", demo_scenario())
        write("zone_gap_list.madrid", gap_list(conn, "28079"))
        write("zone_gap_list.mostoles", gap_list(conn, "28092"))
        write("zone_gap_list.centro", gap_list(conn, "2807901", TerritoryLevel.DISTRITO))
        # gap-0.3 (D-217): a municipio too small alone, compared with its nearest neighbours
        write("zone_gap_list.el_alamo", gap_list(conn, "28004"))
        write("places.colegios_chamartin", colegios_chamartin(conn))
        write(
            "gap_row_map.colegio_municipio",
            row_map(conn, TerritoryLevel.MUNICIPIO, GapRowKey.COLEGIO),
        )
        write(
            "gap_row_map.centro_salud_distrito",
            row_map(conn, TerritoryLevel.DISTRITO, GapRowKey.CENTRO_SALUD),
        )
        write("search_result.familia_presupuesto", search_result(conn))
        write("dataset_list.all", dataset_list(conn, cm_only=False))


if __name__ == "__main__":
    main()
