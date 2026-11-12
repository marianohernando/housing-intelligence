"""Who lives where something is missing, and where to invest first (D-229).

Each row of the list of what is missing divides its supply by a target population (children of
0 to 4 for the escuelas infantiles, people of 65 or more for the centros de mayores, …). The
people affected by a FALTA are that population in the zone, the same denominator its indicator
uses: nothing is estimated. Zones in FALTA are ranked by those people, with the probability
that a shortfall like theirs is chance (the test of D-213, as a number).
"""

import math
from collections.abc import Iterable, Mapping
from typing import Any, NamedTuple

from scipy.stats import chi2

from hi_contracts.catalog.enums import GapRowKey
from hi_domain.gaps import es_number


class RowPeople(NamedTuple):
    people: str  # the row's target population, plural («niños de 0 a 4 años»)
    missing: str  # what a FALTA lacks («faltan escuelas infantiles»)
    lack: str  # the noun after «una falta clara de» («escuelas infantiles»)


ROW_PEOPLE: dict[GapRowKey, RowPeople] = {
    GapRowKey.ESCUELA_INFANTIL: RowPeople(
        "niños de 0 a 4 años", "faltan escuelas infantiles", "escuelas infantiles"
    ),
    GapRowKey.COLEGIO: RowPeople("niños de 5 a 14 años", "faltan colegios", "colegios"),
    GapRowKey.CENTRO_SALUD: RowPeople("personas", "faltan centros de salud", "centros de salud"),
    GapRowKey.MAYORES: RowPeople(
        "personas de 65 años o más", "faltan centros de mayores", "centros de mayores"
    ),
    GapRowKey.FARMACIA: RowPeople("personas", "faltan farmacias", "farmacias"),
    GapRowKey.VIVIENDA: RowPeople(
        "hogares de 4 o más personas", "falta vivienda para familias", "vivienda para familias"
    ),
}

# The 2SFCA features store their denominator per `per` people (D-217: the Poisson test counts
# facility-equivalents over population units); the per-population methods store people.
_PER_UNIT_METHODS = frozenset({"two_step_fca"})


def people_scale(formula: Mapping[str, Any], level: str) -> float:
    """People per unit of the stored denominator at this level (a level may change method)."""
    override = (formula.get("levels") or {}).get(level) or {}
    method = override.get("method", formula.get("method"))
    return float(formula.get("per", 1)) if method in _PER_UNIT_METHODS else 1.0


def people_in(
    counts: Mapping[str, float] | None, formula: Mapping[str, Any], level: str
) -> int | None:
    """The row's target population in a zone, from the counts its feature keeps (D-213 §4);
    None without counts (unknown, never 0)."""
    if not counts:
        return None
    return round(float(counts["denominator"]) * people_scale(formula, level))


def shortfall_p_value(observed: float, expected: float) -> float:
    """One-sided exact Poisson probability that a zone at the reference rate has this little
    or less. It is below 0,025 exactly when the Garwood upper bound at 95 % (D-213) is below
    the expected count, i.e. when the shortfall is significant."""
    return float(chi2.sf(2 * expected, 2 * (observed + 1)))


def shown_p_value(p_value: float, digits: int = 3) -> float:
    """Rounded down to `digits` significant figures, so a significant p (< 0,025) is never
    shown as 0,025."""
    if p_value <= 0:
        return 0.0
    scale = 10 ** (digits - 1 - math.floor(math.log10(p_value)))
    return math.floor(p_value * scale) / scale


def share_of(people: int, total: int) -> float:
    """Share of the region's target population, at most 1; 0 when the total is unknown."""
    return min(1.0, people / total) if total > 0 else 0.0


def chance_text(p_value: float) -> str:
    """How often chance would give such a shortfall, in words (FALTA always has p < 0,025)."""
    if p_value < 0.001:
        return "menos de 1 entre 1.000"
    if p_value < 0.01:
        return "menos de 1 entre 100"
    return "menos de 1 entre 40"


class ImpactZone(NamedTuple):
    code: str
    name: str
    people: int
    ratio: float  # oriented: the zone's (or its group's) supply over the reference
    p_value: float | None  # None: the row keeps no counts and the ratio alone decided
    grouped: bool  # compared together with its nearest neighbours (D-217)


def rank(zones: Iterable[ImpactZone]) -> list[ImpactZone]:
    """Where to invest first: most people affected first, then by name."""
    return sorted(zones, key=lambda z: (-z.people, z.name, z.code))


def row_summary(row: GapRowKey, people: int, total: int, zones: int) -> str:
    """«En la Comunidad de Madrid, 23.456 niños de 0 a 4 años (el 9,0 %) viven en 3 zonas
    donde faltan escuelas infantiles»"""
    words = ROW_PEOPLE[row]
    if zones == 0:
        return f"Ninguna zona de la Comunidad de Madrid tiene una falta clara de {words.lack}"
    share = f" (el {es_number(100 * share_of(people, total), 1)} %)" if total > 0 else ""
    where = "1 zona donde" if zones == 1 else f"{zones} zonas donde"
    return (
        f"En la Comunidad de Madrid, {es_number(people, 0)} {words.people}{share} "
        f"viven en {where} {words.missing}"
    )


def zone_sentence(row: GapRowKey, zone: ImpactZone) -> str:
    """«Viven aquí 9.876 niños de 0 a 4 años. Tienen 62 por cada 100 que tienen los
    municipios parecidos, y una diferencia así sale por azar menos de 1 entre 1.000 veces»"""
    who = f"Viven aquí {es_number(zone.people, 0)} {ROW_PEOPLE[row].people}."
    have = "Junto con sus vecinos tienen" if zone.grouped else "Tienen"
    compared = (
        f"{who} {have} {round(100 * zone.ratio)} por cada 100 que tienen los municipios parecidos"
    )
    if zone.p_value is None:
        return compared
    return f"{compared}, y una diferencia así sale por azar {chance_text(zone.p_value)} veces"
