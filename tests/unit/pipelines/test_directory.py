"""Official directories (D-218): parsing, entity resolution against a register and naming."""

import math

import pandas as pd
import pytest

from hi_contracts.catalog.pipeline import FacilityDirectoryPipeline
from hi_domain.facilities import dependency
from hi_ingestion.pipelines.directory.normalize import normalize_directory
from hi_ingestion.pipelines.directory.quality import run_directory_quality
from hi_ingestion.pipelines.places.directory import (
    ADDRESS,
    POSTCODE,
    STREET,
    Entry,
    LoadedDirectory,
    RegisterPlace,
    attach_directories,
    institutional_name,
    resolve_places,
    title_case,
)

KINDS = {"Hospital general": "Hospitales Generales", "Hospital especializado": "Especializados"}


def entry(
    external_id: str,
    address: str,
    postal_code: str = "28001",
    kind: str = "Hospitales Generales",
    name: str = "Hospital X",
) -> Entry:
    return Entry(external_id, name, address, postal_code, kind, "Privados", 100.0)


def place(
    external_id: str,
    street: str | None,
    number: int | None,
    postal_code: str | None = "28001",
    subcategory: str = "Hospital general",
) -> RegisterPlace:
    return RegisterPlace(external_id, subcategory, postal_code, street, number)


def matched(resolution_places: list[RegisterPlace], entries: list[Entry]) -> dict[str, str]:
    resolution = resolve_places(resolution_places, entries, KINDS)
    return {m.place_id: f"{m.entry.external_id}:{m.method}" for m in resolution.matches}


def test_same_street_and_number_is_an_address_match() -> None:
    entries = [entry("E1", "Calle De Arturo Soria 17"), entry("E2", "Calle De Arturo Soria 103")]
    assert matched([place("P1", "de Arturo Soria", 17)], entries) == {"P1": f"E1:{ADDRESS}"}


def test_the_number_can_be_any_in_a_range() -> None:
    entries = [entry("E1", "AVENIDA DE ABRANTES, Nº 55 - 57")]
    assert matched([place("P1", "Abrantes", 57)], entries) == {"P1": f"E1:{ADDRESS}"}


def test_street_without_number_needs_a_single_entry_on_it() -> None:
    one = [entry("E1", "Carretera De Meco S/N")]
    assert matched([place("P1", "de Meco", None)], one) == {"P1": f"E1:{STREET}"}
    two = [entry("E1", "Carretera De Meco S/N"), entry("E2", "Carretera De Meco 2")]
    assert matched([place("P1", "de Meco", None)], two) == {}


def test_postcode_only_needs_the_same_kind_and_a_single_entry() -> None:
    entries = [entry("E1", "Avenida De Córdoba S/N", "28041")]
    assert matched([place("P1", "de Málaga", 11, "28041")], entries) == {"P1": f"E1:{POSTCODE}"}
    other_kind = [entry("E1", "Avenida De Córdoba S/N", "28041", kind="Especializados")]
    assert matched([place("P1", "de Málaga", 11, "28041")], other_kind) == {}


def test_other_postcode_never_matches() -> None:
    entries = [entry("E1", "Calle De Arturo Soria 17", "28027")]
    assert matched([place("P1", "de Arturo Soria", 17, "28043")], entries) == {}


def test_an_entry_claimed_twice_goes_to_neither() -> None:
    entries = [entry("E1", "Calle De Juan Bravo 49")]
    places = [place("P1", "de Juan Bravo", 49), place("P2", "Juan Bravo", 49)]
    resolution = resolve_places(places, entries, KINDS)
    assert resolution.matches == []
    assert set(resolution.unmatched) == {"P1", "P2"}
    assert all(r.startswith("ambiguous") for r in resolution.unmatched.values())


def test_an_entry_taken_by_a_stronger_rule_is_not_offered_again() -> None:
    entries = [entry("E1", "Calle De La Maso 38", "28034")]
    places = [place("P1", "de la Masó", 38, "28034"), place("P2", "de Colmenar Viejo", 9, "28034")]
    resolution = resolve_places(places, entries, KINDS)
    assert {m.place_id for m in resolution.matches} == {"P1"}
    assert "P2" in resolution.unmatched


