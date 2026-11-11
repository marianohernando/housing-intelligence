"""Build the padrón fixture from Bronze (CC BY 4.0, Ayuntamiento de Madrid).

Keeps the districts present in the admin_sample fixture (01 Centro, 05 Chamartín, 06 Tetuán):
their first two census sections with every age, plus any row without a section. Source lines
are copied unchanged, so the fixture keeps the real encoding, quoting and padding.
Usage: uv run python scripts/build_padron_fixture.py [path/to/padron.csv]
"""

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATASET_ID = "ayto_padron_municipal"
BRONZE = REPO / "data" / "bronze" / "datasets" / DATASET_ID
OUT = REPO / "data" / "fixtures" / "golden" / "padron_sample" / f"{DATASET_ID}.csv"
DISTRICTS = {"1", "5", "6"}
SECTIONS_PER_DISTRICT = 2


def _latest_bronze() -> Path:
    files = sorted(BRONZE.glob("*/*.csv"), key=lambda p: p.stat().st_mtime)
    return files[-1]


def _kept_sections(rows: list[dict[str, str]]) -> set[tuple[str, str]]:
    sections: dict[str, set[int]] = {}
    for row in rows:
        district, section = row["COD_DISTRITO"].strip(), row["COD_SECCION"].strip()
        if district in DISTRICTS and section:
            sections.setdefault(district, set()).add(int(section))
    return {
        (district, str(section))
        for district, found in sections.items()
        for section in sorted(found)[:SECTIONS_PER_DISTRICT]
    }


def main(source: Path) -> None:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    rows = list(csv.DictReader(lines, delimiter=";"))
    kept = _kept_sections(rows)
    out = [lines[0]]
    for line, row in zip(lines[1:], rows, strict=True):
        district, section = row["COD_DISTRITO"].strip(), row["COD_SECCION"].strip()
        if district in DISTRICTS and (not section or (district, section) in kept):
            out.append(line)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8-sig")
    print(f"{OUT.relative_to(REPO)}: {len(out) - 1} rows from {source.name}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else _latest_bronze())
