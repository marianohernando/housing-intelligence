"""Build pitch/datasets_cm.md: the open datasets the product uses, with licence and Quality Gate.

Which datasets, what each one feeds and its Gate 1 evidence come from data/catalog and
evidence/gate-01, with no network. The official title and licence shown on the Comunidad de
Madrid portal come from a dated snapshot of its CKAN API (pitch/portal_cm_snapshot.json).

Usage:
    uv run python pitch/build_datasets_cm.py                   # offline, deterministic
    uv run python pitch/build_datasets_cm.py --refresh-portal  # re-read titles and licences
"""

import argparse
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

import httpx

from hi_contracts.catalog import DatasetSpec
from hi_domain.gaps import es_number
from hi_ingestion.catalog.loader import Catalog, load_catalog
from hi_ingestion.catalog.provenance import CM_SOURCE_ID, is_cm_open_data, portal_url

ROOT = Path(__file__).resolve().parents[1]
GATE1_DIR = ROOT / "evidence" / "gate-01"
OUTPUT = ROOT / "pitch" / "datasets_cm.md"
SNAPSHOT = ROOT / "pitch" / "portal_cm_snapshot.json"
CKAN_PACKAGE_SHOW = "https://datos.comunidad.madrid/api/3/action/package_show"
# D-226, D-235: features the zone view shows as context; they never score
CONTEXT_LINE = "Dato de contexto en la vista de zona (no puntúa)"
NOT_IN_LIST = (
    "No entra en la lista de lo que falta ni en el buscador: es dato de apoyo o total de la región"
)

ROLE_ES = {
    "primary": "fuente principal",
    "denominator": "denominador",
    "secondary": "fuente de apoyo",
}
CATEGORY_ES = {
    "education": "educación",
    "health": "salud",
    "social": "mayores y atención social",
    "transport": "transporte",
}
MODE_ES = {
    "metro": "metro",
    "metro_ligero": "metro ligero",
    "cercanias": "Cercanías",
    "emt": "autobuses EMT de Madrid",
    "autobus_urbano": "autobuses urbanos del resto de municipios",
    "autobus_interurbano": "autobuses interurbanos",
}
VOLUME_KEYS = [
    ("municipio", "municipios"),
    ("distrito", "distritos censales"),
    ("barrio", "barrios de Madrid"),
    ("seccion_censal", "secciones censales"),
    ("h3_cells", "celdas H3"),
    ("places", "puntos"),
    ("observations", "observaciones"),
    ("total_km", "km de calles y caminos"),
]


@dataclass(frozen=True)
class Gate1:
    day: str
    passed: bool
    critical_ok: int
    critical_total: int
    version: str | None
    volume: str | None
    report: Path


Row = tuple[DatasetSpec, Gate1, dict[str, Any] | None]


def latest_gate1(dataset_id: str) -> Gate1 | None:
    reports = sorted(GATE1_DIR.glob(f"*/{dataset_id}/quality_report.json"))
    if not reports:
        return None
    report = reports[-1]
    quality = json.loads(report.read_text(encoding="utf-8"))
    critical = [check for check in quality["checks"] if check["critical"]]
    lineage = report.with_name("lineage.json")
    counts = report.with_name("row_counts.json")
    return Gate1(
        day=report.parent.parent.name,
        passed=quality["passed"] is True,
        critical_ok=sum(1 for check in critical if check["passed"]),
        critical_total=len(critical),
        version=json.loads(lineage.read_text(encoding="utf-8"))["dataset_version"]
        if lineage.exists()
        else None,
        volume=volume(json.loads(counts.read_text(encoding="utf-8"))) if counts.exists() else None,
        report=report,
    )


def volume(row_counts: dict[str, Any]) -> str | None:
    parts = [
        f"{es_number(row_counts[key], 1 if key == 'total_km' else 0)} {label}"
        for key, label in VOLUME_KEYS
        if isinstance(row_counts.get(key), int | float)
    ]
    return " · ".join(parts) or None


def gap_row_labels(catalog: Catalog) -> dict[str, str]:
    return {
        feature.gap_row.row: feature.gap_row.label
        for feature in catalog.features.values()
        if feature.gap_row and feature.gap_row.label
    }


def where_shown(feature: Any, row_labels: dict[str, str]) -> str:
    gap_row = feature.gap_row
    if gap_row is None and "context_only" in feature.tests:
        return CONTEXT_LINE
    if gap_row is None:
        return "Indicador por zona"
    if gap_row.label:
        return f"«Qué falta», fila «{gap_row.label}»"
    if gap_row.row in row_labels:
        return f"«Qué falta», fila «{row_labels[gap_row.row]}» (dato extra)"
    return f"«Qué falta», fila `{gap_row.row}` (dato extra)"


