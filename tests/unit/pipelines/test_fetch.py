from pathlib import Path

import httpx
import pytest
import respx
from tenacity import wait_none

from hi_contracts.catalog import DatasetSpec
from hi_ingestion.http import make_client
from hi_ingestion.pipelines.fetch import download, fetch_role

URL = "https://feeds.test/sharing/rest/content/items/abc123/data"


def _spec(file_name: str | None) -> DatasetSpec:
    resource: dict[str, str] = {"name": "feed.zip", "format": "ZIP", "url": URL}
    if file_name:
        resource["file_name"] = file_name
    return DatasetSpec.model_validate(
        {
            "dataset_id": "crtm_gtfs_test",
            "source_id": "crtm_open_data",
            "name": "Test feed",
            "domain": "transport",
            "owner": "test",
            "format": "ZIP",
            "geography": "point",
            "geo": {"resolution": "point"},
            "refresh_policy": "unknown",
            "license_status": "CLEAR",
            "priority": "P1",
            "resources": [
                resource,
                {
                    "name": "portal",
                    "format": "HTML",
                    "url": "https://portal.test/dataset/x",
                    "role": "cm_portal",
                },
            ],
        }
    )


@respx.mock
def test_download_retries_transient_errors(tmp_path: Path) -> None:
    route = respx.get(URL).mock(
        side_effect=[
            httpx.Response(503),
            httpx.ConnectError("reset"),
            httpx.Response(200, content=b"PK"),
        ]
    )
    dest = tmp_path / "feed.zip"
    with make_client() as client:
        download.retry_with(wait=wait_none())(client, URL, dest)
    assert route.call_count == 3
    assert dest.read_bytes() == b"PK"


@respx.mock
def test_download_asks_for_any_content_type(tmp_path: Path) -> None:
    route = respx.get(URL).mock(return_value=httpx.Response(200, content=b"PK"))
    with make_client() as client:
        download(client, URL, tmp_path / "feed.zip")
    assert route.calls.last.request.headers["accept"] == "*/*"


@respx.mock
def test_fetch_uses_declared_file_name(tmp_path: Path) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=b"PK\x03\x04zip"))
    fetched = fetch_role(_spec("google_transit_M4.zip"), "primary", root=tmp_path)
    assert fetched.path.name == "google_transit_M4.zip"
    assert fetched.path.read_bytes() == b"PK\x03\x04zip"


@respx.mock
def test_fetch_falls_back_to_last_url_segment(tmp_path: Path) -> None:
    respx.get(URL).mock(return_value=httpx.Response(200, content=b"x"))
    assert fetch_role(_spec(None), "primary", root=tmp_path).path.name == "data"


@respx.mock
def test_failed_fetch_leaves_no_partial_file(tmp_path: Path) -> None:
    respx.get(URL).mock(return_value=httpx.Response(404))
    with pytest.raises(httpx.HTTPStatusError):
        fetch_role(_spec("feed.zip"), "primary", root=tmp_path)
    assert not list(tmp_path.rglob("*.part"))
    assert not (tmp_path / "datasets").exists()


def test_file_name_rejects_paths() -> None:
    with pytest.raises(ValueError, match="file_name"):
        _spec("../escape.zip")
