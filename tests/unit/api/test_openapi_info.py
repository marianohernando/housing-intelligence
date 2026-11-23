"""The OpenAPI document says what the API is, its licence, where to find it and how to contact."""

from fastapi.testclient import TestClient

from hi_api.main import app


def test_openapi_info_names_the_api_its_licence_and_its_server() -> None:
    spec = TestClient(app).get("/api/v1/openapi.json").json()
    info = spec["info"]
    assert info["title"] == "Vida Fácil API"
    description = info["description"]
    assert "\n" not in description  # one paragraph
    for words in ("pública y gratuita", "solo lectura", "Comunidad de Madrid", "fuente"):
        assert words in description
    assert "CC BY 4.0" in description  # the data keep their source's licence
    assert info["license"] == {"name": "Apache-2.0", "identifier": "Apache-2.0"}
    assert info["contact"]["url"] == "https://github.com/marianohernando/housing-intelligence"
    assert "email" not in info["contact"]
    assert [s["url"] for s in spec["servers"]] == ["https://vidafacil-madrid.vercel.app"]
