"""D-247: the data of the investor version (premises, VEDA buildable area, CM cadastre by
district and the pilot barrios), on real samples and without a database."""

from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
import pytest
from pydantic import ValidationError

from hi_contracts.catalog.enums import NullReason
from hi_contracts.catalog.manual import AreaPointsTable
from hi_contracts.catalog.pipeline import (
    CmDistrictConceptPipeline,
    MadridBuildableAreasPipeline,
    MadridPremisesCensusPipeline,
    PilotZonesPipeline,
)
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.pipelines.buildable.normalize import PlacedArea, normalize_buildable_areas
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.district_concept.run import normalize_district_concept
from hi_ingestion.pipelines.pilot.run import EDGE, load_pilot, pilot_rows
from hi_ingestion.pipelines.premises.normalize import (
    ANY_GROUP,
    UNREAD_ACTIVITY,
    PremisesObservations,
    normalize_premises,
)
from hi_ingestion.pipelines.premises.run import proximity_labels_check
from hi_ingestion.pipelines.zone_context.parcels import Placement

GOLDEN = Path(__file__).resolve().parents[3] / "data" / "fixtures" / "golden" / "investor_sample"
PALACIO, CASTILLEJOS = "28079011", "28079063"


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog()


@pytest.fixture(scope="module")
def premises_spec(catalog: Catalog) -> MadridPremisesCensusPipeline:
    spec = catalog.pipelines["ayto_censo_locales_actividades"]
    assert isinstance(spec, MadridPremisesCensusPipeline)
    return spec


@pytest.fixture(scope="module")
def premises(premises_spec: MadridPremisesCensusPipeline) -> pd.DataFrame:
    return read_csv(GOLDEN / "ayto_censo_locales_actividades.csv", premises_spec.csv)


def _value(result: PremisesObservations, zone: str, dim: str, value: str) -> float:
    frame = result.obs.frame
    rows = frame.loc[
        [
            code == zone and dims.get(dim) == value
            for code, dims in zip(frame["territory_code"], frame["dims"], strict=True)
        ]
    ]
    assert len(rows) == 1, (zone, dim, value)
    return float(rows["value"].iloc[0])


def _expected(premises: pd.DataFrame, spec: MadridPremisesCensusPipeline) -> dict[str, Any]:
    """The sample counted by hand: one premise per id, street or grouped access, not gone."""
    by_premise = premises.groupby("id_local")
    counted = {
        key: rows
        for key, rows in by_premise
        if rows["id_tipo_acceso_local"].iloc[0] in {"0", "1"}
        and rows["id_situacion_local"].iloc[0] in {"1", "4", "5", "7"}
    }
    proximity = {code for group in spec.proximity.values() for code in group}
    states: Counter[tuple[str, str]] = Counter()
    shops: Counter[str] = Counter()
    for rows in counted.values():
        barrio = (
            f"28079{int(rows['id_distrito_local'].iloc[0]):02d}{rows['cod_barrio_local'].iloc[0]}"
        )
        states[(barrio, rows["id_situacion_local"].iloc[0])] += 1
        if rows["id_situacion_local"].iloc[0] == "1" and set(rows["id_epigrafe"]) & proximity:
            shops[barrio] += 1
    return {"states": states, "shops": shops}


def test_premises_are_counted_once_by_situation_and_proximity(
    premises: pd.DataFrame, premises_spec: MadridPremisesCensusPipeline
) -> None:
    result = normalize_premises(premises, premises_spec)
    expected = _expected(premises, premises_spec)
    for barrio in (PALACIO, CASTILLEJOS):
        assert _value(result, barrio, "situacion", "abierto") == expected["states"][(barrio, "1")]
        assert _value(result, barrio, "situacion", "cerrado") == expected["states"][(barrio, "4")]
        assert _value(result, barrio, "situacion", "obras") == 0  # a 0 of an exhaustive census
        assert _value(result, barrio, "grupo", ANY_GROUP) == expected["shops"][barrio]
    assert _value(result, CASTILLEJOS, "grupo", "farmacia") == 1
    # The premise with a butcher's, a grocer's and a ready-meal epígrafe is one proximity shop
    assert _value(result, CASTILLEJOS, "grupo", "carniceria") == 1
    assert _value(result, CASTILLEJOS, "grupo", "autoservicio") == 1
    assert result.not_counted["access:interior"] > 0
    assert result.not_counted["access:puerta_calle_asociado"] > 0
    assert result.not_counted["state:baja"] > 0


