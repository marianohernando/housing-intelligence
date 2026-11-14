"""Rent where the CM publishes none (D-242): the Ministry's rent reference (SERPAVI), brought to
the level of the CM figure. Pure functions over observation frames.

The CM rent is a mean of the leases in force; SERPAVI publishes their median and quartiles per
m² from the same tax sources (IRPF and Catastro). Where both exist, CM mean / SERPAVI median is
measured zone by zone, and its median over those zones (the calibration) scales the SERPAVI
figures of every other zone, quartiles included. The lease-signed-in-the-year factor of D-228
is applied afterwards, as for the CM figure (hi_features.compute).
"""

import statistics
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import NullReason
from hi_features.methods import DimFilter, latest, null_row, ok_row, result_frame

MEDIAN, LOW, HIGH = "mediana", "p25", "p75"


@dataclass(frozen=True)
class ReferenceRent:
    """One zone's reference rent per m² for one kind of home, and the leases behind it."""

    typology: str
    median: float
    p25: float | None
    p75: float | None
    contracts: float | None
    sections: int | None = None  # pooled from this many census sections (barrios)


@dataclass(frozen=True)
class Calibration:
    """CM mean / reference median, measured where both exist (statistic over the zones)."""

    ratio: float
    zones: int
    low: float
    high: float
    statistic: str = "median"

    def as_inputs(self) -> dict[str, Any]:
        return {
            "ratio": round(self.ratio, 4),
            "zones": self.zones,
            "min": round(self.low, 4),
            "max": round(self.high, 4),
            "statistic": self.statistic,
        }


def _known(value: Any) -> float | None:
    return None if value is None or pd.isna(value) else float(value)


def references_by_typology(
    rent: pd.DataFrame, count: pd.DataFrame, typology_dim: str, statistic_dim: str
) -> tuple[dict[str, dict[str, ReferenceRent]], Any]:
    """Every zone's reference rents in the latest period, by typology (only those with a
    published median), and that period."""
    rent_now = latest(rent)
    period = rent_now["period_start"].max() if not rent_now.empty else None
    cells: dict[tuple[str, str], dict[str, float | None]] = {}
    for record in rent_now.to_dict("records"):
        dims: dict[str, str] = record["dims"]
        key = (str(record["territory_code"]), dims[typology_dim])
        cells.setdefault(key, {})[dims[statistic_dim]] = _known(record["value"])
    contracts: dict[tuple[str, str], float | None] = {}
    for record in count.to_dict("records"):
        if record["period_start"] == period:
            key = (str(record["territory_code"]), record["dims"][typology_dim])
            contracts[key] = _known(record["value"])
    out: dict[str, dict[str, ReferenceRent]] = {}
    for (code, typology), values in cells.items():
        median = values.get(MEDIAN)
        if median is None:
            continue
        out.setdefault(code, {})[typology] = ReferenceRent(
            typology, median, values.get(LOW), values.get(HIGH), contracts.get((code, typology))
        )
    return out, period


def pick(
    by_typology: Mapping[str, ReferenceRent], typologies: Sequence[str]
) -> ReferenceRent | None:
    """The first typology of `typologies` with a median: flats, else single-family homes."""
    return next((by_typology[t] for t in typologies if t in by_typology), None)


def _weighted(members: Sequence[ReferenceRent], attribute: str) -> float | None:
    pairs = [
        (getattr(m, attribute), m.contracts)
        for m in members
        if getattr(m, attribute) is not None and m.contracts
    ]
    weight = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / weight if weight > 0 else None


def pooled(
    sections: Mapping[str, Mapping[str, ReferenceRent]],
    parent_of: Mapping[str, str],
    typologies: Sequence[str],
) -> dict[str, ReferenceRent]:
    """A zone made of census sections (a barrio): the mean of its sections' figures weighted
    by their leases, for the first typology any of them publishes. A mean of medians is not
    the zone's median: a declared approximation, kept on its leases' count."""
    members: dict[str, list[Mapping[str, ReferenceRent]]] = {}
    for section, by_typology in sections.items():
        zone = parent_of.get(section)
        if zone:
            members.setdefault(zone, []).append(by_typology)
    out: dict[str, ReferenceRent] = {}
    for zone, rows in members.items():
        typology = next((t for t in typologies if any(t in r for r in rows)), None)
        if typology is None:
            continue
        chosen = [r[typology] for r in rows if typology in r and r[typology].contracts]
        median = _weighted(chosen, "median")
        if median is None:
            continue
        out[zone] = ReferenceRent(
            typology,
            median,
            _weighted(chosen, "p25"),
            _weighted(chosen, "p75"),
            sum(m.contracts or 0.0 for m in chosen),
            sections=len(chosen),
        )
    return out


