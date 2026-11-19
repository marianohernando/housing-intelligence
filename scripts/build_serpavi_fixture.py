"""Build the small SERPAVI fixture (D-242) from the real workbook (Ministerio de Vivienda).

Usage: uv run python scripts/build_serpavi_fixture.py [workbook.xlsx]
Without an argument it reads the workbook in Bronze. Keeps the territories of the admin sample
(Madrid's sections of Sol, Palacio, Chamartín and Tetuán, La Acebeda and Ajalvir), their
districts and municipios, and the first territory of another province on each sheet; and only
the columns of 2023 and 2024, so the tests see a year left out by `period_min`.
"""

import sys
from pathlib import Path
from typing import Any

import pyogrio
from openpyxl import Workbook, load_workbook

from hi_contracts.catalog.pipeline import SerpaviRentPipeline
from hi_ingestion.catalog.loader import load_catalog
from hi_ingestion.pipelines.serpavi.normalize import in_province, value_columns

REPO = Path(__file__).resolve().parents[1]
DATASET = "mivau_serpavi_alquiler"
OUT = REPO / "data" / "fixtures" / "golden" / "serpavi_sample" / f"{DATASET}.xlsx"
SECTIONS = REPO / "data" / "fixtures" / "golden" / "admin_sample" / "sections.gpkg"
YEARS = (2023, 2024)


def sample_codes() -> dict[str, set[str]]:
    frame = pyogrio.read_dataframe(SECTIONS)
    sections = {"28" + str(g).replace("-", "") for g in frame["CDGSECCION"]}
    return {
        "seccion_censal": sections,
        "distrito": {s[:7] for s in sections},
        "municipio": {s[:5] for s in sections},
    }


def main() -> None:
    spec = load_catalog().pipelines[DATASET]
    if not isinstance(spec, SerpaviRentPipeline):
        msg = f"{DATASET} is not a serpavi_rent pipeline"
        raise TypeError(msg)
    source = (
        Path(sys.argv[1])
        if len(sys.argv) > 1
        else next((REPO / "data" / "bronze" / "datasets" / DATASET).glob("*/*.xlsx"))
    )
    codes = sample_codes()
    book = load_workbook(source, read_only=True, data_only=True)
    out = Workbook()
    out.remove(out.active)  # pyright: ignore[reportArgumentType]
    for level, sheet in spec.sheets.items():
        rows = book[sheet.sheet].iter_rows(values_only=True)
        header = [str(c) for c in next(rows)]
        names = [sheet.name_column] if sheet.name_column else []
        lead = [spec.province_column, sheet.code_column, *names]
        columns = lead + [c for y in YEARS for c in value_columns(spec, y)]
        index = [header.index(c) for c in columns]
        target = out.create_sheet(sheet.sheet)
        target.append(columns)
        other_province = False
        for row in rows:
            cells: list[Any] = [row[i] for i in index]
            code = str(cells[1])
            if in_province(cells[0], spec.province_code) and code in codes[level]:
                target.append(cells)
            elif not in_province(cells[0], spec.province_code) and not other_province:
                target.append(cells)
                other_province = True
    book.close()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    out.save(OUT)
    print(f"{OUT.relative_to(REPO)}: {[(s.title, s.max_row - 1) for s in out.worksheets]}")


if __name__ == "__main__":
    main()