def test_districts_add_up_their_barrios(
    premises: pd.DataFrame, premises_spec: MadridPremisesCensusPipeline
) -> None:
    frame = normalize_premises(premises, premises_spec).obs.frame
    barrios = frame.loc[frame["territory_level"] == "barrio"]
    districts = frame.loc[frame["territory_level"] == "distrito"]
    added = Counter[tuple[str, str]]()
    for code, key, value in zip(
        barrios["territory_code"], barrios["dims_key"], barrios["value"], strict=True
    ):
        added[(code[:7], key)] += value
    assert dict(added) == {
        (c, k): v
        for c, k, v in zip(
            districts["territory_code"], districts["dims_key"], districts["value"], strict=True
        )
    }


def test_a_pending_epigrafe_is_listed_and_its_activity_unknown(
    premises: pd.DataFrame, premises_spec: MadridPremisesCensusPipeline
) -> None:
    result = normalize_premises(premises, premises_spec)
    quarantine = result.obs.quarantine
    pending = quarantine.loc[quarantine["reason"].str.contains("SIN ASIGNAR")]
    assert len(pending) == 1 and not pending["blocking"].iloc[0]
    assert result.blocking == 0
    embajadores = "28079012"
    assert _value(result, embajadores, "situacion", "abierto") == 1  # it counts as open
    assert _value(result, embajadores, "grupo", ANY_GROUP) == 0
    assert _value(result, embajadores, "grupo", UNREAD_ACTIVITY) == 1  # not a 0 in disguise


def test_an_undeclared_situation_or_epigrafe_blocks(
    premises: pd.DataFrame, premises_spec: MadridPremisesCensusPipeline
) -> None:
    changed = premises.copy()
    changed.loc[changed.index[0], "desc_situacion_local"] = "Abierta temporalmente"
    changed.loc[changed.index[1], "id_epigrafe"] = "47A301"
    result = normalize_premises(changed, premises_spec)
    assert result.blocking == 2
    reasons = " ".join(result.obs.quarantine["reason"])
    assert "situation" in reasons and "epígrafe" in reasons


def test_a_premise_whose_rows_disagree_or_without_id_blocks(
    premises: pd.DataFrame, premises_spec: MadridPremisesCensusPipeline
) -> None:
    """A premise is counted once: its rows must agree (review R-03)."""
    ids: list[str] = premises["id_local"].tolist()
    key = next(i for i in ids if ids.count(i) > 1)
    changed = premises.copy()
    last = changed.index[changed["id_local"] == key][-1]
    changed.loc[last, ["id_situacion_local", "desc_situacion_local"]] = ["4", "Cerrado"]
    changed.loc[changed.index[0], "id_local"] = ""
    result = normalize_premises(changed, premises_spec)
    reasons = " ".join(result.obs.quarantine["reason"])
    assert result.blocking == 2
    assert "another access" in reasons and "without premise id" in reasons


def test_a_pending_code_with_another_literal_blocks(
    premises: pd.DataFrame, premises_spec: MadridPremisesCensusPipeline
) -> None:
    changed = premises.copy()
    changed.loc[changed["id_epigrafe"] == "999", "desc_epigrafe"] = "COMERCIO DIVERSO"
    assert normalize_premises(changed, premises_spec).blocking == 1


def test_a_premise_without_barrio_is_listed_never_counted(
    premises: pd.DataFrame, premises_spec: MadridPremisesCensusPipeline
) -> None:
    changed = premises.copy()
    first = changed["id_local"].iloc[0]
    changed.loc[changed["id_local"] == first, "cod_barrio_local"] = ""
    result = normalize_premises(changed, premises_spec)
    assert result.unplaced == 1 and result.blocking == 0
    assert result.counted == normalize_premises(premises, premises_spec).counted - 1


def test_a_changed_proximity_description_blocks(
    premises: pd.DataFrame, premises_spec: MadridPremisesCensusPipeline
) -> None:
    changed = premises.copy()
    changed.loc[changed["id_epigrafe"] == "477301", "desc_epigrafe"] = "FARMACIA Y ORTOPEDIA"
    checks = proximity_labels_check(normalize_premises(changed, premises_spec), premises_spec)
    declared = next(c for c in checks if c.name == "proximity_epigrafes_as_declared")
    assert declared.critical and not declared.passed


# --- VEDA: buildable area left in the planning areas ---------------------------------------

