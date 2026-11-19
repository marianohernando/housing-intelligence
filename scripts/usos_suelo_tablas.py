"""D-252c: the plan's buildable m² by use of every urban parcel of Madrid (USOS_SUELO, tables 4
«Uso cualificado principal» and 5 «Otros usos cualificados»; Ayuntamiento de Madrid, datos.madrid.es
300744, CC BY 4.0), read once into bronze and into two versioned tables that
scripts/export_investor_data.py turns into hi_domain.plan_uses_data:

- data/catalog/manual/usos_suelo_edificabilidad.csv: the rows with a figure, by CODIGO (= UBOV_ID
  of the urban parcel), principal (table 4) or other use (table 5);
- data/catalog/manual/usos_suelo_parcelas.csv: the CODIGO ranges of table 4. Every urban parcel
  has one row there with its principal use, most of them without a figure: a parcel in table 4
  and not in the first file has a principal use and no figure.

Live, a cold query of one CODIGO takes 6,5–10 s on sigma's side (D-252c): the search by parcel
reads this snapshot instead. Polite to the service: the count and the ids of each table, then
windows of at most 2000 OBJECTIDs (its maxRecordCount), one at a time with a pause (26 requests).

    uv run python scripts/usos_suelo_tablas.py               # download into bronze, then build
    uv run python scripts/usos_suelo_tablas.py --from-bronze # build from the newest bronze copy
"""

import csv
import hashlib
import io
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import httpx

ROOT = Path(__file__).resolve().parents[1]
SERVICE = "https://sigma.madrid.es/hosted/rest/services/DESARROLLO_URBANO_ACTUALIZADO/USOS_SUELO/MapServer"
TABLES = {4: True, 5: False}  # table: principal use
FIELDS = "OBJECTID,ETIQUETA,USO,EDIFICABIL,UNIDAD,CODIGO"
PAGE = 2000
PAUSE_S = 0.6
DATASET = "ayto_usos_suelo_urbanismo"
LANDING = "https://datos.madrid.es/dataset/300744-0-usos-suelo-urbanismo"
BRONZE = ROOT / "data" / "bronze" / "datasets" / DATASET
MANUAL = ROOT / "data" / "catalog" / "manual"
FIGURES = MANUAL / "usos_suelo_edificabilidad.csv"
PARCELS = MANUAL / "usos_suelo_parcelas.csv"
USER_AGENT = "VidaFacil/0.1 (+https://vidafacil-madrid.vercel.app/desarrolladores)"


def query(client: httpx.Client, table: int, **params: str) -> dict[str, Any]:
    response = client.get(f"{SERVICE}/{table}/query", params={"f": "json", **params})
    response.raise_for_status()
    payload = response.json()
    if "error" in payload:
        raise SystemExit(f"table {table}: {payload['error']}")
    time.sleep(PAUSE_S)
    return payload


def read_table(client: httpx.Client, table: int) -> list[dict[str, Any]]:
    count = query(client, table, where="1=1", returnCountOnly="true")["count"]
    ids = sorted(query(client, table, where="1=1", returnIdsOnly="true")["objectIds"])
    if len(ids) != count:
        raise SystemExit(f"table {table}: {len(ids)} ids for a count of {count}")
    rows: list[dict[str, Any]] = []
    for start in range(0, len(ids), PAGE):
        low, high = ids[start], ids[min(start + PAGE, len(ids)) - 1]
        where = f"OBJECTID >= {low} AND OBJECTID <= {high}"
        page = query(client, table, where=where, outFields=FIELDS, returnGeometry="false")
        rows += [f["attributes"] for f in page.get("features") or []]
        print(f"table {table}: {len(rows)}/{count}")
    if len(rows) != count or len({r["OBJECTID"] for r in rows}) != count:
        raise SystemExit(f"table {table}: {len(rows)} rows read for a count of {count}")
    return rows


