"""Per-zone list of what is missing (GAP-001): a value against the regional reference.

The ratio is oriented so that above 1 always means better than the region; the status comes
from the declared cut-offs of the method version. An unknown value is never classified.
"""

from typing import Literal

from hi_contracts.public import GapMethod, GapStatus

GAP_METHOD = GapMethod(
    version="gap-0.1",
    reference="Comunidad de Madrid: total de la región dividido por su población",
    falta_below=0.8,
    cubierto_from=1.0,
)
Direction = Literal["higher_is_better", "lower_is_better"]


class UnclassifiableError(ValueError):
    """The value exists but cannot be compared with the region (e.g. reference 0)."""


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


def classify(ratio: float | None, method: GapMethod = GAP_METHOD) -> GapStatus:
    if ratio is None:
        return GapStatus.SIN_DATOS
    if ratio < method.falta_below:
        return GapStatus.FALTA
    return GapStatus.CUBIERTO if ratio >= method.cubierto_from else GapStatus.JUSTO


def es_number(value: float, decimals: int) -> str:
    """Spanish formatting: 1.234,5"""
    text = f"{value:,.{decimals}f}"
    return text.replace(",", "_").replace(".", ",").replace("_", ".")


def explanation(value: float, reference: float, phrase: str) -> str:
    decimals = 2 if max(abs(value), abs(reference)) < 1 else 1
    return (
        f"{es_number(value, decimals)} {phrase}; "
        f"en el conjunto de la Comunidad de Madrid, {es_number(reference, decimals)}"
    )