AREA_COLUMNS = [
    "COD_DISTRITO",
    "DISTRITO",
    "COD_AMBITO",
    "AMBITO",
    "SITUACION DEL ÁMBITO",
    "Colectiva. Edif. Residencial",
    "Unifamiliar. Edif. Residencial",
    "Edif. Industrial",
    "Edif. Terciario",
    "Etapa",
    "ESTADO DEL DESARROLLO A FECHA",
]
# Real rows of the July 2026 register (None is an empty cell)
AREAS = [
    [
        "02",
        "Arganzuela",
        "APE.02.12",
        "C/ BOLIVAR Y C/ COBRE",
        "FASE DE EDIFICACION",
        "6670",
        None,
        None,
        None,
        None,
        "2026-07-01 00:00:00",
    ],
    [
        "02",
        "Arganzuela",
        "APE.02.26",
        "ANTIGUO MERCADO DE FRUTAS Y VERDURAS",
        "FASE DE EDIFICACION",
        None,
        None,
        None,
        "29956",
        None,
        "2026-07-01 00:00:00",
    ],
    [
        "02",
        "Arganzuela",
        "APE.02.28",
        "NUEVO SUR - MENDEZ ALVARO",
        "FASE GESTION Y/O URBANIZACION",
        "0",
        "0",
        "0",
        "51776.54",
        None,
        "2026-07-01 00:00:00",
    ],
    [
        "19",
        "Vicálvaro",
        "UZP.2.01",
        "DESARROLLO DEL ESTE - VALDECARROS",
        "FASE DE EDIFICACION",
        "90530",
        "0",
        "0",
        "0",
        "Etapa 1",
        "2026-07-01 00:00:00",
    ],
    [
        "19",
        "Vicálvaro",
        "UZP.2.01",
        "DESARROLLO DEL ESTE - VALDECARROS",
        "FASE GESTION Y/O URBANIZACION",
        "22000",
        "0",
        "0",
        "0",
        "Resto",
        "2026-07-01 00:00:00",
    ],
]


@pytest.fixture(scope="module")
def areas_spec(catalog: Catalog) -> MadridBuildableAreasPipeline:
    spec = catalog.pipelines["ayto_edificabilidad_remanente_ambitos"]
    assert isinstance(spec, MadridBuildableAreasPipeline)
    return spec


PLACED = {
    "APE.02.12": PlacedArea(Placement("2807902", "28079024"), 100),
    "APE.02.26": PlacedArea(Placement("2807902", "28079022"), 88),
    "APE.02.28": PlacedArea(Placement("2807902", "28079022"), 100),
    "UZP.2.01": PlacedArea(Placement("2807919", "28079191"), 70),
}


def test_residential_area_left_by_area_and_never_a_blank_as_zero(
    areas_spec: MadridBuildableAreasPipeline,
) -> None:
    register = normalize_buildable_areas(
        pd.DataFrame(AREAS, columns=AREA_COLUMNS), areas_spec, PLACED
    )
    assert register.obs.quarantine.empty
    assert register.out_of_scope == {"not_residential": 1, "nothing_left": 1}
    assert register.partial_blank == 1  # APE.02.12: colectiva with a figure, unifamiliar blank
    barrios = register.obs.frame.loc[register.obs.frame["territory_level"] == "barrio"]
    items = {d["item"]: (d, v) for d, v in zip(barrios["dims"], barrios["value"], strict=True)}
    assert items["APE.02.12"][1] == 6670  # the blank unifamiliar cell is absent, not 0
    assert items["APE.02.12"][0]["use"] == "colectiva"
    stage_one = items["UZP.2.01|etapa_1"]
    assert stage_one[1] == 90530 and stage_one[0]["stage"] == "edificacion"
    assert stage_one[0]["name"].endswith("(etapa 1)")
    assert "note" in stage_one[0]  # 70 % of it in its barrio: said in the barrio only
    districts = register.obs.frame.loc[register.obs.frame["territory_level"] == "distrito"]
    assert all("note" not in d for d in districts["dims"])


def test_an_area_with_every_use_blank_keeps_an_unknown_value(
    areas_spec: MadridBuildableAreasPipeline,
) -> None:
    row = [*AREAS[0][:5], None, None, None, None, None, AREAS[0][-1]]
    register = normalize_buildable_areas(
        pd.DataFrame([row], columns=AREA_COLUMNS), areas_spec, PLACED
    )
    assert all(pd.isna(v) for v in register.obs.frame["value"])
    assert set(register.obs.frame["null_reason"]) == {NullReason.UNKNOWN.value}


def test_an_area_without_point_or_out_of_its_district_blocks(
    areas_spec: MadridBuildableAreasPipeline,
) -> None:
    frame = pd.DataFrame(AREAS, columns=AREA_COLUMNS)
    missing = {k: v for k, v in PLACED.items() if k != "APE.02.12"}
    elsewhere = PLACED | {"APE.02.12": PlacedArea(Placement("2807903", "28079031"), 100)}
    for placed in (missing, elsewhere):
        register = normalize_buildable_areas(frame, areas_spec, placed)
        assert len(register.obs.quarantine) == 1


