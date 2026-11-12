"""Versioned corrections with an official source per record (D-218 §10)."""

import pandas as pd
import pytest
from pydantic import ValidationError

from hi_contracts.catalog.corrections import PlaceCorrection, PlaceCorrections
from hi_contracts.catalog.pipeline import PointsPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.common import read_csv
from hi_ingestion.pipelines.places.coordinates import GEOCODED, GeocodeHit
from hi_ingestion.pipelines.places.corrections import load_corrections
from hi_ingestion.pipelines.places.directory import (
    ADDRESS,
    CORRECTION,
    Entry,
    LoadedDirectory,
    RegisterPlace,
    resolve_places,
)
from hi_ingestion.pipelines.places.normalize import Repair, normalize_places
from tests.unit.pipelines.test_place_coordinates import MADRID, geocoder, locate
from tests.unit.pipelines.test_places import FIXTURES

SOURCE = {
    "publisher": "Ministerio de Sanidad",
    "url": "https://www.sanidad.gob.es/x.xlsx",
    "consulted": "2026-11-12",
    "says": "CALLE ATOCHA, Nº 1",
}


def test_the_versioned_file_names_real_pipelines_and_cites_https_sources() -> None:
    corrections = load_corrections().corrections
    assert corrections, "the file holds the corrections decided on 12 Nov"
    pipelines = load_catalog().pipelines
    for c in corrections:
        assert isinstance(pipelines[c.dataset_id], PointsPipeline)
        assert str(c.source.url).startswith("https://")
        if c.directory is not None:
            assert c.directory.dataset_id in pipelines


def test_a_correction_fixes_something_and_places_the_record_once() -> None:
    base = {"dataset_id": "cm_x", "entity_id": "1", "reason": "una razón larga", "source": SOURCE}
    with pytest.raises(ValidationError):  # nothing to fix
        PlaceCorrection.model_validate(base)
    with pytest.raises(ValidationError):  # an address and a directory entry both place it
        PlaceCorrection.model_validate(
            base
            | {
                "address": {"street": "Atocha", "number": "1"},
                "directory": {"dataset_id": "ms_x_y", "entry_id": "9"},
            }
        )
    with pytest.raises(ValidationError):  # one per record
        PlaceCorrections.model_validate(
            {"corrections": [base | {"address": {"street": "Atocha", "number": "1"}}] * 2}
        )


BOCM = {
    "publisher": "Comunidad de Madrid · BOCM",
    "url": "https://www.bocm.es/boletin/CM_Orden_BOCM/2022/12/27/BOCM-20221227-29.PDF",
    "consulted": "2026-11-12",
    "says": "CH0049. Hospital Universitario “Ramón y Cajal”. Renovación de la autorización",
}


def test_a_corrected_name_is_the_text_of_its_source_tildes_included() -> None:
    base = {"dataset_id": "cm_x", "entity_id": "CH0049", "reason": "una razón larga"}
    fix = PlaceCorrection.model_validate(
        base | {"source": BOCM, "name": "Hospital Universitario Ramón y Cajal"}
    )
    assert fix.name == "Hospital Universitario Ramón y Cajal"
    # Only case and quotation marks may differ from the source ("Centro de Salud" -> "salud").
    PlaceCorrection.model_validate(
        base | {"source": BOCM, "name": "hospital universitario ramón y cajal"}
    )
    for not_said in ("Hospital Universitario Ramon y Cajal", "Hospital Ramón y Cajal"):
        with pytest.raises(ValidationError, match="says"):
            PlaceCorrection.model_validate(base | {"source": BOCM, "name": not_said})


def test_the_ramon_y_cajal_takes_its_name_from_the_source_of_its_correction() -> None:
    fixes = {c.entity_id: c for c in load_corrections().for_dataset("cm_centros_sanitarios")}
    assert fixes["CH0049"].name == "Hospital Universitario Ramón y Cajal"
    assert fixes["CH0049"].directory is not None  # still paired by hand with the CNH entry
    for fix in fixes.values():  # every name comes with its official source
        if fix.name is not None:
            assert str(fix.source.url).startswith("https://")


