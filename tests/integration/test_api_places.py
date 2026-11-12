"""GET /api/v1/places on the fixture database: zone and subcategory filters, no silent cut."""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import Engine, text

from hi_api.deps import get_engine
from hi_api.main import app
from hi_api.services import places

pytestmark = pytest.mark.db


@pytest.fixture
def client(migrated_engine: Engine, features_computed: None) -> TestClient:
    app.dependency_overrides[get_engine] = lambda: migrated_engine
    return TestClient(app)


def _features(client: TestClient, **params: Any) -> list[dict[str, Any]]:
    response = client.get("/api/v1/places", params={"category": "education", **params})
    assert response.status_code == 200, response.text
    return response.json()["data"]["features"]


def _section_code(feature: dict[str, Any]) -> str | None:
    seccion = feature["properties"]["seccion"]
    return seccion.rsplit(".", 1)[1] if seccion else None


def _ids(features: list[dict[str, Any]]) -> set[str]:
    return {f["id"] for f in features}


def test_district_filter_uses_the_section_each_place_lies_in(client: TestClient) -> None:
    every = _features(client)
    section = next(c for f in every if (c := _section_code(f)) and c.startswith("28079"))
    district = section[:7]
    inside = _features(client, admin_unit_id=f"ES.28.DIS.{district}")
    assert inside
    assert _ids(inside) == {f["id"] for f in every if (_section_code(f) or "")[:7] == district}
    assert len(inside) < len(every)


def test_municipio_and_section_filters(client: TestClient) -> None:
    every = _features(client)
    madrid = _features(client, admin_unit_id="ES.28.MUN.28079")
    assert _ids(madrid) == {f["id"] for f in every if f["properties"]["municipio"] == "28079"}
    seccion = next(f["properties"]["seccion"] for f in every if f["properties"]["seccion"])
    one = _features(client, admin_unit_id=seccion)
    assert one
    assert {f["properties"]["seccion"] for f in one} == {seccion}


def test_subcategory_filter_is_repeatable_and_combines_with_the_zone(client: TestClient) -> None:
    every = _features(client)
    wanted = sorted({f["properties"]["subcategory"] for f in every})[:2]
    some = _features(client, subcategory=wanted)
    assert _ids(some) == {f["id"] for f in every if f["properties"]["subcategory"] in wanted}
    both = _features(client, subcategory=wanted, admin_unit_id="ES.28.MUN.28079")
    assert _ids(both) == {f["id"] for f in some if f["properties"]["municipio"] == "28079"}


def test_unknown_zone_is_404_and_unsupported_level_is_422(
    client: TestClient, migrated_engine: Engine
) -> None:
    params = {"category": "education"}
    assert (
        client.get("/api/v1/places", params={**params, "admin_unit_id": "ES.28.DIS.0"}).status_code
        == 404
    )
    with migrated_engine.connect() as conn:
        barrio = conn.execute(
            text("SELECT admin_unit_id FROM geo_admin_unit WHERE level = 'barrio' LIMIT 1")
        ).scalar_one()
    response = client.get("/api/v1/places", params={**params, "admin_unit_id": barrio})
    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "OUT_OF_COVERAGE"


def test_large_layers_come_in_pages_that_say_how_to_ask_for_the_rest(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vercel answers 4.5 MB at most: a page keeps the payload well below it."""
    complete = client.get("/api/v1/places", params={"category": "education"}).json()
    assert complete["warnings"] == []
    total = complete["data"]["total"]
    assert (complete["data"]["page"], complete["data"]["pages"]) == (1, 1)
    assert total == len(complete["data"]["features"]) > 2
    monkeypatch.setattr(places, "PAGE_SIZE", 2)
    first = client.get("/api/v1/places", params={"category": "education"}).json()
    second = client.get("/api/v1/places", params={"category": "education", "page": 2}).json()
    assert len(first["data"]["features"]) == len(second["data"]["features"]) == 2
    assert first["data"]["total"] == total
    assert first["data"]["pages"] == -(-total // 2)
    assert "?page=2" in first["warnings"][0] and "admin_unit_id" in first["warnings"][0]
    assert not _ids(first["data"]["features"]) & _ids(second["data"]["features"])
    past = client.get("/api/v1/places", params={"category": "education", "page": total})
    assert past.status_code == 422
    assert "last page" in past.json()["detail"]["message"]


def test_hospitals_carry_their_name_and_installed_beds(client: TestClient) -> None:
    """D-218: name and beds from the Catálogo Nacional de Hospitales, matched by address;
    public or private and the type from the CM register (additive inside `capacity`)."""
    response = client.get(
        "/api/v1/places", params={"category": "health", "subcategory": "Hospital general"}
    )
    assert response.status_code == 200, response.text
    by_name = {
        f["properties"]["name"]: f["properties"] for f in response.json()["data"]["features"]
    }
    fuensanta = by_name["Hospital Fuensanta"]
    assert fuensanta["capacity"] == {
        "value": 20.0,
        "unit": "camas instaladas",
        "dataset_id": "ms_catalogo_nacional_hospitales",
        "dependency": "privada",
        "kind": "Hospital general",
    }
    assert by_name["Clínica La Luz"]["capacity"]["value"] == 152.0  # «, S.L.» is not the name
    assert not any(name.startswith("Hospital general (") for name in by_name)
