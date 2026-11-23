"""Build pitch/datasets_cm.md: the open datasets the product uses, with licence and Quality Gate.

Which datasets, what each one feeds and its Gate 1 evidence come from data/catalog and
evidence/gate-01, with no network. The official title and licence shown on the Comunidad de
Madrid portal come from a dated snapshot of its CKAN API (pitch/portal_cm_snapshot.json). The
MELODA reusability score of each CM dataset comes from a dated snapshot of the API of the
spain.meloda.org Monitorizador (pitch/meloda_cm_snapshot.json; data under CC BY 4.0), matched by
the exact URL of the dataset's page on the CM portal. The Monitorizador scores 6 dimensions
(D1–D6, 0 to 49); MELODA 5 itself has 8.

Usage:
    uv run python pitch/build_datasets_cm.py                   # offline, deterministic
    uv run python pitch/build_datasets_cm.py --refresh-portal  # re-read titles and licences
    uv run python pitch/build_datasets_cm.py --refresh-meloda  # re-read MELODA (~25 requests)
"""

import argparse
import json
import time
from collections import Counter
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from statistics import mean
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
MELODA_SNAPSHOT = ROOT / "pitch" / "meloda_cm_snapshot.json"
MELODA_API = "https://spain.meloda.org/api/v1"
MELODA_CM_PORTAL = "comunidad_madrid"
# The CRTM's own portal, where its datasets are downloaded from: only its portal-level figures
MELODA_PORTALS = (MELODA_CM_PORTAL, "data_crtm_opendata_arcgis_com")
MELODA_PAUSE_S = 2.5  # the API allows 60 requests a minute per IP
MELODA_PAGE_SIZE = 100  # the API's maximum
# (API field, label, top level the API gives, points in the 0–49 total: spain.meloda.org/sobre.php)
MELODA_DIMENSIONS = [
    ("d1_license", "licencia", 3, 6),
    ("d2_access", "acceso", 3, 6),
    ("d3_format", "formato", 3, 6),
    ("d4_standard", "estandarización", 4, 10),
    ("d5_geo", "geolocalización", 3, 6),
    ("d6_frequency", "frecuencia de actualización", 5, 15),
]
REUSABILITY_ES = {
    "optimum": "óptimo",
    "good": "bueno",
    "basic": "básico",
    "deficient": "deficiente",
}
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


def meloda_key(url: str | None) -> str:
    """The same dataset page with or without a trailing slash or capitals."""
    return (url or "").strip().rstrip("/").lower()


def meloda_score(entry: dict[str, Any]) -> str:
    """«18/49, básico · licencia 3/3 · …», as the API gives it: the total is not the sum."""
    level = REUSABILITY_ES.get(entry["reusability"], entry["reusability"])
    parts = [f"{entry['total']}/49, {level}"]
    for key, label, top, _ in MELODA_DIMENSIONS:
        value = entry[key]
        shown = f"{value}/{top}" if 0 <= value <= top else f"{value} (fuera de 0–{top})"
        parts.append(f"{label} {shown}")
    return " · ".join(parts)


def meloda_cell(dataset: DatasetSpec, meloda_rows: dict[str, dict[str, Any]]) -> str | None:
    """None when MELODA does not apply: not a CM dataset, or no MELODA snapshot yet."""
    if not meloda_rows or not is_cm_open_data(dataset):
        return None
    entry = meloda_rows.get(dataset.dataset_id)
    if entry is None:
        return "no encontrado"
    return f"{meloda_score(entry)} · [API]({MELODA_API}/datasets/{entry['meloda_id']})"


