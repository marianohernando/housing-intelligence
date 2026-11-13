"""Coordinate repair against the declared address (D-216) and the classification fixes (T1)."""

import pandas as pd
import pytest

from hi_contracts.catalog.enums import PlaceCategory
from hi_contracts.catalog.pipeline import PointsPipeline
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.pipelines.places.coordinates import (
    GEOCODED,
    SOURCE,
    Declared,
    GeocodeHit,
    Located,
    fold_name,
    house_number,
    resolve,
    same_street,
)
from hi_ingestion.pipelines.places.geocoder import hit_from_answer
from hi_ingestion.pipelines.places.normalize import Repair, normalize_places

MADRID, VALDEMORO = "28079", "28161"
CARABANCHEL, TETUAN = "2807911", "2807906"


def locate(lon: float, lat: float) -> Located:
    """Toy geography: west of -3.70 is Carabanchel, east is Tetuán; south of 40.25 Valdemoro."""
    if lat < 40.25:
        return Located(VALDEMORO, None)
    return Located(MADRID, CARABANCHEL if lon < -3.70 else TETUAN)


class geocoder:  # noqa: N801 - reads like the function it replaces in the tests
    """Fake geocoder that records what it was asked."""

    def __init__(self, answers: dict[str, GeocodeHit | None]) -> None:
        self.answers = answers
        self.asked: list[str] = []

    def __call__(self, query: str) -> GeocodeHit | None:
        self.asked.append(query)
        return self.answers.get(query)


def test_coherent_coordinates_are_kept_and_the_geocoder_is_never_asked() -> None:
    geocode = geocoder({})
    got = resolve((-3.71, 40.40), Declared(MADRID, CARABANCHEL, "calle A 1"), locate, geocode)
    assert (got.lon, got.lat, got.origin, got.note) == (-3.71, 40.40, SOURCE, None)
    assert geocode.asked == []


def test_missing_coordinates_take_the_portal_inside_the_declared_municipio() -> None:
    hit = GeocodeHit(-3.68, 40.82, "28094", "portal", 56, "X")
    got = resolve(
        None,
        Declared("28094", None, "calle Eras de Arriba 56", 56, "de X"),
        locate,
        geocoder({"calle Eras de Arriba 56": hit}),
    )
    assert (got.lon, got.lat, got.origin) == (-3.68, 40.82, GEOCODED)


@pytest.mark.parametrize(
    "hit",
    [
        None,
        GeocodeHit(-3.68, 40.82, "28094", "callejero", None),  # only the street: too vague on foot
        GeocodeHit(-3.68, 40.82, "28006", "portal", 1, "X"),  # a portal, but in another municipio
    ],
)
def test_missing_coordinates_without_a_good_portal_stay_in_quarantine(
    hit: GeocodeHit | None,
) -> None:
    got = resolve(
        None, Declared("28094", None, "calle X 1", 1, "de X"), locate, geocoder({"calle X 1": hit})
    )
    assert not got.accepted
    assert got.quarantine_reason


def test_coordinates_in_another_municipio_are_replaced_by_the_address() -> None:
    """D3: a Madrid pharmacy whose coordinates fall in Valdemoro."""
    hit = GeocodeHit(-3.70, 40.40, MADRID, "portal", 36, "X")
    declared = Declared(MADRID, None, "Afueras a Valverde 36, Madrid", 36, "de X")
    got = resolve((-3.68, 40.19), declared, locate, geocoder({declared.address or "": hit}))
    assert (got.lon, got.lat, got.origin) == (-3.70, 40.40, GEOCODED)


def test_coordinates_in_another_municipio_without_address_are_quarantined_never_kept() -> None:
    got = resolve((-3.68, 40.19), Declared(MADRID, None, None), locate, geocoder({}))
    assert not got.accepted
    assert "28161" in (got.quarantine_reason or "")


