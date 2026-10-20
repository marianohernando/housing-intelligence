import httpx
import respx

from hi_ingestion.bronze import BronzeWriter
from hi_ingestion.catalog_harvester.ckan import CKANHarvester, normalize_ckan
from hi_ingestion.http import make_client
from tests.unit.harvester.conftest import load_fixture

API = "https://ckan.test/api/3/action"


def _page(results: list[dict[str, object]], count: int) -> dict[str, object]:
    return {"success": True, "result": {"count": count, "results": results}}


def test_normalize_real_package() -> None:
    pkg = next(p for p in load_fixture("ckan_packages.json") if p["name"] == "secciones_censales")
    c = normalize_ckan(pkg, "comunidad_madrid_ckan", "https://datos.comunidad.madrid", None)
    assert c.candidate_id == "comunidad_madrid_ckan:secciones_censales"
    assert c.license_id == "cc-by"
    assert c.landing_url == "https://datos.comunidad.madrid/dataset/secciones_censales"
    assert c.update_frequency == "ANUAL"
    assert {"CSV", "JSON"} <= set(c.formats)


def test_numeric_names_get_alpha_prefix() -> None:
    pkg = next(p for p in load_fixture("ckan_packages.json") if p["name"] == "1934259")
    c = normalize_ckan(pkg, "comunidad_madrid_ckan", "https://datos.comunidad.madrid", None)
    assert c.name.startswith("estadistica_")
    assert c.external_id == "1934259"


@respx.mock
def test_paginates_and_snapshots_every_page(bronze: BronzeWriter) -> None:
    pkgs = load_fixture("ckan_packages.json")
    route = respx.get(f"{API}/package_search")
    route.side_effect = [
        httpx.Response(200, json=_page(pkgs[:2], 3)),
        httpx.Response(200, json=_page(pkgs[2:], 3)),
    ]
    with make_client() as client:
        result = CKANHarvester("comunidad_madrid_ckan", API, "https://ckan.test", rows=2).harvest(
            client, bronze
        )
    assert result.status == "OK"
    assert result.pages == 2
    assert len(result.candidates) == 3
    assert route.calls[1].request.url.params["start"] == "2"
    assert all(c.bronze_ref and len(c.bronze_ref.sha256) == 64 for c in result.candidates)
    assert len(list(bronze.directory.glob("page_*.json"))) == 2


@respx.mock
def test_maintenance_page_is_reported_not_raised(bronze: BronzeWriter) -> None:
    respx.get(f"{API}/package_search").mock(
        return_value=httpx.Response(
            404, text="<html>mantenimiento</html>", headers={"content-type": "text/html"}
        )
    )
    with make_client() as client:
        result = CKANHarvester("ayuntamiento_madrid_ckan", API, "https://ckan.test").harvest(
            client, bronze
        )
    assert result.status == "MAINTENANCE"
    assert result.candidates == []