def uses(catalog: Catalog, dataset: DatasetSpec) -> list[str]:
    lines: list[str] = []
    in_features = False
    row_labels = gap_row_labels(catalog)
    for feature in sorted(catalog.features.values(), key=lambda f: f.feature_id):
        for source in feature.sources:
            if source.dataset_id != dataset.dataset_id:
                continue
            in_features = True
            where = where_shown(feature, row_labels)
            role = ROLE_ES.get(source.role, source.role)
            lines.append(f"{where}: {feature.human_name} (`{feature.feature_id}`, {role})")
    pipeline = catalog.pipelines.get(dataset.dataset_id)
    if pipeline is not None:
        category = getattr(pipeline, "category", None)
        mode = getattr(pipeline, "mode", None)
        if category:
            label = CATEGORY_ES.get(category, category)
            lines.append(f"Puntos del mapa ({label}): `GET /api/v1/places?category={category}`")
        if mode:
            lines.append(
                f"Paradas y estaciones de {MODE_ES.get(mode, mode)} con su frecuencia de paso"
            )
        if pipeline.kind == "osm_walk_network":
            lines.append("Red peatonal para medir la distancia a pie a cada servicio")
        if not in_features:
            lines.extend(
                f"Métrica cargada: {metric.human_name} (`{metric.metric_id}`)"
                for metric in sorted(catalog.metrics.values(), key=lambda m: m.metric_id)
                if metric.dataset_id == dataset.dataset_id
            )
    if dataset.domain == "geography":
        lines.insert(0, "Geografía de todas las zonas del mapa y de la lista de lo que falta")
    if not in_features:
        lines.append(NOT_IN_LIST)
    return lines


def licence(catalog: Catalog, dataset: DatasetSpec, portal: dict[str, Any] | None) -> str:
    source = catalog.sources[dataset.source_id]
    title = portal["license_title"] if portal else source.license_name
    origin = "según el portal CM" if portal else "según el registro de fuentes"
    return f"[{title}]({source.license_url}) ({origin})"


def dataset_block(
    catalog: Catalog, dataset: DatasetSpec, gate: Gate1, portal: dict[str, Any] | None
) -> list[str]:
    name = portal["title"] if portal else dataset.name
    url = portal_url(dataset)
    status = "PASS" if gate.passed else "FAIL"
    report = gate.report.relative_to(ROOT).as_posix()
    gate_parts = [
        status,
        gate.day,
        f"{gate.critical_ok}/{gate.critical_total} checks críticos",
        f"versión `{gate.version}`" if gate.version else None,
        gate.volume,
        f"[quality_report.json](../{report})",
    ]
    lines = [
        f"### {name}",
        f"- **Ficha:** {url} · id `{dataset.dataset_id}` · publica: {dataset.owner}",
    ]
    if portal is None and is_cm_open_data(dataset):
        lines.append("- **Nombre:** el del catálogo; falta verificarlo en el portal")
    if dataset.source_id != CM_SOURCE_ID and is_cm_open_data(dataset):
        download = next((r.url for r in dataset.resources if r.role == "primary"), None)
        note = "fuente original; también tiene ficha en el portal CM"
        lines.append(f"- **Descarga:** {download} ({note})")
    lines.append(f"- **Licencia:** {licence(catalog, dataset, portal)}")
    lines.append("- **Qué alimenta:**")
    lines.extend(f"  - {line}" for line in uses(catalog, dataset))
    lines.append(f"- **Quality Gate 1:** {' · '.join(p for p in gate_parts if p)}")
    lines.append("")
    return lines


def summary_table(rows: list[Row]) -> list[str]:
    lines = ["| # | Dataset | Publica | Gate 1 |", "|---|---|---|---|"]
    for index, (dataset, gate, portal) in enumerate(rows, start=1):
        name = portal["title"] if portal else dataset.name
        status = "PASS" if gate.passed else "FAIL"
        lines.append(
            f"| {index} | [{name}]({portal_url(dataset)}) | {dataset.owner} | {status} {gate.day} |"
        )
    lines.append("")
    return lines


@dataclass(frozen=True)
class Groups:
    cm_own: list[Row]
    cm_partner: list[Row]
    complementary: list[Row]
    not_ingested: list[DatasetSpec]


def group_datasets(catalog: Catalog, portal_rows: dict[str, dict[str, Any]]) -> Groups:
    """Ingested = has Gate 1 evidence. CM = has a page on the CM portal (D-196)."""
    groups = Groups([], [], [], [])
    for dataset_id, dataset in sorted(catalog.datasets.items()):
        gate = latest_gate1(dataset_id)
        if gate is None:
            groups.not_ingested.append(dataset)
            continue
        row = (dataset, gate, portal_rows.get(dataset_id))
        if not is_cm_open_data(dataset):
            groups.complementary.append(row)
        elif dataset.source_id == CM_SOURCE_ID:
            groups.cm_own.append(row)
        else:
            groups.cm_partner.append(row)
    return groups


