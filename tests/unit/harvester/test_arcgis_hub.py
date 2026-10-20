import httpx
import respx

from hi_ingestion.bronze import BronzeWriter
from hi_ingestion.catalog_harvester.arcgis_hub import ArcGISHubHarvester, normalize_hub
from hi_ingestion.http import make_client
from tests.unit.harvester.conftest import load_fixture

ITEMS = "https://hub.test/api/search/v1/collections/dataset/items"


def test_normalize_gtfs_item() -> None:
    feature = next(
        f
        for f in load_fixture("hub_features.json")
        if f["properties"]["title"] == "GTFS Red de Metro"
    )
    c = normalize_hub(feature, "crtm_open_data", "https://datos.crtm.es", None)
    assert c.license_id == "CRTM-LDA"
    assert c.name == "crtm_gtfs_red_de_metro"
    assert c.modified_at is not None and c.modified_at.tzinfo is not None
    assert c.resources[0].url and c.external_id in c.resources[0].url


@respx.mock
def test_follows_next_links(bronze: BronzeWriter) -> None:
    features = load_fixture("hub_features.json")
    respx.get(ITEMS, params={"limit": "100"}).mock(
        return_value=httpx.Response(
            200,
            json={"features": features[:1], "links": [{"rel": "next", "href": f"{ITEMS}?page=2"}]},
        )
    )
    respx.get(f"{ITEMS}?page=2").mock(
        return_value=httpx.Response(200, json={"features": features[1:], "links": []})
    )
    with make_client() as client:
        result = ArcGISHubHarvester("crtm_open_data", ITEMS, "https://datos.crtm.es").harvest(
            client, bronze
        )
    assert result.status == "OK"
    assert result.pages == 2
    assert len(result.candidates) == 2