def test_subcategories_without_a_kind_are_not_matched() -> None:
    entries = [entry("E1", "Calle De Arturo Soria 17")]
    centre = place("P1", "de Arturo Soria", 17, subcategory="Centro de salud mental")
    assert matched([centre], entries) == {}


def test_matching_is_one_to_one() -> None:
    entries = [entry(f"E{i}", f"Calle Mayor {i}", "28013") for i in range(1, 6)]
    places = [place(f"P{i}", "Mayor", i, "28013") for i in range(1, 6)]
    places += [place("P9", "Mayor", None, "28013")]
    resolution = resolve_places(places, entries, KINDS)
    used = [m.entry.external_id for m in resolution.matches]
    assert len(used) == len(set(used)) == 5
    assert "P9" in resolution.unmatched


@pytest.mark.parametrize(
    ("published", "prefix", "expected"),
    [
        ("Hospital Universitario La Paz", None, "Hospital Universitario La Paz"),
        ("Clínica La Luz, S.L.", None, "Clínica La Luz"),
        ("Clínica Isadora S.A.", None, "Clínica Isadora"),
        ("Hospital Viamed Santa Elena, S.L", None, "Hospital Viamed Santa Elena"),
        ("Servicio Madrileño de Salud", None, None),
        ("HM Hospitales 1989, S.A.", None, None),
        ("ID Dalud Móstoles Sa", None, None),
        ("Alm Univass S.L.", None, None),
        ("ABRANTES", "Centro de salud", "Centro de salud Abrantes"),
        (
            "LOS SANTOS DE LA HUMOSA",
            "Consultorio local",
            "Consultorio local Los Santos de la Humosa",
        ),
    ],
)
def test_institutional_name(published: str, prefix: str | None, expected: str | None) -> None:
    assert institutional_name(published, prefix) == expected


def test_title_case_keeps_roman_numerals_and_restarts_after_separators() -> None:
    assert title_case("LAS ROZAS / EL ABAJÓN") == "Las Rozas / El Abajón"
    assert title_case("TRES CANTOS II - SECTOR OFICIOS") == "Tres Cantos II - Sector Oficios"
    assert title_case("DR. CASTROVIEJO") == "Dr. Castroviejo"
    assert title_case("POZUELO-ESTACIÓN") == "Pozuelo-Estación"


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Servicios o Institutos de Salud de las CC.AA", "publica"),
        ("Servicios e Institutos de Salud de Las Comunidades Autónomas", "publica"),
        ("Ministerio de Defensa", "publica"),
        ("Privado No Benéfico", "privada"),
        ("Privado Benéfico (Iglesia)", "privada"),
        ("Privados", "privada"),
        ("Mutua de Accidentes de Trabajo", "privada"),
        ("Mútuas Colaboradoras con La Seguridad Social", "privada"),
        ("Otra dependencia funcional", None),
        ("", None),
    ],
)
def test_dependency(text: str, expected: str | None) -> None:
    assert dependency(text) == expected


