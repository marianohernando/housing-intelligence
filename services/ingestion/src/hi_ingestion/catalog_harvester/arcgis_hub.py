"""ArcGIS Hub OGC API Records harvester (datos.crtm.es)."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from hi_contracts.catalog.candidate import BronzeRef, CandidateRecord, CandidateResource
from hi_ingestion.bronze import BronzeWriter
from hi_ingestion.catalog_harvester.common import HarvestResult, dedupe, slugify, snapshot_page
from hi_ingestion.http import SourceUnavailableError, get_json

CRTM_LICENSE_MARKER = "crtm.es/licencia"
HUB_ITEM_DATA_URL = "https://www.arcgis.com/sharing/rest/content/items/{item_id}/data"


def _epoch_ms(value: Any) -> datetime | None:
    return datetime.fromtimestamp(value / 1000, tz=UTC) if isinstance(value, int | float) else None


def normalize_hub(
    feature: dict[str, Any], source_id: str, landing_base: str, bronze_ref: BronzeRef | None
) -> CandidateRecord:
    props: dict[str, Any] = feature.get("properties") or {}
    item_id = str(feature.get("id") or props["id"])
    title = str(props.get("title") or item_id)
    license_info = str(props.get("licenseInfo") or "")
    item_type = str(props.get("type") or "")
    return CandidateRecord(
        candidate_id=f"{source_id}:{item_id}",
        source_id=source_id,
        external_id=item_id,
        name=f"crtm_{slugify(title, 50)}",
        title=title,
        description=str(props.get("snippet") or props.get("description") or ""),
        tags=dedupe([str(t) for t in props.get("tags") or []]),
        formats=dedupe(
            [item_type.upper(), *[str(k).upper() for k in props.get("typeKeywords") or []]]
        ),
        landing_url=f"{landing_base.rstrip('/')}/datasets/{item_id}",
        resources=[
            CandidateResource(
                name=str(props.get("name") or title),
                format=item_type,
                url=HUB_ITEM_DATA_URL.format(item_id=item_id),
            )
        ],
        publisher=str(props.get("source") or props.get("owner") or "CRTM"),
        license_id="CRTM-LDA" if CRTM_LICENSE_MARKER in license_info else props.get("license"),
        license_title="CRTM Licencia de datos abiertos (LDA)"
        if CRTM_LICENSE_MARKER in license_info
        else None,
        modified_at=_epoch_ms(props.get("modified")),
        geographic_coverage="Comunidad de Madrid",
        update_frequency=None,
        extra={"item_type": item_type, "size_bytes": props.get("size"), "slug": slugify(title)},
        bronze_ref=bronze_ref,
    )


@dataclass
class ArcGISHubHarvester:
    source_id: str
    items_url: str
    landing_base: str
    limit: int = 100
    max_pages: int = 20

    def harvest(self, client: httpx.Client, bronze: BronzeWriter) -> HarvestResult:
        result = HarvestResult(source_id=self.source_id)
        url: str | None = self.items_url
        params: dict[str, Any] | None = {"limit": self.limit}
        page = 0
        client.headers["Accept"] = "application/geo+json, application/json"
        try:
            while url and page < self.max_pages:
                payload, response = get_json(client, url, params)
                page += 1
                ref = snapshot_page(bronze, page, payload, response)
                for feature in payload.get("features", []):
                    result.candidates.append(
                        normalize_hub(feature, self.source_id, self.landing_base, ref)
                    )
                nxt = [lnk["href"] for lnk in payload.get("links", []) if lnk.get("rel") == "next"]
                url, params = (nxt[0], None) if nxt else (None, None)
        except SourceUnavailableError as exc:
            result.status, result.message = ("PARTIAL" if page else "MAINTENANCE"), str(exc)
        result.pages = page
        return result
