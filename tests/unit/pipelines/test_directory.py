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
    MUNICIPALITY,
    ONLY_IN_MUNICIPALITY,
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


# Primary care names, second pass (D-218 §9): the cases the first pass left generic.


def ap_entry(external_id: str, address: str, postal_code: str, municipality: str) -> Entry:
    return Entry(external_id, "X", address, postal_code, "CENTRO SALUD", None, None, municipality)


def ap_place(
    external_id: str, street: str, number: int | None, postal_code: str, municipality: str
) -> RegisterPlace:
    return RegisterPlace(
        external_id, "Centro de salud", postal_code, street, number, "publica", municipality
    )


AP_KINDS = {"Centro de salud": "CENTRO SALUD", "Consultorio de atención primaria": "CONSULTORIO"}


def ap_matched(places: list[RegisterPlace], entries: list[Entry]) -> dict[str, str]:
    resolution = resolve_places(places, entries, AP_KINDS)
    return {m.place_id: f"{m.entry.external_id}:{m.method}" for m in resolution.matches}


def test_another_postcode_of_the_same_municipality_needs_street_and_number() -> None:
    entries = [
        ap_entry("E1", "CALLE CABO MACHICHACO, Nº 62", "28018", "Madrid"),
        ap_entry("E2", "CALLE IBIZA, Nº 7", "28009", "Madrid"),
    ]
    same = ap_place("P1", "del Cabo Machichaco", 62, "28053", "Madrid")
    assert ap_matched([same], entries) == {"P1": f"E1:{MUNICIPALITY}"}
    other_number = ap_place("P1", "del Cabo Machichaco", 60, "28053", "Madrid")
    assert ap_matched([other_number], entries) == {}
    other_municipality = ap_place("P1", "del Cabo Machichaco", 62, "28053", "Getafe")
    assert ap_matched([other_municipality], entries) == {}


def test_the_municipality_rule_needs_a_single_entry_at_that_address() -> None:
    entries = [
        ap_entry("E1", "AVENIDA DE MADRID, Nº 9 - 11", "28822", "Coslada"),
        ap_entry("E2", "AVENIDA DE MADRID, Nº 11", "28823", "Coslada"),
    ]
    assert ap_matched([ap_place("P1", "de Madrid", 11, "28820", "Coslada")], entries) == {}
    assert ap_matched([ap_place("P1", "de Madrid", 11, "28820", "Coslada")], entries[:1]) == {
        "P1": f"E1:{MUNICIPALITY}"
    }


def test_the_municipality_rule_comes_before_the_postcode_rule() -> None:
    """Leganés: «Mª» is María, so P1 takes E1 by address and P2 is not left claiming it."""
    entries = [
        ap_entry("E1", "CALLE Mª ÁNGELES LÓPEZ GÓMEZ, Nº 2", "28915", "Leganés"),
        ap_entry("E2", "AVENIDA DE EUROPA, Nº 1", "28916", "Leganés"),
    ]
    places = [
        ap_place("P1", "María Ángeles López Gómez", 2, "28915", "Leganés"),
        ap_place("P2", "Europa", 1, "28915", "Leganés"),
    ]
    assert ap_matched(places, entries) == {"P1": f"E1:{ADDRESS}", "P2": f"E2:{MUNICIPALITY}"}


@pytest.mark.parametrize(
    ("published", "street", "number", "method"),
    [
        # The catalogue writes «CALLE» for every «CL» and «AVENIDA» for every «AV», also inside
        # a word: San Claudio, Valle Inclán, Isla de Java, a glued «CL» before the street.
        ("CALLE SAN CALLEAUDIO, Nº 154", "de San Claudio", 154, ADDRESS),
        ("CALLE VALLE INCALLEÁN, Nº 97", "de Valle Inclán", 97, ADDRESS),
        ("CALLE ISLA DE JAVENIDAA, S/N", "de la Isla de Java", None, STREET),
        ("CALLEFUENTESPINA, Nº 2", "de Fuentespina", 2, ADDRESS),
        # Abbreviations and street types
        ("AVENIDA DE NTRA SRA DE FÁTIMA, Nº 93", "de Nuestra Señora de Fátima", 93, ADDRESS),
        ("BULEVAR INDALECIO PRIETO, Nº 26", "de Indalecio Prieto", 26, ADDRESS),
        # A corner is on both streets
        ("CALLE ZEUS, esq JOAQUÍN BLUME S/N", "Joaquín Blume", None, STREET),
    ],
)
def test_the_catalogue_spelling_of_a_street_is_the_register_street(
    published: str, street: str, number: int | None, method: str
) -> None:
    entries = [ap_entry("E1", published, "28001", "Madrid")]
    assert ap_matched([ap_place("P1", street, number, "28001", "Madrid")], entries) == {
        "P1": f"E1:{method}"
    }


def test_spelling_variants_never_join_different_streets() -> None:
    entries = [
        ap_entry("E1", "CALLE CLARA CAMPOAMOR, Nº 3", "28001", "Madrid"),
        ap_entry("E2", "CALLE SANTA ENGRACIA, Nº 3", "28001", "Madrid"),
    ]
    assert ap_matched([ap_place("P1", "de Campoamor", 3, "28001", "Madrid")], entries) == {}
    assert ap_matched([ap_place("P2", "de Engracia", 3, "28001", "Madrid")], entries) == {}


