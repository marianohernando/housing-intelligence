"""What each zone is compared with in the list of what is missing (D-213).

The reference is the rate of the other municipios of the zone's type (rural or urban, Ley
45/2007) in the Comunidad de Madrid: the sum of their counts over the sum of their populations,
from the counts each feature row keeps. The zone's own municipio is left out (Madrid is half of
the urban population: it must not be compared with itself). A district or section takes the
type of its municipio and leaves the whole municipio out. Without counts, or with no case left
in the type, the zone is compared with the whole region. Parameterised SQL only.
"""

import math
import os
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, NamedTuple

from sqlalchemy import Connection, text

from hi_contracts.public import ComparisonGroup, GapStatus
from hi_domain.gaps import (
    REGION_TEXT,
    TYPE_TEXT,
    Pool,
    TerritoryType,
    classify,
    min_expected,
    pool_with_neighbours,
    pooled_status,
    significant_shortfall,
    territory_type,
)
from hi_domain.geo.names import display_name

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


# How far a small municipio looks for same-type neighbours to be compared with (D-217).
POOL_RADIUS_M = float(os.environ.get("GAP_POOL_RADIUS_M", "15000"))
# Where each municipio is, to find its nearest same-type neighbours (gap-0.3, D-217).
_MUNICIPIOS = text(
    """
    SELECT code_official, name,
           ST_X(ST_PointOnSurface(geom_25830)) AS x, ST_Y(ST_PointOnSurface(geom_25830)) AS y
      FROM geo_admin_unit
     WHERE level = 'municipio'
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
    places: dict[str, tuple[str, float, float]] = field(
        default_factory=dict[str, tuple[str, float, float]]
    )  # municipio -> (display name, x, y)

    def neighbours(self, code: str) -> list[str]:
        """Same-type municipios within POOL_RADIUS_M, nearest first (between interior points)."""
        kind, here = self.types.get(code), self.places.get(code)
        if kind is None or here is None:
            return []
        others = [
            (math.dist(here[1:], where[1:]), other)
            for other, where in self.places.items()
            if other != code and self.types.get(other) is kind
        ]
        return [other for metres, other in sorted(others) if metres <= POOL_RADIUS_M]

    def pool(self, feature_id: str, code: str) -> Pool | None:
        """A small municipio with its nearest same-type neighbours (D-217); None elsewhere."""
        kind, floor = self.types.get(code), min_expected()
        own = self.own.get(feature_id, {})
        typed = self.sums.get(feature_id, {}).get(kind) if kind else None
        if len(code) != 5 or code not in own or not typed or floor is None:
            return None

        def rate_without(members: set[str]) -> float | None:
            num = typed[0] - sum(own[m][0] for m in members)
            den = typed[1] - sum(own[m][1] for m in members)
            return num / den if num > 0 and den > 0 else None

        return pool_with_neighbours(code, own, self.neighbours(code), rate_without, floor)

    def group(self, pool: Pool) -> ComparisonGroup:
        names = [self.places[c][0] if c in self.places else c for c in pool.codes]
        return ComparisonGroup(codes=pool.codes, names=names, ratio_to_reference=pool.ratio)

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
    for row in conn.execute(_MUNICIPIOS).mappings():
        refs.places[str(row["code_official"])] = (
            display_name(str(row["name"])),
            float(row["x"]),
            float(row["y"]),
        )
    return refs


class Assessment(NamedTuple):
    significant: bool | None  # shortfall test; None when it cannot be run (no counts)
    reliable: bool  # False: too small to show a shortfall; True also when not testable


def assess(
    row: dict[str, Any], reference: Reference, direction: str, denominator_is_count: bool = False
) -> Assessment:
    """Significance of a shortfall and reliability of a count-based row (D-213). When the
    denominator is itself a count (households, not a population per `per`), it must reach the
    same floor: below it the count is compatible with none and the ratio compares nothing."""
    counts = (row.get("inputs") or {}).get("counts")
    if direction != "higher_is_better" or not counts or reference.rate is None:
        return Assessment(None, True)
    expected = counts["denominator"] * reference.rate
    floor = min_expected()
    reliable = floor is None or (
        expected >= floor and (not denominator_is_count or counts["denominator"] >= floor)
    )
    return Assessment(significant_shortfall(counts["numerator"], expected), reliable)


class Verdict(NamedTuple):
    status: GapStatus
    reliable: bool
    group: ComparisonGroup | None


def judge(
    ratio: float | None,
    judged: Assessment,
    references: References,
    feature_id: str,
    code: str,
) -> Verdict:
    """The zone's status; a municipio too small alone takes its group's (gap-0.3, D-217)."""
    if ratio is None or judged.reliable:
        return Verdict(classify(ratio, significant=judged.significant), judged.reliable, None)
    pool = references.pool(feature_id, code)
    if pool is None or len(pool.codes) < 2:
        return Verdict(classify(ratio, significant=judged.significant), False, None)
    return Verdict(pooled_status(pool), True, references.group(pool))


def group_sentence(group: ComparisonGroup) -> str:
    """«demasiado pequeño para compararlo solo: junto con 4 municipios vecinos (A, B, C y D),
    tiene el 112 % de lo esperado»"""
    others = group.names[1:]
    listed = others[0] if len(others) == 1 else ", ".join(others[:-1]) + " y " + others[-1]
    plural = "municipio vecino" if len(others) == 1 else "municipios vecinos"
    share = round(100 * group.ratio_to_reference)
    return (
        f"demasiado pequeño para compararlo solo: junto con {len(others)} {plural} del mismo "
        f"tipo ({listed}), tiene el {share} % de lo esperado"
    )