def test_a_name_correction_wins_over_the_directory_and_keeps_what_it_replaced() -> None:
    spec = load_catalog().pipelines["cm_centros_sanitarios"]
    assert isinstance(spec, PointsPipeline)
    frame = read_csv(FIXTURES / "cm_centros_sanitarios.csv", spec.csv)
    directory = LoadedDirectory(
        dataset_id="ms_catalogo_nacional_hospitales",
        source_id="ministerio_sanidad",
        version_label="v1",
        capacity_unit="camas instaladas",
        kinds=dict(spec.directories[0].kinds),
        name_prefix={},
        entries=[
            Entry(
                "280549", "Hospital Fuensanta", "Calle De Arturo Soria 17", "28027",
                "Hospitales Generales", "Privados", 100.0, "Madrid",
            )
        ],
    )  # fmt: skip
    fix = PlaceCorrection.model_validate(
        {
            "dataset_id": "cm_centros_sanitarios",
            "entity_id": "CH0006",
            "reason": "el catálogo escribe el nombre sin tilde",
            "source": SOURCE | {"says": "CH0006. Hospital «Fuensanta Ñ». Renovación"},
            "name": "Hospital Fuensanta Ñ",
        }
    )
    places = normalize_places(frame, spec, directories=[directory], corrections=[fix])
    row = places.frame.set_index("external_id").loc["CH0006"]
    assert row["canonical_name"] == "Hospital Fuensanta Ñ"
    assert row["attributes"]["directory"]["name"] == "Hospital Fuensanta"  # as published
    assert row["attributes"]["directory"]["capacity"] == 100.0
    assert row["attributes"]["correction"]["kind"] == "name"
    assert row["attributes"]["correction"]["previous_name"] == "Hospital Fuensanta"
    untouched = places.frame.set_index("external_id").loc["CH0008"]
    assert "correction" not in untouched["attributes"]


def test_a_forced_pair_goes_first_and_its_entry_is_never_offered_again() -> None:
    entry = Entry("E1", "Hospital X", "Calle De Ayala 38", "28001", "Generales", None, 886.0)
    far = RegisterPlace("P1", "Hospital general", "28034", "de Colmenar Viejo", None)
    same_street = RegisterPlace("P2", "Hospital general", "28001", "de Ayala", 38)
    kinds = {"Hospital general": "Generales"}
    plain = resolve_places([far, same_street], [entry], kinds)
    assert {m.place_id: m.method for m in plain.matches} == {"P2": ADDRESS}
    fixed = resolve_places([far, same_street], [entry], kinds, forced={"P1": "E1"})
    assert {m.place_id: m.method for m in fixed.matches} == {"P1": CORRECTION}


def test_an_address_correction_is_geocoded_and_the_place_says_it_was_corrected() -> None:
    spec = load_catalog().pipelines["cm_oficinas_farmacia"]
    assert isinstance(spec, PointsPipeline)
    frame = pd.DataFrame(
        [
            {
                "FARMACIA_NRO_SOE": "7",
                "DIRECCION_VIAL_TIPO": "CALLE",
                "DIRECCION_VIAL_NOMBRE": "Atocha",
                "DIRECCION_VIAL_NRO": "S/N",
                "MUNICIPIO_NOMBRE": "Madrid",
                "LOCALIZACION_COORDENADA_X": "",
                "LOCALIZACION_COORDENADA_Y": "",
            }
        ]
    )
    hit = GeocodeHit(-3.70, 40.42, MADRID, "portal", 1, "ATOCHA")
    repair = Repair(locate, geocoder({"CALLE Atocha 1, Madrid": hit}), {"madrid": MADRID})
    assert normalize_places(frame, spec, repair).frame.empty  # «S/N»: quarantined (D-216)
    fix = PlaceCorrection.model_validate(
        {
            "dataset_id": "cm_oficinas_farmacia",
            "entity_id": "7",
            "reason": "el registro no da número de portal",
            "source": SOURCE,
            "address": {"street": "Atocha", "number": "1"},
        }
    )
    places = normalize_places(frame, spec, repair, corrections=[fix])
    row = places.frame.iloc[0]
    assert row["attributes"]["coordinates"]["origin"] == GEOCODED
    assert row["attributes"]["correction"]["kind"] == "address"
    assert row["attributes"]["correction"]["url"] == SOURCE["url"]