def dataset_block(
    catalog: Catalog,
    dataset: DatasetSpec,
    gate: Gate1,
    portal: dict[str, Any] | None,
    meloda: str | None = None,
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
    if meloda:
        lines.append(f"- **MELODA (Monitorizador spain.meloda.org):** {meloda}")
    lines.append("")
    return lines


def summary_table(rows: list[Row], meloda_rows: dict[str, dict[str, Any]]) -> list[str]:
    lines = ["| # | Dataset | Publica | Gate 1 | MELODA |", "|---|---|---|---|---|"]
    for index, (dataset, gate, portal) in enumerate(rows, start=1):
        name = portal["title"] if portal else dataset.name
        status = "PASS" if gate.passed else "FAIL"
        entry = meloda_rows.get(dataset.dataset_id)
        level = f"{entry['total']}, {REUSABILITY_ES[entry['reusability']]}" if entry else "—"
        lines.append(
            f"| {index} | [{name}]({portal_url(dataset)}) | {dataset.owner} | {status} {gate.day} "
            f"| {level} |"
        )
    lines.append("")
    return lines


def mean_text(values: list[int]) -> str:
    return es_number(mean(values), 1) if values else "—"


def levels_text(entries: list[dict[str, Any]]) -> str:
    counts = Counter(entry["reusability"] for entry in entries)
    parts = [f"{counts[key]} {label}" for key, label in REUSABILITY_ES.items() if counts[key]]
    return ", ".join(parts[:-1]) + f" y {parts[-1]}" if len(parts) > 1 else "".join(parts)


def dimension_rows(entries: list[dict[str, Any]], portal: dict[str, Any]) -> list[str]:
    lines = [
        f"| Dimensión | Nivel máximo | Puntos en el total | Los {len(entries)} que usamos: "
        "cuántos con cada nivel | Media del portal CM |",
        "|---|---|---|---|---|",
    ]
    for key, label, top, points in MELODA_DIMENSIONS:
        counts = sorted(Counter(entry[key] for entry in entries).items(), reverse=True)
        spread = " · ".join(f"{value}: {count}" for value, count in counts)
        portal_mean = es_number(portal["dimension_means"][key], 2)
        lines.append(f"| {label.capitalize()} | {top} | {points} | {spread} | {portal_mean} |")
    return lines


def meloda_section(cm_own: list[Row], cm_partner: list[Row], meloda: dict[str, Any]) -> list[str]:
    """The reusability of the CM datasets we use, from the MELODA snapshot, with no network."""
    rows: dict[str, dict[str, Any]] = meloda.get("datasets", {})
    if not rows:
        return []
    own = [rows[d.dataset_id] for d, _, _ in cm_own if d.dataset_id in rows]
    partner = [rows[d.dataset_id] for d, _, _ in cm_partner if d.dataset_id in rows]
    used = own + partner
    totals = [entry["total"] for entry in used]
    cm_portal = meloda["portals"][MELODA_CM_PORTAL]
    crtm_portal = meloda["portals"][MELODA_PORTALS[1]]
    return [
        "## Reutilización según MELODA",
        "",
        f"> Fuente: spain.meloda.org. {meloda['method']}; datos bajo {meloda['license']}. "
        f"API leída el {meloda['fetched_at']}; cosecha del portal CM del "
        f"{cm_portal['last_harvest'][:10]}. Instantánea: `pitch/meloda_cm_snapshot.json`. "
        "Cada dataset se empareja por la URL exacta de su ficha en datos.comunidad.madrid: "
        f"{len(used)} de {len(cm_own) + len(cm_partner)} encontrados.",
        "",
        f"- **Los {len(used)} datasets CM que usamos:** media de {mean_text(totals)} sobre 49 "
        f"(de {min(totals)} a {max(totals)}): {levels_text(used)}.",
        f"- **Publicados por la Comunidad ({len(own)}):** media de "
        f"{mean_text([e['total'] for e in own])}. **Del CRTM con ficha en el portal CM "
        f"({len(partner)}):** media de {mean_text([e['total'] for e in partner])}; MELODA puntúa "
        "su ficha en el portal CM, y los datos se descargan del portal del CRTM.",
        f"- **Todo el portal CM en MELODA:** {es_number(cm_portal['datasets_harvested'], 0)} "
        f"datasets, media de {es_number(cm_portal['meloda']['avg_score'], 1)}. **El portal del "
        f"CRTM:** {es_number(crtm_portal['datasets_harvested'], 0)} datasets, media de "
        f"{es_number(crtm_portal['meloda']['avg_score'], 1)} (sus datasets no se emparejan uno a "
        "uno).",
        "",
        *dimension_rows(used, cm_portal),
        "",
        "La puntuación y los niveles son los que da la API del Monitorizador, sin recalcular: el "
        "total pondera cada dimensión con sus puntos (spain.meloda.org, «Sobre el proyecto»). El "
        "Monitorizador puntúa seis dimensiones (D1–D6); MELODA 5 tiene ocho, con difusión y "
        "reputación (presentación de la formación de DATAMAD del 5 nov, diapositiva 43). "
        "La puntuación se calcula solo con los "
        "metadatos públicos de la ficha del portal, no con el contenido del dataset. Un nivel "
        "fuera del rango que documenta la API (como −1 en geolocalización) se deja como viene.",
        "",
    ]


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


def render(catalog: Catalog, snapshot: dict[str, Any], meloda: dict[str, Any]) -> str:
    portal_rows: dict[str, dict[str, Any]] = snapshot.get("datasets", {})
    meloda_rows: dict[str, dict[str, Any]] = meloda.get("datasets", {})
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
        f"(`pitch/portal_cm_snapshot.json`, leída el {snapshot.get('fetched_at', '—')}). "
        "La puntuación MELODA sale de la API de spain.meloda.org "
        f"(`pitch/meloda_cm_snapshot.json`, leída el {meloda.get('fetched_at', '—')}; "
        "Fuente: spain.meloda.org, CC BY 4.0).",
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
        *summary_table(cm_rows, meloda_rows),
        *meloda_section(cm_own, cm_partner, meloda),
        f"## 1. Portal CM: publicados por la Comunidad de Madrid ({len(cm_own)})",
        "",
    ]
    for dataset, gate, portal in cm_own:
        out += dataset_block(catalog, dataset, gate, portal, meloda_cell(dataset, meloda_rows))
    partner_title = "## 2. Portal CM: horarios y estaciones del CRTM con ficha en el portal"
    out += [f"{partner_title} ({len(cm_partner)})", ""]
    for dataset, gate, portal in cm_partner:
        out += dataset_block(catalog, dataset, gate, portal, meloda_cell(dataset, meloda_rows))
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
        "| Dataset | Publica | ¿Portal CM? | Ficha | MELODA |",
        "|---|---|---|---|---|",
    ]
    for dataset in not_ingested:
        portal = portal_rows.get(dataset.dataset_id)
        name = portal["title"] if portal else dataset.name
        cm = "sí" if is_cm_open_data(dataset) else "no"
        entry = meloda_rows.get(dataset.dataset_id)
        level = f"{entry['total']}, {REUSABILITY_ES[entry['reusability']]}" if entry else "—"
        if entry is None and meloda_rows and is_cm_open_data(dataset):
            level = "no encontrado"
        out.append(f"| {name} | {dataset.owner} | {cm} | {portal_url(dataset)} | {level} |")
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


