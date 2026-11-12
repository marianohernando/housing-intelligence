"""PUBLIC contracts: fixtures validate, and the rules the web relies on are enforced."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from hi_contracts.public import (
    DatasetList,
    GapImpact,
    GapImpactRow,
    GapMethod,
    GapRow,
    GapRowMap,
    RealityCheck,
    ScenarioState,
    SearchResult,
    ZoneGapList,
)
from hi_contracts.public.places import PlaceCollection
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.catalog.provenance import dataset_ref, is_cm_open_data

FIXTURES = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "contracts"
CONTRACTS: dict[str, type[BaseModel]] = {
    "scenario_state": ScenarioState,
    "zone_gap_list": ZoneGapList,
    "gap_row_map": GapRowMap,
    "gap_impact": GapImpact,
    "search_result": SearchResult,
    "dataset_list": DatasetList,
    "places": PlaceCollection,
}


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.fixture.json")), ids=lambda p: p.name)
def test_every_fixture_validates_against_its_contract(path: Path) -> None:
    contract = CONTRACTS[path.name.split(".")[0]]
    contract.model_validate(json.loads(path.read_text()))


def test_every_contract_has_a_fixture() -> None:
    names = {p.name.split(".")[0] for p in FIXTURES.glob("*.fixture.json")}
    assert names == set(CONTRACTS)


def _gap_row(**overrides: Any) -> dict[str, Any]:
    path = FIXTURES / "zone_gap_list.madrid.fixture.json"
    row: dict[str, Any] = json.loads(path.read_text())["rows"][0]
    return row | overrides


def test_sin_datos_if_and_only_if_the_value_is_unknown() -> None:
    GapRow.model_validate(_gap_row())
    unknown = _gap_row()
    unknown["indicator"] = unknown["indicator"] | {"value": None, "null_reason": "SOURCE_MISSING"}
    with pytest.raises(ValidationError):
        GapRow.model_validate(unknown)  # status still FALTA
    GapRow.model_validate(unknown | {"status": "SIN_DATOS"})
    with pytest.raises(ValidationError):
        GapRow.model_validate(_gap_row(status="SIN_DATOS"))  # a known value is never SIN_DATOS
    no_reason: dict[str, Any] = unknown | {"status": "SIN_DATOS"}
    no_reason["indicator"] = no_reason["indicator"] | {"null_reason": None}
    with pytest.raises(ValidationError):
        GapRow.model_validate(no_reason)


def _relaxation(**overrides: Any) -> dict[str, Any]:
    return {
        "constraint_id": "budget",
        "label": "+200 €/mes",
        "zones_if_relaxed": 5,
        "added_zones": 2,
        "relaxed_scenario": {"budget": {"kind": "rent", "amount_eur": 1400}},
    } | overrides


def test_reality_check_counts_add_up() -> None:
    base: dict[str, Any] = {
        "zones_evaluated": 10,
        "zones_passing": 3,
        "zones_unknown": 2,
        "relaxations": [_relaxation()],
    }
    RealityCheck.model_validate(base)
    with pytest.raises(ValidationError):
        RealityCheck.model_validate(base | {"zones_unknown": 8})
    with pytest.raises(ValidationError):
        RealityCheck.model_validate(base | {"relaxations": [_relaxation(zones_if_relaxed=4)]})


@pytest.mark.parametrize(
    "change",
    [
        {"nearby": [{"need": "colegio"}, {"need": "colegio"}]},
        {"priorities": ["transporte", "transporte"]},
        {"priorities": ["coste"]},  # not one of the six «Me importa» priorities
        {"household": {"adults": 2, "minors": 2, "minor_ages": [4]}},
        {"household": {"adults": 1, "minors": 1, "minor_ages": [19]}},
        {"household": {"adults": 0}},
        {"anchors": [{"label": "Lisboa", "lon": -9.14, "lat": 38.72}]},
        {"budget": {"kind": "rent", "amount_eur": 300_000}},  # a purchase price as rent
        {"budget": {"kind": "buy", "amount_eur": 1200}},  # a rent as purchase price
        {"budget_monthly_eur": 1200},  # v1 field
        {"schema_version": 1},
        {"sexo": "mujer"},
    ],
)
def test_scenario_rejects_incoherent_or_unknown_input(change: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        ScenarioState.model_validate(change)


def test_default_scenario_and_household_size() -> None:
    scenario = ScenarioState()
    assert scenario.schema_version == 2
    assert scenario.budget is None
    household = ScenarioState.model_validate(
        {"household": {"adults": 2, "minors": 2, "seniors_in_care": 1}}
    ).household
    assert household.people == 5
    buy = ScenarioState.model_validate({"budget": {"kind": "buy", "amount_eur": 320_000}})
    assert buy.budget is not None
    assert buy.budget.kind == "buy"


def test_search_fixture_never_shows_a_grade_and_maps_every_zone() -> None:
    result = SearchResult.model_validate(
        json.loads((FIXTURES / "search_result.familia_presupuesto.fixture.json").read_text())
    )
    assert all(0 <= z.match_pct <= 100 and 1 <= len(z.facts) <= 5 for z in result.results)
    assert len(result.all_zones) == result.reality_check.zones_evaluated
    unknown = [z for z in result.all_zones if not z.passes_all and not z.failed_constraints]
    assert len(unknown) == result.reality_check.zones_unknown
    assert all(z.match_pct is None for z in unknown)  # unknown is never painted as a fit


def test_gap_method_cut_offs_are_ordered() -> None:
    with pytest.raises(ValidationError):
        GapMethod(version="x", reference="r", falta_below=1.2, cubierto_from=1.0)


def test_provenance_counts_cm_portal_datasets() -> None:
    catalog = load_catalog()
    assert is_cm_open_data(catalog.datasets["cm_centros_educativos"])
    assert is_cm_open_data(catalog.datasets["crtm_gtfs_metro"])  # D-196: also on the CM portal
    assert not is_cm_open_data(catalog.datasets["osm_red_peatonal"])
    ref = dataset_ref(catalog, "crtm_gtfs_metro", "v1")
    assert ref.url is not None
    assert ref.url.host == "datos.comunidad.madrid"


def test_row_map_counts_match_its_zones_and_sin_datos_needs_no_value() -> None:
    path = FIXTURES / "gap_row_map.colegio_municipio.fixture.json"
    payload: dict[str, Any] = json.loads(path.read_text())
    GapRowMap.model_validate(payload)
    wrong = payload | {"counts": payload["counts"] | {"falta": payload["counts"]["falta"] + 1}}
    with pytest.raises(ValidationError):
        GapRowMap.model_validate(wrong)
    zone = payload["zones"][0]
    with pytest.raises(ValidationError):
        GapRowMap.model_validate(payload | {"zones": [zone | {"status": "SIN_DATOS"}]})
    with pytest.raises(ValidationError):
        GapRowMap.model_validate(payload | {"zones": [zone, zone]})


def test_small_village_is_compared_with_its_neighbours() -> None:
    """gap-0.3 (D-217): a zone too small alone gets its group's status, never «poco fiable»."""
    path = FIXTURES / "zone_gap_list.el_alamo.fixture.json"
    rows = ZoneGapList.model_validate(json.loads(path.read_text())).rows
    grouped = [r for r in rows if r.comparison_group is not None]
    assert grouped
    for row in grouped:
        group = row.comparison_group
        assert group is not None
        assert group.codes[0] == "28004"
        assert len(group.codes) == len(group.names) >= 2
        assert row.reliable
        assert "junto con" in row.explanation


