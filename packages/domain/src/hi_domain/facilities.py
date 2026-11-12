"""Public or private, from the free text registers and directories publish (D-218).

Mutuas colaboradoras con la Seguridad Social count as private: they attend the work accidents
of their affiliated workers, not anyone with a public health card. Unknown text -> None.
"""

import unicodedata
from typing import Literal

Dependency = Literal["publica", "privada"]

_PRIVATE = ("privad", "mutua", "no gubernamental")
_PUBLIC = (
    "public",
    "salud de",
    "ingesa",
    "defensa",
    "diputacion",
    "municipio",
    "penitenciaria",
    "carlos iii",
)


def _fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text.casefold())
    return " ".join("".join(c for c in decomposed if not unicodedata.combining(c)).split())


def dependency(text: str | None) -> Dependency | None:
    """«Privado Benéfico (Iglesia)» -> privada; «Servicios o Institutos de Salud de las CC.AA»
    -> publica; «Mútuas Colaboradoras con La Seguridad Social» -> privada."""
    folded = _fold(text or "")
    if any(term in folded for term in _PRIVATE):
        return "privada"
    if any(term in folded for term in _PUBLIC):
        return "publica"
    return None
