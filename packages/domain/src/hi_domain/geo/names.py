"""Readable place names and the characters a published place name may carry."""

import re
import string
import unicodedata

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


def name_key(name: str) -> str:
    """How a person may type a place name: no case, accents, punctuation or extra spaces
    ('Fuencarral-El Pardo' and 'fuencarral el pardo' have the same key; ñ stays n)."""
    plain = "".join(
        c for c in unicodedata.normalize("NFKD", name.casefold()) if not unicodedata.combining(c)
    )
    return " ".join(re.sub(r"[^0-9a-z]+", " ", plain).split())


def match_rank(query: str, name: str) -> int | None:
    """How well a typed query matches a place name, best first: 0 the same name, 1 the name
    starts with it, 2 a word of the name starts with it, 3 it is inside the name; None if not."""
    typed, key = name_key(query), name_key(name)
    if not typed or typed not in key:
        return None
    if key == typed:
        return 0
    if key.startswith(typed):
        return 1
    return 2 if f" {typed}" in f" {key}" else 3