def test_places_fixture_carries_ownership_and_the_rows_that_count_them() -> None:
    path = FIXTURES / "places.colegios_chamartin.fixture.json"
    places = PlaceCollection.model_validate(json.loads(path.read_text()))
    assert places.contract_version == "places-1"
    owned = {f.properties.ownership for f in places.features}
    assert owned <= {"publica", "concertada", "privada"}
    counted = [f for f in places.features if "colegio" in f.properties.gap_rows]
    assert counted
    assert all(f.properties.ownership in {"publica", "concertada"} for f in counted)


def test_impact_fixture_adds_up_and_ranks_by_people() -> None:
    """D-229: the people in FALTA add up the ranked zones, most people first."""
    impact = GapImpact.model_validate(
        json.loads((FIXTURES / "gap_impact.comunidad.fixture.json").read_text())
    )
    assert impact.rows
    for row in impact.rows:
        assert row.people_in_falta <= row.people_total
        assert all(z.p_value is None or z.p_value < 0.025 for z in row.ranking)


def test_impact_row_rejects_an_unsorted_or_inconsistent_ranking() -> None:
    zone = {
        "admin_unit_id": "ES.28.MUN.28092",
        "code": "28092",
        "name": "Móstoles",
        "level": "municipio",
        "ratio_to_reference": 0.5,
        "p_value": 0.001,
        "explanation": "…",
    }
    row = {
        "row": "farmacia",
        "label": "Farmacias",
        "people_label": "personas",
        "madrid_level": "distrito",
        "zones": 199,
        "zones_in_falta": 2,
        "people_in_falta": 30,
        "people_total": 100,
        "share_in_falta": 0.3,
        "summary": "…",
        "ranking": [zone | {"people": 10, "code": "1"}, zone | {"people": 20, "code": "2"}],
    }
    with pytest.raises(ValidationError, match="most to fewest"):
        GapImpactRow.model_validate(row)
    with pytest.raises(ValidationError, match="add up"):
        GapImpactRow.model_validate(row | {"people_in_falta": 31})
    with pytest.raises(ValidationError, match="one ranked zone"):
        GapImpactRow.model_validate(row | {"zones_in_falta": 3})
