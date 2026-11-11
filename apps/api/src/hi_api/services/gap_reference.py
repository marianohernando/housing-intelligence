"""What each zone is compared with in the list of what is missing (D-213).

The reference is the rate of the other municipios of the zone's type (rural or urban, Ley
45/2007) in the Comunidad de Madrid: the sum of their counts over the sum of their populations,
from the counts each feature row keeps. The zone's own municipio is left out (Madrid is half of
the urban population: it must not be compared with itself). A district or section takes the
type of its municipio and leaves the whole municipio out. Without counts, or with no case left
in the type, the zone is compared with the whole region. Parameterised SQL only.
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, NamedTuple

from sqlalchemy import Connection, text

from hi_domain.gaps import (
    REGION_TEXT,
    TYPE_TEXT,
    TerritoryType,
    min_expected,
    significant_shortfall,
    territory_type,
)

# Population that sets the type of a municipio (with its area from the canonical geography).
TYPE_POPULATION_FEATURE = "poblacion_total"

_TYPES = text(
    """
    SELECT v.territory_code, v.value, u.area_m2 / 1e6 AS area_km2, v.inputs,
           g.dataset_id AS geo_dataset, g.version_label AS geo_version
      FROM feature_value v
      JOIN geo_admin_unit u ON u.admin_unit_id = v.admin_unit_id
      JOIN dataset_version g ON g.id = u.dataset_version_id
     WHERE v.feature_id = :feature_id AND v.territory_level = 'municipio'
       AND v.value IS NOT NULL
    """
)
_COUNTS = text(
    """
    SELECT feature_id, territory_code, inputs->'counts' AS counts
      FROM feature_value
     WHERE feature_id = ANY(:features) AND territory_level = 'municipio'
       AND inputs ? 'counts'
    """
)


@dataclass(frozen=True)
class Reference:
    value: float
    label: str
    phrase: str
    regional: float | None  # whole region, for context; None when the reference is the region
    rate: float | None  # numerator per unit of denominator, for the expected count


@dataclass
class References:
    """Municipio types and, per feature, the counts summed by type."""

    types: dict[str, TerritoryType] = field(default_factory=dict[str, TerritoryType])
    sums: dict[str, dict[TerritoryType, list[float]]] = field(
        default_factory=dict[str, dict[TerritoryType, list[float]]]
    )
    own: dict[str, dict[str, tuple[float, float]]] = field(
        default_factory=dict[str, dict[str, tuple[float, float]]]
    )  # feature -> municipio -> its own counts, left out of its reference
    versions: dict[str, str] = field(default_factory=dict[str, str])
    used: bool = False  # some zone was compared with its type: cite population and geography

    def zone_type(self, code: str) -> TerritoryType | None:
        return self.types.get(code[:5])

    def for_zone(
        self, feature_id: str, code: str, region_row: dict[str, Any] | None
    ) -> Reference | None:
        """The zone's reference; None when the region itself has no value."""
        if region_row is None or region_row["value"] is None:
            return None
        regional = float(region_row["value"])
        counts = (region_row.get("inputs") or {}).get("counts")
        kind = self.zone_type(code)
        others = self._others(feature_id, code, kind)
        if not counts or not counts["numerator"] or kind is None or others is None:
            # no counts, no type, or no case left in the type: compare with the whole region
            return Reference(regional, REGION_TEXT.label, REGION_TEXT.phrase, None, _rate(counts))
        self.used = True
        per = regional / (counts["numerator"] / counts["denominator"])
        rate = others[0] / others[1]
        label, phrase = TYPE_TEXT[kind]
        return Reference(per * rate, label, phrase, regional, rate)

    def _others(
        self, feature_id: str, code: str, kind: TerritoryType | None
    ) -> tuple[float, float] | None:
        """Counts of the type without the zone's own municipio; None if nothing is left."""
        typed = self.sums.get(feature_id, {}).get(kind) if kind else None
        if not typed:
            return None
        own_num, own_den = self.own.get(feature_id, {}).get(code[:5], (0.0, 0.0))
        num, den = typed[0] - own_num, typed[1] - own_den
        return (num, den) if num > 0 and den > 0 else None


def _rate(counts: dict[str, float] | None) -> float | None:
    if not counts or not counts["denominator"]:
        return None
    return counts["numerator"] / counts["denominator"]


def load_references(conn: Connection, features: list[str]) -> References:
    refs = References()
    for row in conn.execute(_TYPES, {"feature_id": TYPE_POPULATION_FEATURE}).mappings():
        if row["area_km2"] and row["area_km2"] > 0:
            refs.types[row["territory_code"]] = territory_type(row["value"], row["area_km2"])
            refs.versions.update((row["inputs"] or {}).get("dataset_versions", {}))
            refs.versions[row["geo_dataset"]] = row["geo_version"]
    sums: dict[str, dict[TerritoryType, list[float]]] = defaultdict(dict)
    for row in conn.execute(_COUNTS, {"features": features}).mappings():
        kind = refs.types.get(row["territory_code"])
        if kind is None:
            continue
        num, den = float(row["counts"]["numerator"]), float(row["counts"]["denominator"])
        total = sums[row["feature_id"]].setdefault(kind, [0.0, 0.0])
        total[0] += num
        total[1] += den
        refs.own.setdefault(row["feature_id"], {})[row["territory_code"]] = (num, den)
    refs.sums = dict(sums)
    return refs


class Assessment(NamedTuple):
    significant: bool | None  # shortfall test; None when it cannot be run (no counts)
    reliable: bool  # False: too small to show a shortfall; True also when not testable


def assess(row: dict[str, Any], reference: Reference, direction: str) -> Assessment:
    """Significance of a shortfall and reliability of a count-based row (D-213)."""
    counts = (row.get("inputs") or {}).get("counts")
    if direction != "higher_is_better" or not counts or reference.rate is None:
        return Assessment(None, True)
    expected = counts["denominator"] * reference.rate
    floor = min_expected()
    reliable = floor is None or expected >= floor
    return Assessment(significant_shortfall(counts["numerator"], expected), reliable)
