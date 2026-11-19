"""D-250: the parcels of Madrid capital with official buildable m², by cadastral reference, for
the search by parcel of the investor version. Two versioned tables in data/catalog/manual/, which
scripts/export_investor_data.py writes into hi_domain.parcel_data (the API image has no data/):

- `veda`: the cadastral parcels of the Ayuntamiento's VEDA viewer (Visor de Edificabilidad,
  Departamento de Análisis Urbano; the layer of plots with buildable area left, July 2026), read
  once from its ArcGIS service. The layer's URL is the `parcels` resource of the dataset
  ayto_edificabilidad_remanente_ambitos in the catalog: its service name carries its date, so a
  new edition changes the catalog, not the code. A parcel split in two pieces of the same area
  counts once, with the pieces added up.
- `portal`: the parcels of Madrid capital in «Parcelas publicadas en el Portal del Suelo 4.0»
  (Comunidad de Madrid, D-246), from the CSV already downloaded to Bronze. Only the columns of
  the parcel are read (reference, label, use and areas), never the contact column.

    uv run python scripts/buildable_parcels.py veda
    uv run python scripts/buildable_parcels.py portal [--csv PATH_TO_THE_CSV]
"""

import argparse
import csv
import json
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import yaml

from hi_contracts.catalog.manual import BuildableParcelsTable
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.http import get_json, make_client

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "data" / "catalog" / "manual"
VEDA_DATASET = "ayto_edificabilidad_remanente_ambitos"
VEDA_TARGET = MANUAL / "veda_parcelas.yaml"
VEDA_FIELDS = "rc14,edificabil,superficie,ORDV_TX_ET,TIPO_SUELO,PROTEGIDA"
PORTAL_DATASET = "cm_parcelas_portal_suelo"
PORTAL_TARGET = MANUAL / "portal_suelo_madrid_parcelas.yaml"
MADRID_CM_CODE = "079"  # municipio_codigo of Madrid in the portal's CSV
PORTAL_USES = {
    "R": "Residencial",
    "T": "Terciario",
    "I": "Industrial",
    "C": "Comercial",
    "O": "Otros",
}

HEADER = """\
# D-250: parcelas de Madrid capital con su edificabilidad oficial, por referencia catastral, para
# la búsqueda por parcela de la versión para inversores. Leídas una vez el día `consulted` por
# scripts/buildable_parcels.py; scripts/export_investor_data.py las pasa a hi_domain.parcel_data.
# No editar a mano.
"""


def dump(path: Path, table: BuildableParcelsTable) -> None:
    body = table.model_dump(mode="json", exclude_none=True)
    head = {k: v for k, v in body.items() if k != "parcels"}
    text = yaml.safe_dump(head, allow_unicode=True, sort_keys=False, width=100)
    rows = [
        yaml.safe_dump([p], allow_unicode=True, sort_keys=False, default_flow_style=None, width=300)
        for p in body["parcels"]
    ]
    path.write_text(HEADER + text + "parcels:\n" + "".join(rows), encoding="utf-8")
    print(f"{len(table.parcels)} parcels -> {path.relative_to(ROOT)}")


# --- VEDA ---


def veda_url() -> str:
    dataset = load_catalog().datasets[VEDA_DATASET]
    return next(str(r.url) for r in dataset.resources if r.role == "parcels")