def test_the_directory_keeps_the_municipality_of_each_entry() -> None:
    spec = SPEC.model_copy(update={"municipality_column": "Municipio"})
    frame = _sheet([("280029", "Hospital A", "Calle De Ayala 38", "28001", "Generales", "886")])
    frame["Municipio"] = ["Madrid"]
    directory = normalize_directory(frame, spec)
    assert directory.frame["municipality"].tolist() == ["Madrid"]
    assert "Municipio" in spec.kept_columns()


def consultorio(
    external_id: str, street: str, number: int | None, municipality: str
) -> RegisterPlace:
    return RegisterPlace(
        external_id, "Consultorio de atención primaria", "28755", street, number, "publica",
        municipality,
    )  # fmt: skip


def village_entry(external_id: str, address: str, municipality: str) -> Entry:
    return Entry(external_id, "X", address, "28755", "CONSULTORIO", None, None, municipality)


def test_a_postcode_shared_by_villages_never_joins_two_municipalities() -> None:
    """Robregordo and Madarcos share 28755 and both have a «calle de las Eras»."""
    entries = [
        village_entry("E1", "CALLE DE LAS ERAS, Nº 19", "Robregordo"),
        village_entry("E2", "CALLE DE LA IGLESIA, Nº 1", "Madarcos"),
    ]
    entries[1] = Entry("E2", "X", "CALLE DE LA IGLESIA, Nº 1", "28756", "CONSULTORIO", None, None,
                       "Madarcos")  # fmt: skip
    places = [
        consultorio("P1", "de las Eras", 16, "Robregordo"),
        consultorio("P2", "de las Eras", 23, "Madarcos"),
    ]
    assert ap_matched(places, entries) == {
        "P1": f"E1:{STREET}",
        "P2": f"E2:{ONLY_IN_MUNICIPALITY}",
    }


def test_the_only_entry_of_its_kind_in_the_municipality_needs_to_be_alone() -> None:
    two = [
        village_entry("E1", "PLAZA PEDRO UCEDA, Nº 1", "Horcajo de la Sierra-Aoslos"),
        village_entry("E2", "CALLE REAL, Nº 5", "Horcajo de la Sierra-Aoslos"),
        village_entry("E3", "PLAZA MAYOR, Nº 2", "Madarcos"),
    ]
    place = consultorio("P1", "Mayor", 9, "Horcajo de la Sierra-Aoslos")
    assert ap_matched([place], two) == {}
    taken = [village_entry("E1", "CALLE DE LA IGLESIA, Nº 1", "Madarcos")]
    places = [
        consultorio("P1", "de la Iglesia", 1, "Madarcos"),
        consultorio("P2", "Real", 5, "Madarcos"),
    ]
    assert ap_matched(places, taken) == {"P1": f"E1:{ADDRESS}"}  # P2 never inherits it


def test_singular_and_plural_are_the_same_street() -> None:
    """Parla: «Avda de América 6» is the catalogue's «Avenida de las Américas 6», in another
    postal code; the address beats a centre that only shares the postal code."""
    entries = [ap_entry("E1", "AVENIDA DE LAS AMÉRICAS, Nº 6", "28983", "Parla")]
    places = [
        ap_place("P1", "de América", 6, "28981", "Parla"),
        ap_place("P2", "Planeta Venus", 24, "28983", "Parla"),
    ]
    assert ap_matched(places, entries) == {"P1": f"E1:{MUNICIPALITY}"}


def test_a_full_address_holds_even_if_the_catalogue_files_another_municipality() -> None:
    """The catalogue files Aravaca (Madrid) under Pozuelo de Alarcón, its health area."""
    entries = [ap_entry("E1", "CALLE RIAZA, Nº 5", "28023", "Pozuelo de Alarcón")]
    assert ap_matched([ap_place("P1", "de Riaza", 5, "28023", "Madrid")], entries) == {
        "P1": f"E1:{ADDRESS}"
    }
    assert ap_matched([ap_place("P1", "de Riaza", None, "28023", "Madrid")], entries) == {}


def test_below_a_full_address_the_kind_must_agree() -> None:
    """Madrid: a consultorio at Palma 54 (28015) is not the centro de salud at Palma 51."""
    entries = [ap_entry("E1", "CALLE DE LA PALMA, Nº 51", "28015", "Madrid")]
    consultorio_54 = RegisterPlace(
        "P1", "Consultorio de atención primaria", "28015", "de la Palma", 54, "publica", "Madrid"
    )
    centro_51 = ap_place("P2", "de la Palma", 51, "28004", "Madrid")
    assert ap_matched([consultorio_54, centro_51], entries) == {"P2": f"E1:{MUNICIPALITY}"}
    consultorio_51 = RegisterPlace(
        "P3", "Consultorio de atención primaria", "28015", "de la Palma", 51, "publica", "Madrid"
    )
    assert ap_matched([consultorio_51], entries) == {"P3": f"E1:{ADDRESS}"}


def test_a_number_glued_to_its_marker_is_still_a_number() -> None:
    entries = [ap_entry("E1", "CALLE SECTOR OFICIOS, Nº12", "28760", "Tres Cantos")]
    place = ap_place("P1", "Oficios", 12, "28760", "Tres Cantos")
    assert ap_matched([place], entries) == {"P1": f"E1:{ADDRESS}"}


def test_carrera_is_a_street_type() -> None:
    entries = [
        ap_entry("E1", "CALLE CARRERA SAN JERÓNIMO, Nº 32", "28013", "Madrid"),
        ap_entry("E2", "CALLE IBIZA, Nº 7", "28009", "Madrid"),
    ]
    place = ap_place("P1", "de San Jerónimo", 32, "28014", "Madrid")
    assert ap_matched([place], entries) == {"P1": f"E1:{MUNICIPALITY}"}
