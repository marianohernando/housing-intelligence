"""Versioned corrections with an official source per record (D-218 §10)."""

import pandas as pd
import pytest
from pydantic import ValidationError

from hi_contracts.catalog.corrections import PlaceCorrection, PlaceCorrections
from hi_contracts.catalog.pipeline import PointsPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.places.coordinates import GEOCODED, GeocodeHit
from hi_ingestion.pipelines.places.corrections import load_corrections
from hi_ingestion.pipelines.places.directory import (
    ADDRESS,
    CORRECTION,
    Entry,
    RegisterPlace,
    resolve_places,
)
from hi_ingestion.pipelines.places.normalize import Repair, normalize_places
from tests.unit.pipelines.test_place_coordinates import MADRID, geocoder, locate

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


def test_a_correction_fixes_exactly_one_thing() -> None:
    base = {"dataset_id": "cm_x", "entity_id": "1", "reason": "una razón larga", "source": SOURCE}
    with pytest.raises(ValidationError):
        PlaceCorrection.model_validate(base)
    with pytest.raises(ValidationError):
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
