from datetime import UTC, datetime

import httpx
import respx

from hi_ingestion.bronze import BronzeWriter
from hi_ingestion.catalog_harvester.datos_gob import (
    DatosGobHarvester,
    is_federated_duplicate,
    normalize_dcat,
    parse_spanish_rfc_date,
)
from hi_ingestion.http import make_client
from tests.unit.harvester.conftest import load_fixture

URL = "https://dge.test/apidata/catalog/dataset/spatial/Autonomia/Comunidad-Madrid.json"


def test_parse_spanish_dates() -> None:
    assert parse_spanish_rfc_date("mar, 21 oct 2025 22:00:00 GMT+0000") == datetime(
        2025, 10, 21, 22, tzinfo=UTC
    )
    assert parse_spanish_rfc_date("lun, 17 dic 2018 23:00:00 GMT+0000") == datetime(
        2018, 12, 17, 23, tzinfo=UTC
    )
    assert parse_spanish_rfc_date("garbage") is None
    assert parse_spanish_rfc_date(None) is None


def test_normalize_real_item() -> None:
    item = load_fixture("dcat_items.json")[0]
    c = normalize_dcat(item, "datos_gob_es", None)
    assert c.title
    assert c.landing_url and c.landing_url.startswith("https://datos.gob.es/")
    assert c.name.startswith("dge_")


def test_federated_copies_of_cm_portal_are_detected() -> None:
    item = {
        "_about": "https://datos.gob.es/catalogo/a13-x",
        "distribution": [{"accessURL": "https://datos.comunidad.madrid/dataset/x/resource/y"}],
    }
    assert is_federated_duplicate(item)
    assert not is_federated_duplicate(load_fixture("dcat_items.json")[0])


@respx.mock
def test_stops_when_no_next_page(bronze: BronzeWriter) -> None:
    items = load_fixture("dcat_items.json")
    respx.get(URL).mock(
        return_value=httpx.Response(200, json={"result": {"items": items, "next": None}})
    )
    with make_client() as client:
        result = DatosGobHarvester("datos_gob_es", URL, delay_seconds=0).harvest(client, bronze)
    assert result.pages == 1
    assert len(result.candidates) == len(items)
