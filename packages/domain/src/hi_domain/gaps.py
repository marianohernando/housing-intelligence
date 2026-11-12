"""Per-zone list of what is missing (GAP-001): a value against a regional reference (D-213).

The ratio is oriented so that above 1 always means better than the reference. The reference is
the rate of the municipios of the same type in the Comunidad de Madrid (rural or urban, by the
legal definition of Ley 45/2007), because the rate of several rows depends on the type of
territory (e.g. a village has its own consultorio). FALTA needs a material shortfall (below
the four-fifths cut-off) that is also statistically significant for the size of the zone
(exact Poisson interval of its count). An unknown value is never classified.
"""

from collections.abc import Callable, Mapping, Sequence
from enum import StrEnum
from typing import Literal, NamedTuple

from scipy.stats import chi2

from hi_contracts.public import GapMethod, GapStatus

GAP_METHOD = GapMethod(
    version="gap-0.3",
    reference=(
        "Municipios del mismo tipo de la Comunidad de Madrid (rural o urbano, Ley 45/2007): "
        "la oferta al alcance a pie de su población (2SFCA, 15 min) dividida por su población. "
        "Un municipio demasiado pequeño se compara junto con sus vecinos más cercanos del mismo "
        "tipo (D-217)"
    ),
    falta_below=0.8,
    cubierto_from=1.0,
    confidence_level=0.95,
)
Direction = Literal["higher_is_better", "lower_is_better"]

# Ley 45/2007, de desarrollo sostenible del medio rural, art. 3.a: «medio rural», municipios
# con menos de 30.000 habitantes y menos de 100 habitantes por km2.
RURAL_MAX_POPULATION = 30_000
RURAL_MAX_DENSITY = 100.0


class TerritoryType(StrEnum):
    RURAL = "rural"
    URBANO = "urbano"


class ReferenceText(NamedTuple):
    label: str
    phrase: str


REGION_TEXT = ReferenceText("Comunidad de Madrid", "en el conjunto de la Comunidad de Madrid")
TYPE_TEXT = {  # the zone's own municipio is left out of its reference
    TerritoryType.RURAL: ReferenceText(
        "Otros municipios rurales de la Comunidad de Madrid",
        "en los demás municipios rurales de la Comunidad de Madrid",
    ),
    TerritoryType.URBANO: ReferenceText(
        "Otros municipios urbanos de la Comunidad de Madrid",
        "en los demás municipios urbanos de la Comunidad de Madrid",
    ),
}


class UnclassifiableError(ValueError):
    """The value exists but cannot be compared with the reference (e.g. reference 0)."""


def territory_type(population: float, area_km2: float) -> TerritoryType:
    if area_km2 <= 0:
        msg = f"area must be positive, got {area_km2}"
        raise ValueError(msg)
    rural = population < RURAL_MAX_POPULATION and population / area_km2 < RURAL_MAX_DENSITY
    return TerritoryType.RURAL if rural else TerritoryType.URBANO


def oriented_ratio(value: float, reference: float, direction: Direction) -> float:
    if reference <= 0:
        msg = f"reference must be positive, got {reference}"
        raise UnclassifiableError(msg)
    if direction == "higher_is_better":
        return value / reference
    if value <= 0:
        msg = "a lower-is-better value of 0 has no finite ratio"
        raise UnclassifiableError(msg)
    return reference / value


def poisson_upper(observed: float, level: float) -> float:
    """Exact (Garwood) upper bound of a Poisson count at a two-sided confidence level."""
    return float(chi2.ppf(1 - (1 - level) / 2, 2 * (observed + 1)) / 2)


def significant_shortfall(
    observed: float, expected: float, method: GapMethod = GAP_METHOD
) -> bool | None:
    """True if even the upper bound of the zone's count is below the expected count; None when
    the method does not test it."""
    if method.confidence_level is None:
        return None
    return poisson_upper(observed, method.confidence_level) < expected


def min_expected(method: GapMethod = GAP_METHOD) -> float | None:
    """Smallest expected count at which even a zone with none could be significantly short:
    the upper bound of a zero count (3,69 at 95 %). Below it the data cannot show a shortfall
    for that zone, whatever it has, so its status is not reliable (D-213)."""
    if method.confidence_level is None:
        return None
    return poisson_upper(0, method.confidence_level)


def classify(
    ratio: float | None, method: GapMethod = GAP_METHOD, significant: bool | None = None
) -> GapStatus:
    """`significant` is the shortfall test; None (no counts or not testable) lets the ratio
    decide alone, so a row without counts is never softened silently."""
    if ratio is None:
        return GapStatus.SIN_DATOS
    if ratio >= method.cubierto_from:
        return GapStatus.CUBIERTO
    if ratio < method.falta_below and significant is not False:
        return GapStatus.FALTA
    return GapStatus.JUSTO


def es_number(value: float, decimals: int) -> str:
    """Spanish formatting: 1.234,5"""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def explanation(
    value: float,
    reference: float,
    phrase: str,
    reference_phrase: str = REGION_TEXT.phrase,
    regional: float | None = None,
) -> str:
    numbers = [value, reference, *([regional] if regional is not None else [])]
    decimals = 2 if max(abs(n) for n in numbers) < 1 else 1
    shown, compared = es_number(value, decimals), es_number(reference, decimals)
    text = f"{shown} {phrase}; {reference_phrase}, {compared}"
    if regional is not None:
        text += f" (en toda la Comunidad, {es_number(regional, decimals)})"
    return text


class Pool(NamedTuple):
    """A small zone compared together with its nearest neighbours of the same type (D-217)."""

    codes: list[str]  # the zone first, then the neighbours in the order they were added
    observed: float
    expected: float

    @property
    def ratio(self) -> float:
        return self.observed / self.expected


def pool_with_neighbours(
    code: str,
    counts: Mapping[str, tuple[float, float]],
    neighbours: Sequence[str],
    rate_without: Callable[[set[str]], float | None],
    floor: float,
) -> Pool | None:
    """Add the nearest same-type zones until the group expects `floor` cases (D-217).

    Adaptive spatial filtering with a minimum expected count (Talbot et al., 2000): the group
    is the smallest one around the zone whose count can show a shortfall, with the same 3,69
    floor that marks a zone as too small (D-213). The reference rate always leaves out every
    member of the group (no self-inclusion). None when even all neighbours are not enough.
    """
    members = [code]
    while True:
        rate = rate_without(set(members))
        if rate is None:
            return None
        observed = sum(counts[m][0] for m in members)
        expected = sum(counts[m][1] for m in members) * rate
        if expected >= floor:
            return Pool(members, observed, expected)
        nxt = next((n for n in neighbours if n not in members and n in counts), None)
        if nxt is None:
            return None
        members.append(nxt)


def pooled_status(pool: Pool, method: GapMethod = GAP_METHOD) -> GapStatus:
    """The group's status: same cut-offs and the same Poisson test as a single zone."""
    return classify(pool.ratio, method, significant_shortfall(pool.observed, pool.expected, method))