def test_attach_names_sizes_and_links_the_matched_rows() -> None:
    directory = LoadedDirectory(
        dataset_id="ms_catalogo_nacional_hospitales",
        source_id="ministerio_sanidad",
        version_label="v1",
        capacity_unit="camas instaladas",
        kinds=KINDS,
        name_prefix={},
        entries=[
            entry("E1", "Calle De Arturo Soria 17", name="Hospital Fuensanta"),
            entry("E2", "Calle De Juan Bravo 49", name="HM Hospitales 1989, S.A."),
        ],
    )
    rows: list[dict[str, object]] = [
        {"external_id": pid, "canonical_place_id": f"uuid-{pid}", "canonical_name": "Hospital "
         "general (Madrid)", "attributes": {}}
        for pid in ("P1", "P2", "P3")
    ]  # fmt: skip
    register = {
        "P1": place("P1", "de Arturo Soria", 17),
        "P2": place("P2", "de Juan Bravo", 49),
        "P3": place("P3", "de Serrano", 1),
    }
    attached = attach_directories(rows, register, [directory])
    assert rows[0]["canonical_name"] == "Hospital Fuensanta"
    assert rows[1]["canonical_name"] == "Hospital general (Madrid)"  # a company, not a name
    assert rows[2]["attributes"] == {}
    attribute = rows[1]["attributes"]
    assert isinstance(attribute, dict)
    assert attribute["directory"]["capacity"] == 100.0
    assert attribute["directory"]["match_method"] == ADDRESS
    assert list(attached.links["external_id"]) == ["E1", "E2"]
    report = attached.report["ms_catalogo_nacional_hospitales"]
    assert report["matched"] == 2
    assert report["names_rejected"] == [
        {"external_id": "P2", "published": "HM Hospitales 1989, S.A."}
    ]
    assert [u["external_id"] for u in report["unmatched_places"]] == ["P3"]  # type: ignore[union-attr]


SPEC = FacilityDirectoryPipeline(
    kind="facility_directory",
    dataset_id="ms_catalogo_nacional_hospitales",
    sheet="DIRECTORIO",
    id_column="CODCNH",
    name_column="Nombre Centro",
    address_column="Dirección",
    postal_code_column="Código Postal",
    kind_column="Clase",
    capacity_column="CAMAS",
    capacity_unit="camas instaladas",
    scope_column="Cód. Provincia",
    scope_values=["28"],
    min_rows=2,
    max_rows=10,
)


def _sheet(rows: list[tuple[str, str, str, str, str, str]]) -> pd.DataFrame:
    columns = ["CODCNH", "Nombre Centro", "Dirección", "Código Postal", "Clase", "CAMAS"]
    frame = pd.DataFrame(rows, columns=columns)
    frame["Cód. Provincia"] = ["28" if c.startswith("28") else "31" for c in frame["CODCNH"]]
    return frame


def test_directory_keeps_the_region_and_quarantines_unusable_rows() -> None:
    frame = _sheet(
        [
            ("280029", "Hospital A", "Calle De Ayala 38", "28001", "Generales", "886"),
            ("280035", "Hospital B", "Avenida De Córdoba S/N", "28041", "Generales", ""),
            ("280036", "Hospital C", "Calle X 1", "28O41", "Generales", "10"),
            ("280037", "Hospital D", "Calle Y 1", "28042", "Generales", "-3"),
            ("310121", "Hospital García Orcoyen", "Calle Santa Soria 22", "31200", "G", "108"),
        ]
    )
    directory = normalize_directory(frame, SPEC)
    assert list(directory.frame["external_id"]) == ["280029", "280035"]
    assert directory.out_of_scope == 1
    assert math.isnan(directory.frame["capacity"].iloc[1])  # not published, not zero
    assert set(directory.quarantine["external_id"]) == {"280036", "280037"}
    report = run_directory_quality(directory, SPEC).to_dict()
    failed = {c["name"] for c in report["checks"] if not c["passed"]}
    assert failed == {"quarantine_ratio", "capacity_published"}


def test_directory_quality_fails_when_the_region_is_cut() -> None:
    frame = _sheet([("280029", "Hospital A", "Calle De Ayala 38", "28001", "Generales", "886")])
    report = run_directory_quality(normalize_directory(frame, SPEC), SPEC)
    assert not report.passed


def test_a_contested_entry_is_not_offered_to_a_weaker_rule() -> None:
    entries = [entry("E1", "Calle De Juan Bravo 49")]
    places = [
        place("P1", "de Juan Bravo", 49),
        place("P2", "Juan Bravo", 49),
        place("P3", "de Juan Bravo", None),  # its only candidate on the street is E1
    ]
    resolution = resolve_places(places, entries, KINDS)
    assert resolution.matches == []
    assert set(resolution.unmatched) == {"P1", "P2", "P3"}