def test_an_undeclared_situation_blocks(areas_spec: MadridBuildableAreasPipeline) -> None:
    row = list(AREAS[0])
    row[4] = "FASE DE EDIFICACION PARCIAL"
    register = normalize_buildable_areas(
        pd.DataFrame([row], columns=AREA_COLUMNS), areas_spec, PLACED
    )
    assert "not declared" in register.obs.quarantine["reason"].iloc[0]


def test_area_points_are_one_per_area() -> None:
    point = {"ref": "APE.02.12", "x": 440000, "y": 4472000, "share_pct": 100}
    table = {
        "title": "Ámbitos",
        "publisher": "Ayuntamiento de Madrid",
        "url": "https://sigma.madrid.es/hosted/rest/services/x",
        "layer": "Ambitos_Vigentes_julio26",
        "crs": "EPSG:25830",
        "consulted": "2026-11-19",
        "method": "Punto interior del ámbito",
        "municipio_ine": "28079",
        "points": [point],
    }
    assert AreaPointsTable.model_validate(table).points[0].ref == "APE.02.12"
    with pytest.raises(ValidationError, match="one point per area"):
        AreaPointsTable.model_validate(table | {"points": [point, point]})


# --- CM: buildings by Madrid district and use ------------------------------------------------

CONCEPTS = [
    [
        "2026",
        "Inmuebles para uso comercial del distrito Chamartín del municipio de Madrid",
        "Otros",
        "",
        "",
        "Comercial",
        "4629",
        "Número",
        "",
    ],
    [
        "2026",
        "Inmuebles para uso comercial del distrito Fuencarral-El Pardo del municipio de Madrid",
        "Otros",
        "",
        "",
        "Comercial",
        "4002",
        "Número",
        "",
    ],
    [
        "2026",
        "Inmuebles para uso comercial sin asignar distrito del municipio de Madrid",
        "Otros",
        "",
        "",
        "Comercial",
        "-",
        "Número",
        "",
    ],
    [
        "2023",
        "Inmuebles para uso comercial del distrito Chamartín del municipio de Madrid",
        "Otros",
        "",
        "",
        "Comercial",
        "4600",
        "Número",
        "",
    ],
]
CONCEPT_COLUMNS = [
    "Año",
    "Concepto",
    "Tipo territorio",
    "Código territorio",
    "Territorio",
    "Uso",
    "Valor",
    "Unidad",
    "Estado dato",
]
DISTRICTS = {"chamartin": "2807905", "fuencarral el pardo": "2807908"}


def test_the_district_comes_by_name_from_the_concept(catalog: Catalog) -> None:
    spec = catalog.pipelines["cm_catastro_inmuebles_distrito_uso"]
    assert isinstance(spec, CmDistrictConceptPipeline)
    obs = normalize_district_concept(
        pd.DataFrame(CONCEPTS, columns=CONCEPT_COLUMNS), spec, DISTRICTS
    )
    assert obs.quarantine.empty
    assert obs.out_of_scope == 1 and obs.out_of_window == 1  # «sin asignar» and 2023
    assert dict(zip(obs.frame["territory_code"], obs.frame["value"], strict=True)) == {
        "2807905": 4629.0,
        "2807908": 4002.0,
    }
    assert all(d == {"uso": "comercial"} for d in obs.frame["dims"])
    unknown = normalize_district_concept(
        pd.DataFrame(CONCEPTS[:1], columns=CONCEPT_COLUMNS), spec, {"retiro": "2807903"}
    )
    assert len(unknown.quarantine) == 1
    rows = [list(r) for r in CONCEPTS]
    rows[0][5] = ""  # a row without its use is not a use «unknown»
    rows[2][6] = "12"  # a figure on a row of no district is reported
    changed = normalize_district_concept(
        pd.DataFrame(rows, columns=CONCEPT_COLUMNS), spec, DISTRICTS
    )
    assert len(changed.quarantine) == 1 and changed.unassigned_with_figure == 1


# --- The pilot barrios -------------------------------------------------------------------------


def test_every_pilot_barrio_is_one_observation_with_its_edge_review(catalog: Catalog) -> None:
    spec = catalog.pipelines["osm_m40"]
    assert isinstance(spec, PilotZonesPipeline)
    table = load_pilot(spec)
    frame = pilot_rows(table, spec.metric_id)
    assert len(frame) == len(table.barrios) == frame["territory_code"].nunique()
    assert set(frame["value"]) == {1.0}
    edge = [d for d in frame["dims"] if d["stage"] == EDGE]
    assert edge and all(d.get("note") for d in edge)
