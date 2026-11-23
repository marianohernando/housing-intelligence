"""D-252: the state of development of each planning area (ámbito) of the Plan General, for the
search by parcel of the investor version, into data/catalog/manual/pgoum_ambitos_estado.yaml.

- «PGOUM 97. Estado de desarrollo de los ámbitos» (datos.madrid.es 203200, CC BY 4.0): the four
  phases of each ámbito (planeamiento, gestión, proyecto y obras de urbanización).
- «PGOUM 97. Edificabilidad remanente en ámbitos» (VEDA, 203182, CC BY 4.0): the situation of
  the ámbitos with buildable m² left (pending planning, management or building). An ámbito in
  two stages takes the least advanced one.

Reads the files the ingestion already keeps in bronze (their manifest says which) and writes our
fields, never the files. scripts/export_investor_data.py turns the YAML into
hi_domain.ambit_status.

    uv run python scripts/pgoum_ambitos_estado.py
"""

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from python_calamine import CalamineWorkbook

ROOT = Path(__file__).resolve().parents[1]
BRONZE = ROOT / "data" / "bronze" / "datasets"
TARGET = ROOT / "data" / "catalog" / "manual" / "pgoum_ambitos_estado.yaml"
PHASES = ("Ámbito", "Estado de desarrollo. Planeamiento", "Estado de desarrollo. Gestión")
URBANIZATION = (
    "Estado de desarrollo.Urbanización. Proyecto",
    "Estado de desarrollo. Urbanización. Obras",
)
VEDA_STAGES = {
    "PENDIENTE PLAN SECTORIZACION": "pendiente_sectorizacion",
    "PENDIENTE PLANEAMIENTO DESARROLLO": "pendiente_planeamiento",
    "FASE GESTION Y/O URBANIZACION": "gestion_urbanizacion",
    "FASE DE EDIFICACION": "edificacion",
}
STAGE_ORDER = list(VEDA_STAGES.values())  # least advanced first


def bronze_file(dataset_id: str) -> tuple[Path, dict[str, Any]]:
    """The primary file of the newest bronze manifest of a dataset."""
    manifests = sorted(
        (BRONZE / dataset_id).glob("*/manifest.json"), key=lambda p: p.stat().st_mtime
    )
    if not manifests:
        raise SystemExit(f"{dataset_id}: no bronze manifest (run its ingestion first)")
    entry = next(
        f for f in json.loads(manifests[-1].read_text())["files"] if f["role"] == "primary"
    )
    path = ROOT / entry["path"]
    if not path.exists():
        raise SystemExit(f"{dataset_id}: {path.name} is not in bronze (run its ingestion first)")
    return path, entry


def rows_of(path: Path) -> tuple[list[str], list[list[Any]]]:
    sheet = CalamineWorkbook.from_path(str(path)).get_sheet_by_index(0).to_python()
    header = [str(h).strip() for h in sheet[0]]
    return header, [r for r in sheet[1:] if any(str(c).strip() for c in r)]


def text(value: Any) -> str:
    return " ".join(str(value).split())


def development(path: Path) -> tuple[dict[str, list[str]], str]:
    header, rows = rows_of(path)
    columns = [header.index(c) for c in (*PHASES, *URBANIZATION)]
    as_of = header.index("Estado del desarrollo a fecha")
    ambits: dict[str, list[str]] = {}
    for row in rows:
        code, *phases = (text(row[i]) for i in columns)
        if code in ambits:
            raise SystemExit(f"203200: {code} is twice")
        ambits[code] = phases
    dates = {str(r[as_of])[:10] for r in rows}
    if len(dates) != 1:
        raise SystemExit(f"203200: several dates {sorted(dates)}")
    return ambits, dates.pop()


def veda_stages(path: Path) -> dict[str, str]:
    header, rows = rows_of(path)
    code_at, stage_at = header.index("COD_AMBITO"), header.index("SITUACION DEL ÁMBITO")
    stages: dict[str, str] = {}
    for row in rows:
        code, raw = text(row[code_at]), text(row[stage_at])
        stage = VEDA_STAGES.get(raw)
        if stage is None:
            raise SystemExit(f"203182: unknown situation {raw!r} of {code}")
        known = stages.get(code)
        if known is None or STAGE_ORDER.index(stage) < STAGE_ORDER.index(known):
            stages[code] = stage
    return stages


def main() -> int:
    dev_path, dev_entry = bronze_file("ayto_pgoum_desarrollo_ambitos")
    veda_path, veda_entry = bronze_file("ayto_edificabilidad_remanente_ambitos")
    ambits, as_of = development(dev_path)
    stages = veda_stages(veda_path)
    entries = []
    for code in sorted(set(ambits) | set(stages)):
        entry: dict[str, Any] = {"code": code}
        if code in ambits:
            entry["phases"] = ambits[code]
        if code in stages:
            entry["veda"] = stages[code]
        entries.append(entry)
    spec = {
        "title": "Estado de desarrollo de los ámbitos del Plan General de 1997",
        "publisher": "Ayuntamiento de Madrid (Área de Urbanismo)",
        "license": "CC BY 4.0",
        "development": {
            "dataset": "203200",
            "url": dev_entry["url"],
            "sha256": dev_entry["sha256"],
            "as_of": as_of,
            "phases": ["planeamiento", "gestion", "proyecto_urbanizacion", "obras_urbanizacion"],
        },
        "veda": {
            "dataset": "203182",
            "url": veda_entry["url"],
            "sha256": veda_entry["sha256"],
        },
        "ambits": entries,
    }
    header = (
        "# D-252: estado de desarrollo de cada ámbito del Plan General: sus cuatro fases\n"
        "# (203200) y su situación en VEDA (203182), para la búsqueda por parcela. Escrito por\n"
        "# scripts/pgoum_ambitos_estado.py desde los ficheros de bronze; scripts/export_investor_\n"
        "# data.py lo pasa a hi_domain.ambit_status. No editar a mano.\n"
    )
    body = yaml.safe_dump(
        spec, allow_unicode=True, sort_keys=False, width=100, default_flow_style=None
    )
    TARGET.write_text(header + body, encoding="utf-8")
    print(
        f"{len(entries)} ámbitos ({len(ambits)} con fases, {len(stages)} en VEDA) -> {TARGET.name}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
