"""Turn scored candidates into dataset drafts, a ranked report and curated promotions."""

import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import HttpUrl, TypeAdapter, ValidationError

from hi_contracts.catalog import DatasetSpec
from hi_contracts.catalog.candidate import CandidateRecord
from hi_contracts.catalog.enums import LicenseStatus, Priority
from hi_domain.catalog.scoring import OPEN_LICENSE_THRESHOLD, ScoredCandidate, score_candidate
from hi_ingestion.catalog.loader import DEFAULT_CATALOG_DIR, DRAFTS_DIRNAME, Catalog
from hi_ingestion.catalog_harvester.common import slugify

DRAFTS_DIR = DEFAULT_CATALOG_DIR / "datasets" / DRAFTS_DIRNAME
CURATED_DIR = DEFAULT_CATALOG_DIR / "datasets"
REPORTS_DIR = DEFAULT_CATALOG_DIR / "reports"
SOURCE_PREFIX = {
    "comunidad_madrid_ckan": "cm",
    "ayuntamiento_madrid_ckan": "ayto",
    "crtm_open_data": "crtm",
    "datos_gob_es": "dge",
}
POINT_RESOLUTIONS = {"point", "parcela", "edificio"}
_URL = TypeAdapter(HttpUrl)
MAX_ID_LEN = 90


def draft_dataset_id(scored: ScoredCandidate) -> str:
    c = scored.candidate
    prefix = SOURCE_PREFIX.get(c.source_id, "ext")
    if c.source_id == "comunidad_madrid_ckan" and c.external_id.isdigit():
        base = f"ie{c.external_id}_{slugify(c.title, 50)}"
    else:
        base = slugify(c.name.removeprefix(f"{prefix}_"), 70)
    dataset_id = f"{prefix}_{base}"[:MAX_ID_LEN].rstrip("_")
    return dataset_id if re.match(r"^[a-z]", dataset_id) else f"x{dataset_id}"


