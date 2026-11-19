"""D-248: the construction cost the viability v0 starts from, recomputed from the official file.

Reads «Visados, superficie y presupuesto de dirección de obra de edificios por tipo de obra y
características de los edificios» (portal de datos abiertos de la Comunidad de Madrid, dataset
1006022; Estadística de Obras en Edificación del Ministerio de Vivienda y Agenda Urbana) and
divides, for each year, the budget of works (PEM, thousands of euros) of the new buildings of
homes in blocks («viviendas en bloque») by the area they will build (m²): the PEM per m² built
that the permits declare. Also the single-family homes, for context. Writes
data/catalog/manual/pem_visados_cm.yaml with the dataset, the file, the day it was read, the
file's checksum and each year's figures, so the viability reads a versioned number and never
one typed from memory. Then `scripts/export_investor_data.py` carries it into the API image.

    uv run python scripts/pem_visados_cm.py            # download and write the YAML
    uv run python scripts/pem_visados_cm.py --csv FILE # the same from a file already downloaded
"""

import csv
import hashlib
import io
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import yaml

from hi_ingestion.http import get_json, make_client, polite_retry

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "data" / "catalog" / "manual" / "pem_visados_cm.yaml"
DATASET = "1006022"
PORTAL = "https://datos.comunidad.madrid"
API = f"{PORTAL}/api/3/action/package_show"
YEARS = 5  # the last five published years

# Concept pairs of the file (budget in thousands of euros, area in m²), as the file writes them
KINDS: dict[str, tuple[str, str]] = {
    "viviendas_en_bloque": (
        "Presupuesto de ejecución material de dirección de obra nueva para edificios "
        "destinados a viviendas en bloque",
        "Superficie a construir en edificios de viviendas en bloque con visado de dirección de "
        "obra nueva",
    ),
    "unifamiliar_adosada": (
        "Presupuesto de ejecución material de dirección de obra nueva para edificios "
        "destinados a vivienda unifamiliar adosada",
        "Superficie a construir en edificios de viviendas unifamiliares adosadas con visado de "
        "dirección de obra nueva",
    ),
    "unifamiliar_aislada": (
        "Presupuesto de ejecución material de dirección de obra nueva para edificios "
        "destinados a vivienda unifamiliar aislada",
        "Superficie a construir en edificios de viviendas unifamiliares aisladas con visado de "
        "dirección de obra nueva",
    ),
}
TOTAL_PERMITS_CONCEPT = "Total visados de dirección de obra nueva para edificios"
HEADER = """\
# D-248: presupuesto de ejecución material (PEM) por m² de los visados de obra nueva de
# vivienda, recalculado del fichero oficial por scripts/pem_visados_cm.py. No editar a mano:
# volver a lanzar el script. Es un PEM declarado en el visado, no el coste total de la obra:
# la viabilidad lo multiplica por un coeficiente editable (gastos generales, beneficio
# industrial, honorarios, licencias e impuestos) y avisa de que suele declararse a la baja.
"""


@polite_retry
def download(url: str) -> bytes:
    with make_client(timeout=120.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


def dataset_metadata() -> dict[str, Any]:
    with make_client() as client:
        body, _ = get_json(client, API, params={"id": DATASET})
    result = body["result"]
    extras = {e["key"]: e["value"] for e in result.get("extras", [])}
    csv_resource = next(r for r in result["resources"] if r["format"].upper() == "CSV")
    return {
        "title": result["title"],
        "metadata_modified": result["metadata_modified"][:10],
        "updated": extras.get("Fecha Actualización"),
        "source": extras.get("Fuente"),
        "csv_url": csv_resource["url"],
    }


def number(text: str) -> float:
    return float(text.replace(".", "").replace(",", ".")) if "," in text else float(text)


def pem_by_year(rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Each of the last YEARS years with both concepts of every kind: budget, area and the
    budget per m², rounded to the euro. A missing concept stops the script (never a 0)."""
    values = {(r["Año"], r["Concepto"]): r for r in rows}
    years = sorted({r["Año"] for r in rows})[-YEARS:]
    series: list[dict[str, Any]] = []
    for year in years:
        entry: dict[str, Any] = {"year": int(year)}
        for kind, (budget_concept, area_concept) in KINDS.items():
            budget, area = values.get((year, budget_concept)), values.get((year, area_concept))
            if budget is None or area is None:
                msg = f"{year}: the file has no {kind} budget or area"
                raise ValueError(msg)
            if budget["Unidad"] != "Miles euros" or area["Unidad"] != "m2":
                msg = f"{year} {kind}: unexpected units {budget['Unidad']} / {area['Unidad']}"
                raise ValueError(msg)
            budget_keur, area_m2 = number(budget["Valor"]), number(area["Valor"])
            entry[kind] = {
                "pem_miles_eur": round(budget_keur),
                "superficie_m2": round(area_m2),
                "pem_eur_m2": round(budget_keur * 1000 / area_m2),
                "provisional": bool(budget["Estado dato"] or area["Estado dato"]),
            }
        series.append(entry)
    return series


def build(content: bytes, meta: dict[str, Any], consulted: str) -> dict[str, Any]:
    rows = list(csv.DictReader(io.StringIO(content.decode("utf-8-sig")), delimiter=";"))
    if {r["Territorio"] for r in rows} != {""}:
        raise ValueError("the file now has territories: read it again by hand")
    series = pem_by_year(rows)
    latest = series[-1]
    year = str(latest["year"])
    permits = next(r for r in rows if r["Año"] == year and r["Concepto"] == TOTAL_PERMITS_CONCEPT)
    return {
        "title": meta["title"],
        "publisher": "Comunidad de Madrid (portal de datos abiertos)",
        "source": meta["source"],
        "license": "CC BY 4.0",
        "portal_id": DATASET,
        "url": f"{PORTAL}/dataset/{DATASET}",
        "csv_url": meta["csv_url"],
        "updated": meta["updated"],
        "metadata_modified": meta["metadata_modified"],
        "consulted": consulted,
        "sha256": hashlib.sha256(content).hexdigest(),
        "territory": (
            "Comunidad de Madrid. El fichero no trae columna de territorio y su ficha dice "
            "«Ámbito: Toda España», pero el portal es el de la Comunidad y la escala es la "
            f"de la región: {permits['Valor']} visados de obra nueva en {year}, cuando España "
            "suma decenas de miles al año"
        ),
        "method": (
            "PEM por m² = presupuesto de ejecución material de dirección de obra nueva "
            "(miles de euros × 1.000) / superficie a construir (m²), por año y tipo de "
            "edificio. Es la superficie construida total del edificio que declara el visado."
        ),
        "default": {"kind": "viviendas_en_bloque", "year": latest["year"]},
        "series": series,
    }


def main() -> int:
    meta = dataset_metadata()
    if "--csv" in sys.argv:
        content = Path(sys.argv[sys.argv.index("--csv") + 1]).read_bytes()
    else:
        content = download(meta["csv_url"])
    table = build(content, meta, datetime.now(UTC).date().isoformat())
    body = yaml.safe_dump(table, allow_unicode=True, sort_keys=False, width=100)
    TARGET.write_text(HEADER + body)
    latest = table["series"][-1]
    print(
        f"wrote {TARGET.relative_to(ROOT)}: {latest['year']} viviendas en bloque "
        f"{latest['viviendas_en_bloque']['pem_eur_m2']} €/m²"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
