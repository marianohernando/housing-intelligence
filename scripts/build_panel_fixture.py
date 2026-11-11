"""Build the district-panel fixture from Bronze (CC BY 4.0, Ayuntamiento de Madrid).

Keeps the household indicators the pipeline reads for the districts in the admin_sample fixture
(01 Centro, 05 Chamartín, 06 Tetuán), at district and barrio level and for the city row, plus
one other indicator of Centro, so the tests see what the pipeline must leave out. Source lines
are copied unchanged.
Usage: uv run python scripts/build_panel_fixture.py [path/to/panelcsv.csv]
"""

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATASET_ID = "ayto_panel_indicadores_distritos_barrios"
BRONZE = REPO / "data" / "bronze" / "datasets" / DATASET_ID
OUT = REPO / "data" / "fixtures" / "golden" / "panel_sample" / f"{DATASET_ID}.csv"
DISTRICTS = {"1", "5", "6", ""}  # "" is the city row
INDICATORS = {"Total hogares", "Tamaño medio del hogar"}
LEFT_OUT = "Número habitantes"


def _latest_bronze() -> Path:
    files = sorted(BRONZE.glob("*/*.csv"), key=lambda p: p.stat().st_mtime)
    return files[-1]


def _keep(row: dict[str, str]) -> bool:
    district, indicator = row["cod_distrito"].strip(), row["indicador_completo"]
    if indicator in INDICATORS:
        return district in DISTRICTS
    return indicator == LEFT_OUT and district == "1" and not row["cod_barrio"].strip()


def main(source: Path) -> None:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    rows = csv.DictReader(lines, delimiter=";")
    out = [lines[0], *(line for line, row in zip(lines[1:], rows, strict=True) if _keep(row))]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8-sig")
    print(f"{OUT.relative_to(REPO)}: {len(out) - 1} rows from {source.name}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else _latest_bronze())
