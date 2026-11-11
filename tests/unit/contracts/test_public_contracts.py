"""PUBLIC contracts: fixtures validate, and the rules the web relies on are enforced."""

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import BaseModel, ValidationError

from hi_contracts.public import (
    GapMethod,
    GapRow,
    RealityCheck,
    ScenarioState,
    SearchResult,
    ZoneGapList,
)
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.catalog.provenance import dataset_ref, is_cm_open_data

FIXTURES = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "contracts"
CONTRACTS: dict[str, type[BaseModel]] = {
    "scenario_state": ScenarioState,
    "zone_gap_list": ZoneGapList,
    "search_result": SearchResult,
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


def test_reality_check_counts_add_up() -> None:
    base: dict[str, Any] = {
        "zones_evaluated": 10,
        "zones_passing": 3,
        "zones_unknown": 2,
        "relaxations": [
            {"constraint_id": "budget", "label": "+200 €", "zones_if_relaxed": 5, "added_zones": 2}
        ],
    }
    RealityCheck.model_validate(base)
    with pytest.raises(ValidationError):
        RealityCheck.model_validate(base | {"zones_unknown": 8})
    wrong = base | {"relaxations": [base["relaxations"][0] | {"zones_if_relaxed": 4}]}
    with pytest.raises(ValidationError):
        RealityCheck.model_validate(wrong)


@pytest.mark.parametrize(
    "change",
    [
        {"nearby": [{"need": "colegio"}, {"need": "colegio"}]},
        {"priorities": ["coste", "coste"]},
        {"household": {"adults": 2, "children": 2, "children_ages": [4]}},
        {"household": {"adults": 1, "children": 1, "children_ages": [19]}},
        {"household": {"adults": 1, "seniors": 2}},
        {"zone_level": "h3_r9"},
        {"anchors": [{"label": "Lisboa", "lon": -9.14, "lat": 38.72}]},
        {"budget_monthly_eur": 0},
        {"sexo": "mujer"},
    ],
)
def test_scenario_rejects_incoherent_or_unknown_input(change: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        ScenarioState.model_validate(change)


def test_default_scenario_is_valid_and_rents_by_municipio() -> None:
    scenario = ScenarioState()
    assert scenario.tenure == "rent"
    assert scenario.zone_level == "municipio"
    assert scenario.household.size == 1


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