def test_a_place_the_directory_lacks_never_inherits_a_leftover_entry() -> None:
    """Uniqueness counts every entry of the postal code, also those already taken."""
    entries = [entry("E1", "Calle De La Maso 38", "28034"), entry("E2", "Calle Otra 1", "28034")]
    places = [place("P1", "de la Masó", 38, "28034"), place("P2", "de Colmenar Viejo", 9, "28034")]
    resolution = resolve_places(places, entries, KINDS)
    assert [m.place_id for m in resolution.matches] == ["P1"]
    assert "P2" in resolution.unmatched


def test_public_and_private_never_match() -> None:
    entries = [entry("E1", "Calle De Arturo Soria 17")]  # «Privados»
    public = RegisterPlace("P1", "Hospital general", "28001", "de Arturo Soria", 17, "publica")
    assert matched([public], entries) == {}
    private = RegisterPlace("P1", "Hospital general", "28001", "de Arturo Soria", 17, "privada")
    assert matched([private], entries) == {"P1": f"E1:{ADDRESS}"}


def test_a_place_without_postal_code_is_declared_unmatched() -> None:
    resolution = resolve_places([place("P1", "de Meco", 1, None)], [entry("E1", "Meco 1")], KINDS)
    assert resolution.unmatched == {"P1": "no postal code in the register"}


def test_street_words_must_be_equal_and_road_positions_are_not_numbers() -> None:
    entries = [entry("E1", "Calle Real de Pozuelo 5"), entry("E2", "Carretera De M-501 KM.17,900")]
    assert matched([place("P1", "Real", 5)], entries) == {}
    assert matched([place("P2", "de M-501", 17)], entries) == {}  # km 17 is not portal 17


def test_a_new_directory_parser_changes_the_register_checksum() -> None:
    from hi_ingestion.pipelines.places.run import directory_input
    from hi_ingestion.pipelines.versions import combined_checksum

    bronze = {
        "dataset_id": "ms_catalogo_nacional_hospitales",
        "role": "primary",
        "path": "data/bronze/datasets/x/CNH_2025.xlsx",
        "sha256": "a" * 64,
        "bytes": 1,
        "url": "https://example.org/CNH_2025.xlsx",
        "retrieved_at": "2026-11-12T00:00:00+00:00",
    }
    old = directory_input({"inputs": [bronze], "parser_version": "directory-1.0.0"})
    new = directory_input({"inputs": [bronze], "parser_version": "directory-1.1.0"})
    assert combined_checksum([old]) != combined_checksum([new])


def test_address_numbers_skip_road_positions_and_postal_codes() -> None:
    from hi_ingestion.pipelines.places.directory import address_numbers

    assert address_numbers("Carretera De M-501 (De Alcorcón A Plasencia) KM.17,900") == {501}
    assert address_numbers("AVENIDA DE ABRANTES, Nº 55 - 57, 28025") == {55, 57}


def test_a_directory_without_capacity_counts_none() -> None:
    from hi_ingestion.pipelines.directory.normalize import published_capacities

    spec = SPEC.model_copy(update={"capacity_column": None, "capacity_unit": None})
    frame = _sheet([("280029", "Hospital A", "Calle De Ayala 38", "28001", "Generales", "886")])
    directory = normalize_directory(frame.drop(columns=["CAMAS"]), spec)
    assert published_capacities(directory) == []
    assert directory.frame["capacity"].tolist() == [None]


def test_bracketed_locality_hints_do_not_break_the_street() -> None:
    entries = [
        entry("E1", "CALLE LA PALOMA, Nº 14", "28722"),
        entry("E2", "Carretera M-515 (Pozuelo) 61"),
    ]
    assert matched([place("P1", "de la Paloma (El Vellón)", 14, "28722")], entries) == {
        "P1": f"E1:{ADDRESS}"
    }
    assert matched([place("P2", "M-515 (POZUELO)", 61)], entries) == {"P2": f"E2:{ADDRESS}"}