def calibration(
    reference: Mapping[str, float], refs: Mapping[str, ReferenceRent], min_zones: int
) -> Calibration:
    """Median over the zones with both of (CM mean / reference median). Too few zones stop
    the computation: a scale measured on a handful of zones is not one."""
    ratios = [reference[c] / refs[c].median for c in sorted(reference.keys() & refs.keys())]
    ratios = [r for r in ratios if r > 0]
    if len(ratios) < min_zones:
        msg = f"rent calibration: {len(ratios)} zones with both figures, {min_zones} needed"
        raise ValueError(msg)
    return Calibration(statistics.median(ratios), len(ratios), min(ratios), max(ratios))


def values_at(obs: pd.DataFrame, dims: DimFilter, period: Any) -> dict[str, float]:
    """Each territory's single matching value in `period` (the reference year of the fill)."""
    out: dict[str, float] = {}
    for record in obs.to_dict("records"):
        if record["period_start"] != period or record["value"] is None or pd.isna(record["value"]):
            continue
        record_dims: dict[str, str] = record["dims"]
        if all(record_dims.get(k) == v for k, v in dims.items()):
            out[str(record["territory_code"])] = float(record["value"])
    return out


@dataclass(frozen=True)
class FillConfidence:
    base: float
    few_contracts_below: float = 0.0
    few_contracts: float = 1.0
    by_typology: Mapping[str, float] | None = None

    def of(self, ref: ReferenceRent) -> float:
        confidence = self.base
        if ref.contracts is None or ref.contracts < self.few_contracts_below:
            confidence = min(confidence, self.few_contracts)
        cap = (self.by_typology or {}).get(ref.typology)
        return confidence if cap is None else min(confidence, cap)


def fill_rows(
    refs: Mapping[str, ReferenceRent],
    zones: Sequence[str],
    period: Any,
    scale: Calibration,
    confidence: FillConfidence,
) -> pd.DataFrame:
    """Every zone of `zones`: its reference median x the calibration, with its confidence and
    the figures behind it in `reference` (quartiles scaled the same way); a zone without a
    published median is SOURCE_MISSING, never 0 and never a neighbour's."""
    rows: list[dict[str, Any]] = []
    for code in zones:
        ref = refs.get(code)
        if ref is None:
            rows.append(null_row(code, period, NullReason.SOURCE_MISSING))
            continue
        row = ok_row(code, period, ref.median * scale.ratio, confidence.of(ref))
        row["reference"] = {
            "typology": ref.typology,
            "contracts": ref.contracts,
            "median_m2": round(ref.median, 4),
            "p25_m2": None if ref.p25 is None else round(ref.p25, 4),
            "p75_m2": None if ref.p75 is None else round(ref.p75, 4),
            "sections": ref.sections,
            "calibration": scale.as_inputs(),
            "quartiles": _scaled_quartiles(ref, scale.ratio),
        }
        rows.append(row)
    return result_frame(rows)


def _scaled_quartiles(ref: ReferenceRent, factor: float) -> dict[str, float] | None:
    if ref.p25 is None or ref.p75 is None:
        return None
    return {LOW: ref.p25 * factor, HIGH: ref.p75 * factor}


def scale_quartiles_by_adjustment(result: pd.DataFrame) -> pd.DataFrame:
    """After the lease-signed-in-the-year factor (D-228): the quartiles move with the value."""
    rows: list[dict[str, Any]] = result.to_dict("records")  # pyright: ignore[reportAssignmentType]
    for row in rows:
        reference, adjustment = row.get("reference"), row.get("adjustment")
        if not isinstance(reference, dict) or not isinstance(adjustment, dict):
            continue
        quartiles = reference.get("quartiles")
        if isinstance(quartiles, dict):
            factor = float(adjustment["factor"])
            reference["quartiles"] = {k: round(v * factor, 4) for k, v in quartiles.items()}
    return result_frame(rows)
