"""datos.gob.es linked-data API harvester, restricted to Comunidad de Madrid coverage."""

import re
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import httpx

from hi_contracts.catalog.candidate import BronzeRef, CandidateRecord, CandidateResource
from hi_ingestion.bronze import BronzeWriter
from hi_ingestion.catalog_harvester.common import HarvestResult, dedupe, slugify, snapshot_page
from hi_ingestion.http import SourceUnavailableError, get_json

MONTHS = {
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}  # fmt: skip
_DATE = re.compile(r"(\d{1,2}) (\w{3}) (\d{4}) (\d{2}):(\d{2}):(\d{2})")
DUPLICATE_PORTALS = ("datos.comunidad.madrid",)  # harvested directly, skip federated copies


def parse_spanish_rfc_date(value: str | None) -> datetime | None:
    """'mar, 21 oct 2025 22:00:00 GMT+0000' -> aware datetime (UTC)."""
    if not value:
        return None
    match = _DATE.search(value)
    if not match or match.group(2).lower() not in MONTHS:
        return None
    day, mon, year, hh, mm, ss = match.groups()
    return datetime(int(year), MONTHS[mon.lower()], int(day), int(hh), int(mm), int(ss), tzinfo=UTC)


def _lang_value(field: Any, lang: str = "es") -> str:
    values = field if isinstance(field, list) else [field]
    texts = [v for v in values if isinstance(v, dict)]
    for v in texts:
        if v.get("_lang") == lang:
            return str(v.get("_value", ""))
    if texts:
        return str(texts[0].get("_value", ""))
    return str(values[0]) if values and values[0] is not None else ""


def _distributions(item: dict[str, Any]) -> list[CandidateResource]:
    raw = item.get("distribution") or []
    dists = raw if isinstance(raw, list) else [raw]
    resources: list[CandidateResource] = []
    for dist in dists:
        if not isinstance(dist, dict):
            continue
        fmt = dist.get("format")
        fmt_value = fmt.get("value") if isinstance(fmt, dict) else fmt
        resources.append(
            CandidateResource(
                name=_lang_value(dist.get("title")) or None,
                format=str(fmt_value).split("/")[-1].upper() if fmt_value else None,
                url=dist.get("accessURL"),
            )
        )
    return resources


def is_federated_duplicate(item: dict[str, Any]) -> bool:
    urls = [str(r.url or "") for r in _distributions(item)] + [str(item.get("identifier") or "")]
    return any(portal in url for url in urls for portal in DUPLICATE_PORTALS)


def normalize_dcat(
    item: dict[str, Any], source_id: str, bronze_ref: BronzeRef | None
) -> CandidateRecord:
    about = str(item["_about"])
    external_id = about.rstrip("/").rsplit("/", 1)[-1]
    title = _lang_value(item.get("title")) or external_id
    resources = _distributions(item)
    keywords = item.get("keyword") or []
    keywords = keywords if isinstance(keywords, list) else [keywords]
    themes = item.get("theme") or []
    themes = themes if isinstance(themes, list) else [themes]
    spatial = item.get("spatial") or []
    spatial = spatial if isinstance(spatial, list) else [spatial]
    return CandidateRecord(
        candidate_id=f"{source_id}:{external_id}",
        source_id=source_id,
        external_id=external_id,
        name=f"dge_{slugify(external_id, 70)}",
        title=title,
        description=_lang_value(item.get("description")),
        tags=dedupe(
            [_lang_value(k) for k in keywords] + [str(t).rsplit("/", 1)[-1] for t in themes]
        ),
        formats=dedupe([r.format or "" for r in resources]),
        landing_url=about,
        resources=resources,
        publisher=str(item.get("publisher") or "").rsplit("/", 1)[-1] or None,
        license_id=None,
        license_title=None,
        modified_at=parse_spanish_rfc_date(item.get("modified")),
        geographic_coverage=", ".join(str(s).rsplit("/", 1)[-1] for s in spatial)[:300] or None,
        update_frequency=None,
        extra={"n_spatial": len(spatial), "slug": slugify(title)},
        bronze_ref=bronze_ref,
    )


@dataclass
class DatosGobHarvester:
    source_id: str
    spatial_url: str
    page_size: int = 50
    max_pages: int = 80
    delay_seconds: float = 0.3

    def harvest(self, client: httpx.Client, bronze: BronzeWriter) -> HarvestResult:
        result = HarvestResult(source_id=self.source_id)
        skipped = 0
        try:
            for page in range(self.max_pages):
                params = {"_pageSize": self.page_size, "_page": page}
                payload, response = get_json(client, self.spatial_url, params)
                ref = snapshot_page(bronze, page + 1, payload, response)
                items = payload["result"].get("items", [])
                for item in items:
                    if is_federated_duplicate(item):
                        skipped += 1
                        continue
                    result.candidates.append(normalize_dcat(item, self.source_id, ref))
                result.pages = page + 1
                if not payload["result"].get("next") or not items:
                    break
                time.sleep(self.delay_seconds)
            else:
                result.status = "PARTIAL"
                result.message = f"stopped at max_pages={self.max_pages}"
        except SourceUnavailableError as exc:
            result.status, result.message = ("PARTIAL" if result.pages else "MAINTENANCE"), str(exc)
        if skipped:
            note = f"skipped {skipped} federated copies of directly harvested portals"
            result.message = f"{result.message}; {note}" if result.message else note
        return result