def render(catalog: Catalog, snapshot: dict[str, Any]) -> str:
    portal_rows: dict[str, dict[str, Any]] = snapshot.get("datasets", {})
    groups = group_datasets(catalog, portal_rows)
    cm_own, cm_partner = groups.cm_own, groups.cm_partner
    complementary, not_ingested = groups.complementary, groups.not_ingested
    cm_rows = cm_own + cm_partner
    cm_pass = sum(1 for _, gate, _ in cm_rows if gate.passed)
    out = [
        "# Datasets que usa Vida Fácil",
        "",
        "> Fichero generado: no se edita a mano. "
        "Se regenera con `uv run python pitch/build_datasets_cm.py`.",
        "> Qué datasets se usan, qué alimentan y su Quality Gate salen de `data/catalog/` y "
        "`evidence/gate-01/`. El nombre oficial y la licencia salen de la API CKAN del portal "
        f"(`pitch/portal_cm_snapshot.json`, leída el {snapshot.get('fetched_at', '—')}).",
        "",
        f"**{len(cm_rows)} datasets del Portal de Datos Abiertos de la Comunidad de Madrid, "
        f"{cm_pass} con Quality Gate 1 en PASS:** {len(cm_own)} publicados por la Comunidad y "
        f"su Instituto de Estadística, y {len(cm_partner)} del Consorcio Regional de Transportes "
        "que también tienen ficha en el portal.",
        "",
        "Solo cuenta como «dataset CM» lo que tiene ficha en el portal "
        "(`hi_ingestion.catalog.provenance.is_cm_open_data`). El resto es complementario.",
        "",
        "## Resumen",
        "",
        *summary_table(cm_rows),
        f"## 1. Portal CM: publicados por la Comunidad de Madrid ({len(cm_own)})",
        "",
    ]
    for dataset, gate, portal in cm_own:
        out += dataset_block(catalog, dataset, gate, portal)
    partner_title = "## 2. Portal CM: horarios y estaciones del CRTM con ficha en el portal"
    out += [f"{partner_title} ({len(cm_partner)})", ""]
    for dataset, gate, portal in cm_partner:
        out += dataset_block(catalog, dataset, gate, portal)
    out += [
        f"## 3. Fuentes complementarias en uso ({len(complementary)})",
        "",
        "No cuentan como datos CM. Sirven para calcular, no sustituyen a una fuente regional.",
        "",
    ]
    for dataset, gate, portal in complementary:
        out += dataset_block(catalog, dataset, gate, portal)
    out += [
        f"## 4. En el catálogo, todavía sin ingerir ({len(not_ingested)})",
        "",
        "Revisados y con licencia clara, pero todavía sin control de calidad: no se citan como "
        "usados.",
        "",
        "| Dataset | Publica | ¿Portal CM? | Ficha |",
        "|---|---|---|---|",
    ]
    for dataset in not_ingested:
        portal = portal_rows.get(dataset.dataset_id)
        name = portal["title"] if portal else dataset.name
        cm = "sí" if is_cm_open_data(dataset) else "no"
        out.append(f"| {name} | {dataset.owner} | {cm} | {portal_url(dataset)} |")
    out.append("")
    return "\n".join(out)


def refresh_snapshot(catalog: Catalog) -> dict[str, Any]:
    rows: dict[str, dict[str, Any]] = {}
    with httpx.Client(timeout=30) as client:
        for dataset_id, dataset in sorted(catalog.datasets.items()):
            url = portal_url(dataset)
            if not is_cm_open_data(dataset) or url is None:
                continue
            slug = url.rstrip("/").rsplit("/dataset/", 1)[-1]
            response = client.get(CKAN_PACKAGE_SHOW, params={"id": slug})
            response.raise_for_status()
            package = response.json()["result"]
            rows[dataset_id] = {
                "slug": slug,
                "title": package["title"].strip(),
                "license_id": package.get("license_id"),
                "license_title": package.get("license_title"),
            }
    return {"fetched_at": date.today().isoformat(), "api": CKAN_PACKAGE_SHOW, "datasets": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build pitch/datasets_cm.md")
    parser.add_argument(
        "--refresh-portal",
        action="store_true",
        help="re-read official titles and licences from the CM portal CKAN API (network)",
    )
    args = parser.parse_args()
    catalog = load_catalog(include_drafts=False)
    if args.refresh_portal:
        snapshot = refresh_snapshot(catalog)
        SNAPSHOT.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8")) if SNAPSHOT.exists() else {}
    OUTPUT.write_text(render(catalog, snapshot), encoding="utf-8")
    print(f"Escrito {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
