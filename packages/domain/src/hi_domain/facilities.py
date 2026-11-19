"""Public or private, from the free text registers and directories publish (D-218).

Mutuas colaboradoras con la Seguridad Social count as private: they attend the work accidents
of their affiliated workers, not anyone with a public health card. Unknown text -> None.

D-239: a hospital is public when it belongs to the network of the Servicio Madrileño de Salud,
also when a private company runs it (PRIVATE_MANAGEMENT); private is the rest.
"""

import unicodedata
from collections.abc import Mapping
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


# D-239. Hospitals of the network of the Servicio Madrileño de Salud that a private company runs,
# by the code of the Catálogo Nacional de Hospitales (CODCNH) each place is matched to (D-218): the
# only official code a place carries. Both sources are pages of comunidad.madrid, consulted on
# 14 Nov 2026:
# - «Hospitales de la red del Servicio Madrileño de Salud» (updated 26 May 2026): the five are in
#   the public network, where patients of the public health system are sent;
# - «Control y seguimiento de centros y servicios de gestión indirecta» (updated 27 Oct 2026):
#   «Hospitales con concesión de gestión de servicio público, convenio o concierto singular».
# Left out on purpose: the Gómez Ulla (an agreement with another administration, Defensa: public
# management, and not in the CM register) and the PFI hospitals (only the building and the
# non-clinical services are in concession; the care is run by the SERMAS).
PRIVATE_MANAGEMENT_DIRECTORY = "ms_catalogo_nacional_hospitales"
PRIVATE_MANAGEMENT: Mapping[str, str] = {
    "280421": "Hospital Universitario Fundación Jiménez Díaz",  # concierto singular
    "281348": "Hospital Universitario Rey Juan Carlos",  # concesión (Móstoles)
    "281236": "Hospital Universitario Infanta Elena",  # concesión (Valdemoro)
    "281359": "Hospital Universitario General de Villalba",  # concesión (Collado Villalba)
    "281337": "Hospital Universitario de Torrejón",  # concesión (Torrejón de Ardoz)
}


def privately_managed(directory: object) -> bool:
    """A hospital of the public network run by a private company (D-239): the catalogue entry
    the place was matched to is in PRIVATE_MANAGEMENT. Without a match it is never guessed."""
    if not isinstance(directory, Mapping):
        return False
    entry: Mapping[str, object] = directory  # pyright: ignore[reportUnknownVariableType]
    return (
        entry.get("dataset_id") == PRIVATE_MANAGEMENT_DIRECTORY
        and str(entry.get("external_id")) in PRIVATE_MANAGEMENT
    )
