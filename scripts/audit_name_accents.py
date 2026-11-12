"""Names taken from the Ministry's catalogues that may have lost a tilde or an eñe (D-221).

Detection only: a word of a place name (CNH or primary care catalogue) is a candidate when the
official data already loaded writes the same word with a tilde or an eñe (names of municipalities,
districts and barrios; CM register names of schools and social centres; CRTM stop names), or when
it ends in «-cion»/«-sion», which Spanish always accents. A candidate is only corrected with an
official source per record in `data/catalog/corrections/places.yaml`, never from this list.
Prints Markdown. Usage:
    uv run python scripts/audit_name_accents.py > evidence/gate-01/<date>/<file>.md
"""

import re
import sys
import unicodedata
from collections import Counter, defaultdict

from sqlalchemy import create_engine, text

from hi_db.settings import DatabaseSettings

_WORD = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")
_MARKED = re.compile(r"[áéíóúüñ]")
_ALWAYS_ACCENTED = re.compile(r"[cs]ion$")
_VOCABULARY = text(
    """
    SELECT name FROM geo_admin_unit
    UNION ALL
    SELECT canonical_name FROM place_master WHERE category <> 'health'
    """
)
_DIRECTORY_NAMES = text(
    """
    SELECT official_entity_id AS id, canonical_name AS name, subcategory,
           attributes->'directory'->>'dataset_id' AS directory,
           attributes->'correction'->>'previous_name' AS previous_name,
           attributes->'correction'->>'url' AS url
      FROM place_master
     WHERE category = 'health' AND attributes ? 'directory'
     ORDER BY canonical_name, official_entity_id
    """
)


def fold(word: str) -> str:
    decomposed = unicodedata.normalize("NFD", word.lower())
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def accented_forms(names: list[str]) -> dict[str, Counter[str]]:
    """folded word -> how official names write it with a tilde or an eñe."""
    forms: dict[str, Counter[str]] = defaultdict(Counter)
    for name in names:
        for word in _WORD.findall(name):
            if _MARKED.search(word.lower()):
                forms[fold(word)][word.lower()] += 1
    return forms


def candidates(name: str, forms: dict[str, Counter[str]]) -> list[str]:
    found: list[str] = []
    for word in _WORD.findall(name):
        if _MARKED.search(word.lower()):
            continue
        written = forms.get(fold(word))
        if written:
            found.append(f"{word} → {written.most_common(1)[0][0]}")
        elif _ALWAYS_ACCENTED.search(word.lower()):
            found.append(f"{word} → -ción/-sión")
    return found


def main() -> int:
    engine = create_engine(DatabaseSettings().database_url)
    with engine.connect() as conn:
        forms = accented_forms([str(r[0]) for r in conn.execute(_VOCABULARY)])
        places = [dict(r) for r in conn.execute(_DIRECTORY_NAMES).mappings()]
    corrected = [p for p in places if p["previous_name"]]
    flagged = [(p, candidates(str(p["name"]), forms)) for p in places]
    flagged = [(p, words) for p, words in flagged if words]
    out = [
        f"Lugares de salud con nombre de un catálogo del Ministerio: {len(places)}. "
        f"Palabras con tilde o eñe en los datos oficiales cargados: {len(forms)}.",
        "",
        f"## Nombres corregidos con fuente oficial ({len(corrected)})",
        "",
        "| Registro | Publicado | Ahora | Fuente |",
        "|---|---|---|---|",
        *(f"| {p['id']} | {p['previous_name']} | {p['name']} | {p['url']} |" for p in corrected),
        "",
        f"## Candidatos sin corregir ({len(flagged)})",
        "",
        "| Registro | Nombre | Palabras |",
        "|---|---|---|",
        *(f"| {p['id']} | {p['name']} | {'; '.join(words)} |" for p, words in flagged),
    ]
    sys.stdout.write("\n".join(out) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