def _valid_url(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return str(_URL.validate_python(value))
    except ValidationError:
        return None


def _resources(scored: ScoredCandidate) -> list[dict[str, str]]:
    resources: list[dict[str, str]] = []
    for r in scored.candidate.resources:
        url = _valid_url(r.url)
        if url:
            resources.append(
                {"name": r.name or "resource", "format": r.format or "UNKNOWN", "url": url}
            )
    return resources


def to_draft(scored: ScoredCandidate) -> dict[str, Any]:
    c = scored.candidate
    card = scored.scorecard
    open_license = (card.license_clarity or 0) >= OPEN_LICENSE_THRESHOLD
    best_format = next((f for f in c.formats if f), "UNKNOWN")
    return {
        "dataset_id": draft_dataset_id(scored),
        "source_id": c.source_id,
        "name": c.title[:200],
        "domain": scored.domain.value,
        "owner": c.publisher or c.source_id,
        "format": best_format,
        "geography": "point" if scored.geo_resolution.value in POINT_RESOLUTIONS else "table",
        "geo": {"resolution": scored.geo_resolution.value},
        "temporal_resolution": None,
        "refresh_policy": (c.update_frequency or "unknown").lower(),
        "landing_url": _valid_url(c.landing_url),
        "resources": _resources(scored),
        "license_status": (
            LicenseStatus.CLEAR if open_license else LicenseStatus.PENDING_REVIEW
        ).value,
        "status": "DISCOVERED",
        "priority": scored.priority_draft.value,
        "scorecard": card.model_dump(mode="json", exclude_none=True),
        "discovery": {
            "harvested_from": c.source_id,
            "external_id": c.external_id,
            "harvested_at": datetime.now(UTC).isoformat(),
        },
        "notes": f"Auto-draft. composite={scored.composite}; license_id={c.license_id}",
    }


def _curated_keys(catalog: Catalog) -> set[str]:
    keys = set(catalog.datasets)
    keys |= {str(d.landing_url).rstrip("/") for d in catalog.datasets.values() if d.landing_url}
    keys |= {f"{d.discovery.harvested_from}:{d.discovery.external_id}"
             for d in catalog.datasets.values() if d.discovery}  # fmt: skip
    return keys


def rank(scored: list[ScoredCandidate]) -> list[ScoredCandidate]:
    order = {Priority.P1: 0, Priority.P2: 1, Priority.P3: 2, Priority.P0: -1}
    return sorted(
        scored, key=lambda s: (order[s.priority_draft], -s.composite, s.candidate.candidate_id)
    )


def write_drafts(scored: list[ScoredCandidate], catalog: Catalog, top: int) -> list[Path]:
    """Regenerates _drafts/ (generated folder) with the top-N non-curated candidates."""
    curated = _curated_keys(catalog)
    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    for old in DRAFTS_DIR.glob("*.yaml"):
        old.unlink()
    written: list[Path] = []
    used_ids: set[str] = set()
    for item in rank(scored):
        c = item.candidate
        landing = (c.landing_url or "").rstrip("/")
        if c.candidate_id in curated or landing in curated:
            continue
        draft = to_draft(item)
        if draft["dataset_id"] in curated or draft["dataset_id"] in used_ids:
            continue
        DatasetSpec.model_validate(draft)
        path = DRAFTS_DIR / f"{draft['dataset_id']}.yaml"
        path.write_text(
            yaml.safe_dump(draft, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        used_ids.add(draft["dataset_id"])
        written.append(path)
        if len(written) >= top:
            break
    return written


def _status_row(h: dict[str, Any]) -> str:
    note = (h.get("message") or "").replace("|", "/")
    return f"| {h['source_id']} | {h['status']} | {h['pages']} | {h['candidates']} | {note} |"


def _curated_rows(catalog: Catalog) -> list[str]:
    order = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    rows = sorted(catalog.datasets.values(), key=lambda d: (order[d.priority.value], d.dataset_id))
    return [
        f"| {d.priority.value} | `{d.dataset_id}` | {d.domain.value} | {d.geo.resolution.value} | "
        f"{d.source_id} | {d.license_status.value} | {d.name.replace('|', '/')[:90]} |"
        for d in rows
    ]


def write_report(
    scored: list[ScoredCandidate],
    harvest_status: list[dict[str, Any]],
    run_label: str,
    catalog: Catalog,
    top: int = 60,
) -> Path:
    curated = _curated_keys(catalog)
    ranked = [s for s in rank(scored) if s.candidate.candidate_id not in curated]
    by_source = Counter(s.candidate.source_id for s in scored)
    by_domain = Counter(s.domain.value for s in scored)
    by_priority = Counter(s.priority_draft.value for s in scored)
    by_license = Counter((s.candidate.license_id or "none") for s in scored)
    lines = [
        f"# Dataset scorecard — {run_label}",
        "",
        "Generado por `hi-ingest catalog draft` con scoring `heuristic-v2`. Los criterios sin",
        "metadatos suficientes quedan pendientes de revisión humana. Ningún borrador es P0.",
        "",
        "## Cosecha por fuente",
        "",
        "| Fuente | Estado | Páginas | Candidatos | Nota |",
        "|---|---|---|---|---|",
        *[_status_row(h) for h in harvest_status],
        "",
        f"Total candidatos puntuados: **{len(scored)}**.",
        "",
        "## Distribución",
        "",
        "| Prioridad borrador | n |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in sorted(by_priority.items())],
        "",
        "| Dominio | n |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in by_domain.most_common()],
        "",
        "| Fuente | n |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in by_source.most_common()],
        "",
        "| Licencia (id en origen) | n |", "|---|---|",
        *[f"| {k} | {v} |" for k, v in by_license.most_common(12)],
        "",
        f"## Catálogo curado ({len(catalog.datasets)} datasets)",
        "",
        "Revisados y aplicados desde `data/catalog/curation/`. P0 = ingerir ya; P1 = siguiente.",
        "",
        "| Prioridad | dataset_id | Dominio | Resolución | Fuente | Licencia | Nombre |",
        "|---|---|---|---|---|---|---|",
        *_curated_rows(catalog),
        "",
        f"## Top {top} candidatos no curados",
        "",
        "| # | Prioridad | Compuesto | Dominio | Granularidad | Fuente | Título |",
        "|---|---|---|---|---|---|---|",
    ]  # fmt: skip
    for i, s in enumerate(ranked[:top], start=1):
        title = s.candidate.title.replace("|", "/")[:110]
        link = f"[{title}]({s.candidate.landing_url})" if s.candidate.landing_url else title
        lines.append(
            f"| {i} | {s.priority_draft.value} | {s.composite} | {s.domain.value} | "
            f"{s.geo_resolution.value} | {s.candidate.source_id} | {link} |"
        )
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"scorecard_{run_label}.md"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def promote(
    draft_path: Path, priority: Priority, reviewed_by: str, overrides: dict[str, Any] | None = None
) -> Path:
    """Move a draft into the curated catalog with an explicit human/agent review."""
    data = yaml.safe_load(draft_path.read_text(encoding="utf-8"))
    data |= overrides or {}
    data["priority"] = priority.value
    data["status"] = "REVIEWED"
    data["scorecard"] = data.get("scorecard", {}) | {
        "reviewed_by": reviewed_by,
        "reviewed_at": datetime.now(UTC).isoformat(),
    }
    spec = DatasetSpec.model_validate(data)
    target = CURATED_DIR / f"{spec.dataset_id}.yaml"
    target.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    draft_path.unlink()
    return target


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)  # pyright: ignore[reportUnknownArgumentType]
        else:
            merged[key] = value
    return merged


def curate(curation_file: Path, candidates: list[CandidateRecord]) -> list[Path]:
    """Apply a versioned curation file: candidate -> curated dataset with explicit review."""
    spec = yaml.safe_load(curation_file.read_text(encoding="utf-8"))
    by_id = {c.candidate_id: c for c in candidates}
    reviewed_at = datetime.now(UTC).isoformat()
    written: list[Path] = []
    missing = [e["candidate_id"] for e in spec["entries"] if e["candidate_id"] not in by_id]
    if missing:
        msg = f"Candidates not found (run catalog harvest): {missing}"
        raise KeyError(msg)
    for entry in spec["entries"]:
        data = _deep_merge(
            to_draft(score_candidate(by_id[entry["candidate_id"]])), entry.get("overrides") or {}
        )
        data["dataset_id"] = entry["dataset_id"]
        data["priority"] = entry["priority"]
        data["status"] = "REVIEWED"
        data["notes"] = (
            f"{entry.get('note', '')} | curated from {curation_file.name} | {data['notes']}"
        )
        data["scorecard"] = data["scorecard"] | {
            "reviewed_by": spec["reviewed_by"],
            "reviewed_at": reviewed_at,
        }
        validated = DatasetSpec.model_validate(data)
        target = CURATED_DIR / f"{validated.dataset_id}.yaml"
        target.write_text(
            yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )
        written.append(target)
    return written
