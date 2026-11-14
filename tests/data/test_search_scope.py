"""data/catalog/zoning/search_scope.yaml (D-238): the official zoning, cited, and the module
the API reads generated from it (run `uv run python scripts/export_search_scope.py`)."""

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
ZONING = REPO_ROOT / "data" / "catalog" / "zoning" / "search_scope.yaml"
MUNICIPIOS, ZONES = 179, 11


def _exporter() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "export_search_scope", REPO_ROOT / "scripts" / "export_search_scope.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _zoning() -> dict[str, Any]:
    return yaml.safe_load(ZONING.read_text(encoding="utf-8"))


def test_the_generated_module_is_up_to_date() -> None:
    exporter = _exporter()
    assert exporter.TARGET.read_text(encoding="utf-8") == exporter.render(_zoning()), (
        "zoning_data.py is stale: uv run python scripts/export_search_scope.py"
    )


def test_the_zoning_cites_its_publication_and_lists_every_municipio_once() -> None:
    zoning = _zoning()
    source = zoning["source"]
    assert "Instituto de Estadística" in source["publisher"]
    assert source["url"].startswith("https://") and source["retrieved_at"]
    assert len(zoning["zones"]) == ZONES
    codes = [m["cm_code"] for zone in zoning["zones"] for m in zone["municipios"]]
    assert len(codes) == len(set(codes)) == MUNICIPIOS
    assert len(_exporter().scope_by_municipio(zoning)) == MUNICIPIOS


def test_the_surroundings_are_the_four_metropolitan_zones() -> None:
    zoning = _zoning()
    names = {zone["code"]: zone["name"] for zone in zoning["zones"]}
    assert [names[code] for code in zoning["scopes"]["madrid"]] == ["Municipio de Madrid"]
    around = [names[code] for code in zoning["scopes"]["alrededores"]]
    assert len(around) == 4 and all(name.endswith("Metropolitano") for name in around)
    assert not any("Metropolitano" in names[code] for code in zoning["scopes"]["pueblos"])