def test_wrong_district_is_fixed_only_when_the_address_lands_in_the_declared_one() -> None:
    """D4: CEIP Amorós, address in Carabanchel, coordinates in Tetuán."""
    address = "calle Joaquín Turina 37"
    hit = GeocodeHit(-3.75, 40.38, MADRID, "portal", 27, "X")
    got = resolve(
        (-3.69, 40.45),
        Declared(MADRID, CARABANCHEL, address, 37, "de X"),
        locate,
        geocoder({address: hit}),
    )
    assert (got.lon, got.lat, got.origin) == (-3.75, 40.38, GEOCODED)


def test_district_label_alone_never_moves_a_place() -> None:
    """D5: the address agrees with the coordinates; only the register's district label differs."""
    address = "calle María Reiche 34"
    hit = GeocodeHit(
        -3.69, 40.46, MADRID, "portal", 34, "X"
    )  # also in "Tetuán" in the toy geography
    got = resolve(
        (-3.69, 40.45),
        Declared(MADRID, CARABANCHEL, address, 37, "de X"),
        locate,
        geocoder({address: hit}),
    )
    assert (got.lon, got.lat, got.origin) == (-3.69, 40.45, SOURCE)
    assert got.note and "kept" in got.note


def test_geocoder_answer_needs_a_point_and_a_municipio() -> None:
    assert hit_from_answer(None) is None
    assert (
        hit_from_answer({"lng": 0.0, "lat": 0.0, "muniCode": "28022", "type": "callejero"}) is None
    )
    answer = {"lng": -3.67, "lat": 40.82, "muniCode": "28094", "type": "portal", "portalNumber": 56}
    assert hit_from_answer(answer | {"address": "X"}) == GeocodeHit(
        -3.67, 40.82, "28094", "portal", 56, "X"
    )


@pytest.mark.parametrize(
    ("name", "folded"),
    [
        ("Álamo (El)", "el alamo"),
        ("El Álamo", "el alamo"),
        ("ROZAS DE MADRID (LAS)", "las rozas de madrid"),
    ],
)
def test_municipio_names_fold_to_one_key(name: str, folded: str) -> None:
    assert fold_name(name) == folded


@pytest.fixture(scope="module")
def catalog() -> Catalog:
    return load_catalog()


def _points(catalog: Catalog, dataset_id: str) -> PointsPipeline:
    spec = catalog.pipelines[dataset_id]
    assert isinstance(spec, PointsPipeline)
    return spec


def test_normalize_repairs_and_marks_lower_confidence(catalog: Catalog) -> None:
    spec = _points(catalog, "cm_oficinas_farmacia")
    frame = pd.DataFrame(
        [
            {
                "FARMACIA_NRO_SOE": "1",
                "DIRECCION_VIAL_TIPO": "CALLE",
                "DIRECCION_VIAL_NOMBRE": "Atocha",
                "DIRECCION_VIAL_NRO": "1",
                "MUNICIPIO_NOMBRE": "Madrid",
                "LOCALIZACION_COORDENADA_X": "",
                "LOCALIZACION_COORDENADA_Y": "",
            },
            {
                "FARMACIA_NRO_SOE": "2",
                "DIRECCION_VIAL_TIPO": "CALLE",
                "DIRECCION_VIAL_NOMBRE": "B",
                "DIRECCION_VIAL_NRO": "2",
                "MUNICIPIO_NOMBRE": "Madrid",
                "LOCALIZACION_COORDENADA_X": "",
                "LOCALIZACION_COORDENADA_Y": "",
            },
        ]
    )
    hit = GeocodeHit(-3.70, 40.42, MADRID, "portal", 1, "ATOCHA")
    repair = Repair(locate, geocoder({"CALLE Atocha 1, Madrid": hit}), {"madrid": MADRID})
    places = normalize_places(frame, spec, repair)
    assert places.frame["external_id"].tolist() == ["1"]
    row = places.frame.iloc[0]
    assert row["confidence"] == pytest.approx(0.8)
    assert row["attributes"]["coordinates"]["origin"] == GEOCODED
    assert places.quarantine["external_id"].tolist() == ["2"]
    assert places.repairs["external_id"].tolist() == ["1"]