def meloda_get(client: httpx.Client, path: str, params: dict[str, Any] | None = None) -> Any:
    time.sleep(MELODA_PAUSE_S)
    response = client.get(f"{MELODA_API}{path}", params=params)
    response.raise_for_status()
    return response.json()


def fetch_meloda(client: httpx.Client) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """The portals list and every dataset of the CM portal: 1 + 23 requests on 20 Nov 2026."""
    portals = meloda_get(client, "/portals")["data"]
    rows: list[dict[str, Any]] = []
    page, pages = 1, 1
    while page <= pages:
        params = {"page": page, "page_size": MELODA_PAGE_SIZE, "sort": "title"}
        body = meloda_get(client, f"/portals/{MELODA_CM_PORTAL}/datasets", params)
        rows += body["data"]
        pages = body["meta"]["pages"]
        page += 1
    return portals, rows


def meloda_snapshot(
    catalog: Catalog, portals: list[dict[str, Any]], rows: list[dict[str, Any]], fetched_at: str
) -> dict[str, Any]:
    """Match each CM dataset by the exact URL of its CM portal page; never by title."""
    wanted = {
        meloda_key(portal_url(dataset)): dataset_id
        for dataset_id, dataset in catalog.datasets.items()
        if is_cm_open_data(dataset) and portal_url(dataset)
    }
    matched: dict[str, dict[str, Any]] = {}
    for row in rows:
        dataset_id = wanted.get(meloda_key(row["url"]))
        if dataset_id and row.get("meloda"):
            keep = {"meloda_id": row["id"], "url": row["url"], "source_id": row["source_id"]}
            matched[dataset_id] = {**keep, "harvested_at": row["harvested_at"], **row["meloda"]}
    scored = [row["meloda"] for row in rows if row.get("meloda")]
    kept = ("name", "url", "last_harvest", "datasets_harvested", "meloda")
    portal_rows = {
        p["id"]: {k: p.get(k) for k in kept} for p in portals if p["id"] in MELODA_PORTALS
    }
    portal_rows[MELODA_CM_PORTAL]["dimension_means"] = {
        key: round(mean(score[key] for score in scored), 2) for key, _, _, _ in MELODA_DIMENSIONS
    }
    return {
        "fetched_at": fetched_at,
        "source": "spain.meloda.org",
        "attribution": "Fuente: spain.meloda.org",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "method": "Monitorizador spain.meloda.org (MELODA 5): 6 dimensiones D1–D6, de 0 a 49",
        "api": f"{MELODA_API}/portals/{MELODA_CM_PORTAL}/datasets",
        "match": "URL exacta de la ficha del dataset en datos.comunidad.madrid",
        "portals": portal_rows,
        "datasets": matched,
    }


def refresh_meloda(catalog: Catalog) -> dict[str, Any]:
    with httpx.Client(timeout=60) as client:
        portals, rows = fetch_meloda(client)
    return meloda_snapshot(catalog, portals, rows, date.today().isoformat())


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


def main() -> None:
    parser = argparse.ArgumentParser(description="Build pitch/datasets_cm.md")
    parser.add_argument(
        "--refresh-portal",
        action="store_true",
        help="re-read official titles and licences from the CM portal CKAN API (network)",
    )
    parser.add_argument(
        "--refresh-meloda",
        action="store_true",
        help="re-read MELODA scores from the spain.meloda.org API (network, ~25 requests)",
    )
    args = parser.parse_args()
    catalog = load_catalog(include_drafts=False)
    if args.refresh_portal:
        write_json(SNAPSHOT, refresh_snapshot(catalog))
    if args.refresh_meloda:
        write_json(MELODA_SNAPSHOT, refresh_meloda(catalog))
    OUTPUT.write_text(
        render(catalog, read_json(SNAPSHOT), read_json(MELODA_SNAPSHOT)), encoding="utf-8"
    )
    print(f"Escrito {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