def download() -> None:
    retrieved = datetime.now(UTC)
    raw: dict[int, list[dict[str, Any]]] = {}
    with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=60) as client:
        for table in TABLES:
            raw[table] = read_table(client, table)
    blobs = {t: json.dumps(r, ensure_ascii=False, sort_keys=True).encode() for t, r in raw.items()}
    folder = BRONZE / hashlib.sha256(b"".join(blobs.values())).hexdigest()[:12]
    folder.mkdir(parents=True, exist_ok=True)
    files = []
    for table, blob in blobs.items():
        path = folder / f"tabla_{table}.json"
        path.write_bytes(blob)
        files.append(
            {
                "dataset_id": DATASET,
                "role": "primary",
                "path": str(path.relative_to(ROOT)),
                "sha256": hashlib.sha256(blob).hexdigest(),
                "bytes": len(blob),
                "rows": len(raw[table]),
                "url": f"{SERVICE}/{table}/query",
                "retrieved_at": retrieved.isoformat(),
            }
        )
    manifest = {"files": files, "landing_url": LANDING, "license": "CC BY 4.0"}
    (folder / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


def newest_bronze() -> tuple[dict[int, list[dict[str, Any]]], str]:
    manifests = sorted(BRONZE.glob("*/manifest.json"), key=lambda p: p.stat().st_mtime)
    if not manifests:
        raise SystemExit("no bronze copy: run without --from-bronze")
    entries = json.loads(manifests[-1].read_text())["files"]
    raw = {
        int(Path(e["path"]).stem.split("_")[1]): json.loads((ROOT / e["path"]).read_text())
        for e in entries
    }
    retrieved = datetime.fromisoformat(entries[0]["retrieved_at"])
    return raw, retrieved.astimezone(ZoneInfo("Europe/Madrid")).date().isoformat()


def text(value: Any) -> str:
    return " ".join(str(value or "").split())


def figure(value: float) -> str:
    return str(int(value)) if value == int(value) else repr(value)


def build() -> None:
    raw, day = newest_bronze()
    kept = sorted(
        (int(r["CODIGO"]), 1 if TABLES[t] else 0, text(r["USO"]), float(r["EDIFICABIL"]),
         text(r["UNIDAD"]))
        for t, rows in raw.items()
        for r in rows
        if r.get("CODIGO") is not None and (r.get("EDIFICABIL") or 0) > 0 and text(r.get("USO"))
    )  # fmt: skip
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["codigo", "principal", "uso", "edificabil", "unidad"])
    writer.writerows([c, p, u, figure(v), unit] for c, p, u, v, unit in kept)
    total = sum(len(rows) for rows in raw.values())
    FIGURES.write_text(
        "# D-252c: edificabilidad por uso de cada parcela urbanística (USOS_SUELO, tablas 4 y 5;\n"
        f"# Ayuntamiento de Madrid, {LANDING}, CC BY 4.0), leída el {day} por\n"
        f"# scripts/usos_suelo_tablas.py: de {total} filas, las {len(kept)} con cifra.\n"
        "# Información urbanística sin valor jurídico. No editar a mano.\n" + out.getvalue(),
        encoding="utf-8",
    )
    codes = sorted(int(r["CODIGO"]) for r in raw[4] if r.get("CODIGO") is not None)
    runs: list[list[int]] = []
    for code in codes:
        if runs and code == runs[-1][1] + 1:
            runs[-1][1] = code
        else:
            runs.append([code, code])
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(["desde", "hasta"])
    writer.writerows(runs)
    PARCELS.write_text(
        "# D-252c: los CODIGO de la tabla 4 de USOS_SUELO (una fila por parcela urbanística,\n"
        f"# con su uso principal, casi siempre sin cifra), en tramos. Leída el {day}.\n"
        "# No editar a mano.\n" + out.getvalue(),
        encoding="utf-8",
    )
    print(f"{len(kept)} rows -> {FIGURES.name} ({FIGURES.stat().st_size} B)")
    print(
        f"{len(codes)} parcels in {len(runs)} ranges -> {PARCELS.name} ({PARCELS.stat().st_size} B)"
    )


def main() -> int:
    if "--from-bronze" not in sys.argv:
        download()
    build()
    return 0


if __name__ == "__main__":
    sys.exit(main())
