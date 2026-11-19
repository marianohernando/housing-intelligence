"""Build the padrón fixture from Bronze (CC BY 4.0, Ayuntamiento de Madrid).

Keeps the districts present in the admin_sample fixture (01 Centro, 05 Chamartín, 06 Tetuán):
their first two census sections with every age, plus any row without a section. Source lines
are copied unchanged, so the fixture keeps the real encoding, quoting and padding, but for one
thing (D-247): a barrio the admin sample does not have is renumbered, with its name, to a barrio
of the same district that it has (El Viso -> Nueva España, Bellas Vistas -> Castillejos,
Berruguete -> Almenara on 1 Oct 2026), so the padrón totals by barrio resolve in the sample
geography. The district totals do not change.
Usage: uv run python scripts/build_padron_fixture.py [path/to/padron.csv]
"""

import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATASET_ID = "ayto_padron_municipal"
BRONZE = REPO / "data" / "bronze" / "datasets" / DATASET_ID
OUT = REPO / "data" / "fixtures" / "golden" / "padron_sample" / f"{DATASET_ID}.csv"
ADMIN_BARRIOS = REPO / "data" / "fixtures" / "golden" / "admin_sample" / "barrios.csv"
NAME_WIDTH = 20  # the padrón pads its names to 20 characters
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


def _sample_barrios() -> dict[str, list[tuple[str, str]]]:
    """District number -> its barrios in the admin sample, as the padrón's COD_DIST_BARRIO
    («505»: district 5, barrio 5) and the name."""
    text = ADMIN_BARRIOS.read_text(encoding="latin-1")
    barrios: dict[str, list[tuple[str, str]]] = {}
    for row in csv.DictReader(text.splitlines(), delimiter=";"):
        code = row["barrio_codigo"].strip()  # «0796055»: municipio 0796, district 05, barrio 5
        district, digit = int(code[4:6]), int(code[6])
        name = row["barrio_nombre"].strip()
        barrios.setdefault(str(district), []).append((str(district * 100 + digit), name))
    return barrios


def _renumbering(rows: list[dict[str, str]]) -> dict[str, tuple[str, str, str]]:
    """Each barrio of the kept rows that the admin sample lacks -> one of the sample's in the
    same district that no kept row uses, in order: (COD_DIST_BARRIO, DESC_BARRIO, COD_BARRIO)."""
    sample = _sample_barrios()
    used = sorted({(r["COD_DISTRITO"].strip(), r["COD_DIST_BARRIO"].strip()) for r in rows})
    taken = {code for _, code in used}
    out: dict[str, tuple[str, str, str]] = {}
    for district, code in used:
        if not code or code in {c for c, _ in sample.get(district, [])}:
            continue
        free = [(c, n) for c, n in sample[district] if c not in taken]
        new_code, name = free[0]
        taken.add(new_code)
        out[code] = (new_code, name.upper().ljust(NAME_WIDTH), str(int(new_code) % 100))
    return out


def _renumbered(line: str, row: dict[str, str], moves: dict[str, tuple[str, str, str]]) -> str:
    code = row["COD_DIST_BARRIO"].strip()
    if code not in moves:
        return line
    new_code, new_name, new_digit = moves[code]
    old = f';{code};"{row["DESC_BARRIO"]}";{row["COD_BARRIO"]};'
    return line.replace(old, f';{new_code};"{new_name}";{new_digit};', 1)


def main(source: Path) -> None:
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    rows = list(csv.DictReader(lines, delimiter=";"))
    kept = _kept_sections(rows)
    chosen = [
        (line, row)
        for line, row in zip(lines[1:], rows, strict=True)
        if row["COD_DISTRITO"].strip() in DISTRICTS
        and (
            not row["COD_SECCION"].strip()
            or (row["COD_DISTRITO"].strip(), row["COD_SECCION"].strip()) in kept
        )
    ]
    moves = _renumbering([row for _, row in chosen])
    out = [lines[0], *(_renumbered(line, row, moves) for line, row in chosen)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(out) + "\n", encoding="utf-8-sig")
    print(f"{OUT.relative_to(REPO)}: {len(out) - 1} rows from {source.name}")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else _latest_bronze())
