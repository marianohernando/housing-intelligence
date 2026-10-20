"""Build harvesters from the Source Registry and persist candidates as JSONL."""

import json
from datetime import date
from pathlib import Path

from hi_contracts.catalog import SourceSpec
from hi_contracts.catalog.candidate import CandidateRecord
from hi_ingestion.bronze import BronzeWriter
from hi_ingestion.catalog.loader import DEFAULT_CATALOG_DIR, Catalog
from hi_ingestion.catalog_harvester.arcgis_hub import ArcGISHubHarvester
from hi_ingestion.catalog_harvester.ckan import CKANHarvester
from hi_ingestion.catalog_harvester.common import Harvester, HarvestResult
from hi_ingestion.catalog_harvester.datos_gob import DatosGobHarvester
from hi_ingestion.http import make_client

CANDIDATES_DIR = DEFAULT_CATALOG_DIR / "candidates"
DATOS_GOB_MADRID_PATH = "/spatial/Autonomia/Comunidad-Madrid.json"
HARVESTABLE: tuple[str, ...] = (
    "comunidad_madrid_ckan",
    "ayuntamiento_madrid_ckan",
    "crtm_open_data",
    "datos_gob_es",
)


def build_harvester(spec: SourceSpec) -> Harvester:
    catalog_url = str(spec.catalog_url)
    base_url = str(spec.base_url)
    if spec.api_type == "ckan":
        return CKANHarvester(spec.source_id, catalog_url.rsplit("/", 1)[0], base_url)
    if spec.api_type == "arcgis_hub":
        return ArcGISHubHarvester(spec.source_id, catalog_url, base_url)
    if spec.api_type == "dcat_apidata":
        return DatosGobHarvester(spec.source_id, catalog_url.rstrip("/") + DATOS_GOB_MADRID_PATH)
    msg = f"No harvester for api_type={spec.api_type} ({spec.source_id})"
    raise ValueError(msg)


def write_candidates(candidates: list[CandidateRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    unique = {c.candidate_id: c for c in candidates}
    lines = [unique[k].model_dump_json(exclude_none=True) for k in sorted(unique)]
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def read_candidates(directory: Path = CANDIDATES_DIR) -> list[CandidateRecord]:
    records: list[CandidateRecord] = []
    for path in sorted(directory.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(CandidateRecord.model_validate_json(line))
    return records


def harvest_sources(
    catalog: Catalog, source_ids: list[str], run_label: str | None = None
) -> list[HarvestResult]:
    run_label = run_label or date.today().isoformat()
    results: list[HarvestResult] = []
    with make_client() as client:
        for source_id in source_ids:
            harvester = build_harvester(catalog.sources[source_id])
            bronze = BronzeWriter(f"catalog/{source_id}", run_label)
            result = harvester.harvest(client, bronze)
            bronze.write_manifest(
                {"status": result.status, "message": result.message, "pages": result.pages}
            )
            if result.candidates:
                write_candidates(result.candidates, CANDIDATES_DIR / f"{source_id}.jsonl")
            results.append(result)
    status_path = DEFAULT_CATALOG_DIR / "reports" / f"harvest_{run_label}.json"
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(
        json.dumps(
            [
                {"source_id": r.source_id, "status": r.status, "pages": r.pages,
                 "candidates": len(r.candidates), "message": r.message}
                for r in results
            ],
            indent=2, ensure_ascii=False,
        ) + "\n"
    )  # fmt: skip
    return results
