"""D-247: the pilot barrios of the investor version (Madrid inside the M-40), a versioned input."""

from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from hi_contracts.catalog.manual import PilotZonesTable, ring_checksum

TABLE = Path(__file__).resolve().parents[3] / "data/catalog/manual/inversores_barrios_m40.yaml"
# Madrid district numbers (code 28079 + 2 digits + barrio digit)
WHOLE = {
    "01": "Centro",
    "02": "Arganzuela",
    "03": "Retiro",
    "04": "Salamanca",
    "05": "Chamartín",
    "06": "Tetuán",
    "07": "Chamberí",
    "10": "Latina",
    "11": "Carabanchel",
    "12": "Usera",
    "13": "Puente de Vallecas",
    "14": "Moratalaz",
    "15": "Ciudad Lineal",
}
PARTLY = {"08": "Fuencarral-El Pardo", "09": "Moncloa-Aravaca", "16": "Hortaleza", "20": "San Blas"}
NONE = {"17": "Villaverde", "18": "Villa de Vallecas", "19": "Vicálvaro", "21": "Barajas"}


@pytest.fixture(scope="module")
def raw() -> dict[str, Any]:
    return yaml.safe_load(TABLE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def table(raw: dict[str, Any]) -> PilotZonesTable:
    return PilotZonesTable.model_validate(raw)


def _district(code: str) -> str:
    return code[5:7]


def test_every_barrio_of_madrid_is_counted_once(table: PilotZonesTable) -> None:
    assert len(table.barrios) + len(table.reviewed_outside) + table.outside == 131


def test_the_pilot_is_the_inner_city_and_parts_of_four_districts(table: PilotZonesTable) -> None:
    inside = {_district(c) for c in table.codes()}
    assert set(WHOLE) <= inside
    assert set(PARTLY) <= inside
    assert not inside & set(NONE)
    outside = {_district(b.code) for b in table.reviewed_outside}
    assert outside <= set(PARTLY)  # the edge barrios left out are of the partial districts


def test_edge_barrios_carry_their_review(table: PilotZonesTable) -> None:
    edge = [b for b in [*table.barrios, *table.reviewed_outside] if table.on_edge(b)]
    assert edge and all(b.review for b in edge)


def test_a_new_edge_barrio_without_review_is_rejected(raw: dict[str, Any]) -> None:
    changed = dict(raw)
    changed["barrios"] = [
        b | {"review": None} if b["code"] == raw["barrios"][0]["code"] else b
        for b in raw["barrios"]
    ]
    first = changed["barrios"][0]
    first["margin_m"] = 10  # now on the edge, with no note
    with pytest.raises(ValidationError, match="review"):
        PilotZonesTable.model_validate(changed)


def test_a_hand_edited_ring_no_longer_matches_its_checksum(raw: dict[str, Any]) -> None:
    ring = dict(raw["ring"])
    coordinates = [list(c) for c in ring["coordinates"]]
    coordinates[1][0] += 1
    ring["coordinates"] = coordinates
    with pytest.raises(ValidationError, match="sha256"):
        PilotZonesTable.model_validate(raw | {"ring": ring})
    assert ring_checksum([tuple(c) for c in raw["ring"]["coordinates"]]) == raw["ring"]["sha256"]