def veda_parcels(features: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """One entry per parcel: pieces of the same parcel (same planning area) are added up."""
    pieces: dict[str, list[dict[str, Any]]] = {}
    for feature in features:
        attrs = feature["attributes"]
        pieces.setdefault(str(attrs["rc14"]).strip().upper(), []).append(attrs)
    parcels = []
    for rc14, parts in sorted(pieces.items()):
        if len({p["ORDV_TX_ET"] for p in parts}) > 1:
            msg = f"{rc14}: pieces in two planning areas"
            raise ValueError(msg)
        largest = max(parts, key=lambda p: p["edificabil"] or 0)
        use = str(largest["TIPO_SUELO"] or "").strip() or None
        if use and largest["PROTEGIDA"] == "Si" and "PROTEGIDA" not in use:
            use = f"{use} (vivienda protegida)"
        parcels.append(
            {
                "rc14": rc14,
                "buildable_m2": round(sum(p["edificabil"] for p in parts), 2),
                "area_m2": round(sum(p["superficie"] or 0 for p in parts), 1) or None,
                "planning": largest["ORDV_TX_ET"],
                "use": use,
            }
        )
    return parcels


def veda() -> None:
    url = veda_url()
    with make_client(timeout=120) as client:
        layer, _ = get_json(
            client,
            url,
            {"where": "1=1", "outFields": VEDA_FIELDS, "returnGeometry": "false", "f": "json"},
        )
    if layer.get("exceededTransferLimit"):
        raise ValueError("the layer was cut by the service: page the request")
    table = BuildableParcelsTable.model_validate(
        {
            "title": "VEDA Madrid: parcelas catastrales con edificabilidad (julio de 2026)",
            "publisher": "Ayuntamiento de Madrid (VEDA Madrid, Departamento de Análisis Urbano)",
            "url": url,
            "layer": "ANALISIS_URBANO/Visor_Edificabilidad_julio_2026_actual: "
            "Parcelas_Catastrales_julio2026",
            "consulted": datetime.now(UTC).date(),
            "dataset_id": VEDA_DATASET,
            "source_text": "VEDA Madrid (Ayuntamiento de Madrid), julio de 2026: edificabilidad "
            "de la parcela",
            "municipio_ine": "28079",
            "parcels": veda_parcels(layer["features"]),
        }
    )
    dump(VEDA_TARGET, table)


# --- Portal del Suelo ---


def portal_csv() -> tuple[Path, date]:
    """The CSV of the latest version in Bronze and the day it was downloaded, from its manifest."""
    manifests = sorted(
        (ROOT / "data" / "bronze" / "datasets" / PORTAL_DATASET).glob("*/manifest.json"),
        key=lambda p: p.stat().st_mtime,
    )
    if not manifests:
        msg = f"no Bronze version of {PORTAL_DATASET}: make ingest DATASET={PORTAL_DATASET}"
        raise FileNotFoundError(msg)
    entry = json.loads(manifests[-1].read_text())["files"][0]
    return ROOT / entry["path"], datetime.fromisoformat(entry["retrieved_at"]).date()


def spanish_m2(value: str) -> float | None:
    """«516,6» -> 516.6. A dot would be read as thousands («12.192»): it stops the script."""
    text = value.strip()
    if not text:
        return None
    if "." in text:
        msg = f"area with a dot: {text!r}"
        raise ValueError(msg)
    return float(text.replace(",", "."))


def portal_parcels(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        rows = [r for r in reader if r["municipio_codigo"] == MADRID_CM_CODE]
    parcels = []
    for row in rows:
        buildable = spanish_m2(row["superficie_edificable"])
        rc14 = row["referencia_catastral_14"].strip().upper()
        if buildable is None or not rc14:
            print(f"skipped {row['referencia_codigo']}: no buildable area or no reference")
            continue
        parcels.append(
            {
                "rc14": rc14,
                "buildable_m2": buildable,
                "area_m2": spanish_m2(row["superficie_registrada"]),
                "planning": row["parcela_descripcion"].strip() or None,
                "use": PORTAL_USES.get(row["uso_principal_codigo"].strip().upper()),
                "ref": row["referencia_codigo"].strip(),
            }
        )
    return sorted(parcels, key=lambda p: p["rc14"])


def portal(csv_path: Path | None) -> None:
    path, consulted = (csv_path, datetime.now(UTC).date()) if csv_path else portal_csv()
    dataset = load_catalog().datasets[PORTAL_DATASET]
    table = BuildableParcelsTable.model_validate(
        {
            "title": "Portal del Suelo 4.0: parcelas de Madrid capital y su superficie edificable",
            "publisher": "Comunidad de Madrid (Dirección General de Suelo)",
            "url": str(dataset.resources[0].url),
            "layer": path.name,
            "consulted": consulted,
            "dataset_id": PORTAL_DATASET,
            "source_text": "Portal del Suelo 4.0 (Comunidad de Madrid): superficie edificable "
            "publicada de la parcela",
            "municipio_ine": "28079",
            "parcels": portal_parcels(path),
        }
    )
    dump(PORTAL_TARGET, table)


def main() -> None:
    parser = argparse.ArgumentParser(description="Parcels of Madrid with official buildable m²")
    parser.add_argument("table", choices=["veda", "portal"])
    parser.add_argument("--csv", type=Path, default=None, help="the Portal del Suelo CSV")
    args = parser.parse_args()
    if args.table == "veda":
        veda()
    else:
        portal(args.csv)


if __name__ == "__main__":
    main()
