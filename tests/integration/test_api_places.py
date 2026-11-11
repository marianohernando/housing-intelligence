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


def test_reaching_the_cap_is_warned_never_silent(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    complete = client.get("/api/v1/places", params={"category": "education"}).json()
    assert complete["warnings"] == []
    monkeypatch.setattr(places, "MAX_PLACES", 1)
    capped = client.get("/api/v1/places", params={"category": "education"}).json()
    assert len(capped["data"]["features"]) == 1
    assert capped["warnings"] and "admin_unit_id" in capped["warnings"][0]