def test_pharmacies_are_their_own_category_and_never_health(catalog: Catalog) -> None:
    """T1: pharmacies used to fill the health-care layer (category health)."""
    assert _points(catalog, "cm_oficinas_farmacia").category == PlaceCategory.PHARMACY
    for feature in catalog.features.values():
        formula = feature.formula.model_dump()
        subs = formula.get("subcategories") or []
        if "Farmacia" in subs:
            category = formula.get("destination_category") or formula.get("category")
            assert category == PlaceCategory.PHARMACY.value, feature.feature_id


def test_private_polyclinics_are_not_health_places(catalog: Catalog) -> None:
    """T1: 1,001 «Centro Polivalente» (RD 1277/2003 C.2.90, private clinics) are out (D-216)."""
    kinds = _points(catalog, "cm_centros_sanitarios").row_filters["centro_tipo"]
    assert "Centro Polivalente" not in kinds
    assert {"Centro de salud", "Consultorio de atención primaria", "Hospital general"} <= set(kinds)


@pytest.mark.parametrize(
    "dataset_id",
    [
        "cm_centros_educativos",
        "cm_centros_sanitarios",
        "cm_centros_atencion_social",
        "cm_oficinas_farmacia",
    ],
)
def test_facility_registers_declare_an_address_and_a_municipio(
    catalog: Catalog, dataset_id: str
) -> None:
    spec = _points(catalog, dataset_id)
    assert spec.address_template
    assert spec.municipio_code_column or spec.municipio_name_column


@pytest.mark.parametrize(
    ("portal", "number", "confidence"),
    [(56, 56, 0.8), (46, 56, 0.6), (45, 56, None), (1, None, None)],
)
def test_portal_must_match_the_house_number(
    portal: int, number: int | None, confidence: float | None
) -> None:
    """CartoCiudad answers some portal even without a number, or the nearest one it knows."""
    hit = GeocodeHit(-3.68, 40.82, "28094", "portal", portal, "X")
    got = resolve(
        None, Declared("28094", None, "calle Q", number, "de X"), locate, geocoder({"calle Q": hit})
    )
    assert (got.confidence if got.accepted else None) == confidence


@pytest.mark.parametrize(
    ("raw", "number"), [("37", 37), ("83-85", 83), ("5 BIS", 5), ("S/N", None), ("", None)]
)
def test_house_number_takes_the_first_number(raw: str, number: int | None) -> None:
    assert house_number(raw) == number


def test_a_portal_on_another_street_is_never_taken() -> None:
    """CartoCiudad matches loosely: same municipio and number, but another street."""
    hit = GeocodeHit(-3.68, 40.82, "28094", "portal", 56, "ERAS DE ABAJO")
    declared = Declared("28094", None, "calle Eras de Arriba 56", 56, "Eras de Arriba")
    assert not resolve(None, declared, locate, geocoder({"calle Eras de Arriba 56": hit})).accepted


@pytest.mark.parametrize(
    ("matched", "declared", "same"),
    [
        ("JOAQUIN TURINA", "de Joaquín Turina", True),
        ("ARENAS DEL REY", "de Arenas del Rey", True),
        ("REAL", "Real", True),
        ("VILLARES", "Real", False),
        ("ALCALA", "de Alcalá de Henares", False),
        (None, "Real", False),
    ],
)
def test_street_names_are_compared_without_articles_or_accents(
    matched: str | None, declared: str, same: bool
) -> None:
    assert same_street(matched, declared) is same


def test_missing_declared_municipio_never_accepts_a_portal() -> None:
    hit = GeocodeHit(-3.68, 40.82, "28094", "portal", 56, "X")
    declared = Declared(None, None, "calle X 56", 56, "X")
    assert not resolve(None, declared, locate, geocoder({"calle X 56": hit})).accepted
