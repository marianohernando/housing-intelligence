"""Build the Agencia Tributaria rent-table fixtures from Bronze (D-228; reuse with citation).

Keeps the page's year, the header row and a few real rows: the totals and another province
(out of scope), the region and Madrid in the municipio table, and three of the sample's five
postcodes in the postcode table (the other two exercise the fallback to Madrid's factor).
Usage: uv run python scripts/build_aeat_fixtures.py
"""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BRONZE = REPO / "data" / "bronze" / "datasets"
OUT = REPO / "data" / "fixtures" / "golden" / "aeat_sample"
KEEP = {
    "aeat_alquiler_nuevos_contratos_municipios": (
        "Total",
        "Almería-04013",
        "Madrid, Comunidad de",
        "Madrid",
        "Madrid-28079",
    ),
    "aeat_alquiler_nuevos_contratos_codigo_postal": (
        "Madrid, Comunidad de",
        "Madrid-28079",
        "28013-Centro",
        "28029-Tetuán-Valdeacederas-Barrio Del Pilar",
        "28036-Nueva España",
    ),
}
_ROW = re.compile(r"<tr\b.*?</tr>", re.S)
_TAGS = re.compile(r"<[^>]+>")


def _label(row: str) -> str:
    cells = re.findall(r"<t[hd]\b.*?</t[hd]>", row, re.S)
    return " ".join(_TAGS.sub("", cells[0]).split()) if cells else ""


def build(dataset_id: str, labels: tuple[str, ...]) -> Path:
    source = sorted((BRONZE / dataset_id).glob("*/*.html"), key=lambda p: p.stat().st_mtime)[-1]
    html = source.read_text(encoding="utf-8")
    year = re.search(r"Ejercicio\s+\d{4}", html)
    assert year is not None  # noqa: S101 - the page always names its year
    rows = _ROW.findall(html)
    header = next(r for r in rows if "Localizaci" in _label(r))
    kept = [r for r in rows if _label(r) in labels]
    body = "\n".join([header, *kept])
    page = (
        "<!-- FIXTURE: real rows of the Agencia Tributaria table (scripts/build_aeat_fixtures.py)"
        " -->\n"
        f'<html><body><h1>{year.group(0)}</h1><table id="table01">\n{body}\n</table></body>'
        "</html>\n"
    )
    path = OUT / f"{dataset_id}.html"
    path.write_text(page, encoding="utf-8")
    return path


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for dataset_id, labels in KEEP.items():
        print("wrote", build(dataset_id, labels).relative_to(REPO))


if __name__ == "__main__":
    main()
