"""Readable place names from the uppercase official spelling ("ROZAS DE MADRID, LAS")."""

LOWER_PARTICLES = frozenset({"de", "del", "la", "las", "los", "el", "y", "e", "en"})


def display_name(official: str) -> str:
    """'ROZAS DE MADRID, LAS' -> 'Las Rozas de Madrid'. Accents missing in the source stay so."""
    name = " ".join(official.split())
    if not name.isupper():  # already written in mixed case (e.g. Madrid district names)
        return name
    if ", " in name:
        base, article = name.rsplit(", ", 1)
        if article.lower() in {"el", "la", "los", "las"}:
            name = f"{article} {base}"
    words = name.lower().split(" ")
    return " ".join(
        word if i and word in LOWER_PARTICLES else "-".join(p.capitalize() for p in word.split("-"))
        for i, word in enumerate(words)
    )
