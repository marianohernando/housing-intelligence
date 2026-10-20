"""CKAN harvester (datos.comunidad.madrid, datos.madrid.es)."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx

from hi_contracts.catalog.candidate import BronzeRef, CandidateRecord, CandidateResource
from hi_ingestion.bronze import BronzeWriter
from hi_ingestion.catalog_harvester.common import (
    HarvestResult,
    dedupe,
    iter_pages,
    slugify,
    snapshot_page,
)
from hi_ingestion.http import SourceUnavailableError, get_json

EXTRA_COVERAGE = "Cobertura geográfica"
EXTRA_FREQUENCY = "Frecuencia de actualización de datos"


def _parse_dt(value: str | None) -> datetime | None:
    return datetime.fromisoformat(value) if value else None


def normalize_ckan(
    pkg: dict[str, Any], source_id: str, landing_base: str, bronze_ref: BronzeRef | None
) -> CandidateRecord:
    extras = {e["key"]: e["value"] for e in pkg.get("extras", []) if "key" in e}
    resources = [
        CandidateResource(name=r.get("name"), format=(r.get("format") or None), url=r.get("url"))
        for r in pkg.get("resources", [])
    ]
    org = pkg.get("organization") or {}
    name = str(pkg["name"])
    return CandidateRecord(
        candidate_id=f"{source_id}:{name}",
        source_id=source_id,
        external_id=name,
        name=name if name[:1].isalpha() else f"{org.get('name', 'ds')}_{name}",
        title=str(pkg.get("title") or name),
        description=str(pkg.get("notes") or ""),
        tags=dedupe([t.get("name", "") for t in pkg.get("tags", [])]),
        formats=dedupe([(r.format or "").upper() for r in resources]),
        landing_url=f"{landing_base.rstrip('/')}/dataset/{name}",
        resources=resources,
        publisher=org.get("title"),
        license_id=pkg.get("license_id"),
        license_title=pkg.get("license_title"),
        modified_at=_parse_dt(pkg.get("metadata_modified")),
        geographic_coverage=extras.get(EXTRA_COVERAGE),
        update_frequency=extras.get(EXTRA_FREQUENCY),
        extra={"organization": org.get("name"), "slug": slugify(str(pkg.get("title") or name))},
        bronze_ref=bronze_ref,
    )


@dataclass
class CKANHarvester:
    source_id: str
    api_base: str  # .../api/3/action
    landing_base: str
    rows: int = 1000

    def harvest(self, client: httpx.Client, bronze: BronzeWriter) -> HarvestResult:
        result = HarvestResult(source_id=self.source_id)
        url = f"{self.api_base.rstrip('/')}/package_search"
        try:
            first, response = get_json(client, url, {"rows": self.rows, "start": 0})
        except SourceUnavailableError as exc:
            result.status, result.message = "MAINTENANCE", str(exc)
            return result
        total = int(first["result"]["count"])
        for page, start in enumerate(iter_pages(total, self.rows), start=1):
            if start == 0:
                payload = first
            else:
                payload, response = get_json(client, url, {"rows": self.rows, "start": start})
            ref = snapshot_page(bronze, page, payload, response)
            for pkg in payload["result"]["results"]:
                result.candidates.append(
                    normalize_ckan(pkg, self.source_id, self.landing_base, ref)
                )
            result.pages = page
        if len(result.candidates) < total:
            result.status = "PARTIAL"
            result.message = f"expected {total}, got {len(result.candidates)}"
        return result
