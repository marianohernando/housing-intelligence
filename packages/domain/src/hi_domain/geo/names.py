"""Readable place names and the characters a published place name may carry."""

import re
import string

LOWER_PARTICLES = frozenset({"de", "del", "la", "las", "los", "el", "y", "e", "en"})
ARTICLES = ("El", "La", "Los", "Las")
# Statistical tables of the CM write the article after the name: "Álamo (El)".
_TRAILING_ARTICLE = re.compile(
    rf"^(?P<base>.+?) \((?P<article>{'|'.join(ARTICLES)})\)(?P<rest>.*)$"
)
NAME_CHARS = frozenset(string.ascii_letters + string.digits + "ÁÉÍÓÚÜÑáéíóúüñ" + " ,.'-—()")


def invalid_name_chars(name: str) -> list[str]:
    """Characters outside Spanish place-name spelling, such as the '/' or 'Ð' left by a lost Ñ."""
    return sorted({c for c in name if c not in NAME_CHARS})


def display_name(official: str) -> str:
    """'ROZAS DE MADRID, LAS' or 'Rozas de Madrid (Las)' -> 'Las Rozas de Madrid'.

    Mixed-case names keep their spelling; only the trailing article moves to the front.
    Accents missing in an uppercase source stay missing.
    """
    name = " ".join(official.split())
    if not name.isupper():
        match = _TRAILING_ARTICLE.match(name)
        return f"{match['article']} {match['base']}{match['rest']}" if match else name
    if ", " in name:
        base, article = name.rsplit(", ", 1)
        if article.lower() in {"el", "la", "los", "las"}:
            name = f"{article} {base}"
    words = name.lower().split(" ")
    return " ".join(
        word if i and word in LOWER_PARTICLES else "-".join(p.capitalize() for p in word.split("-"))
        for i, word in enumerate(words)
    )
