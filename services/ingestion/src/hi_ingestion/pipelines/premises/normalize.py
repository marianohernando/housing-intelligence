"""Census of premises (Ayuntamiento de Madrid) -> premises by situation and proximity shops,
by district and barrio (D-247). Pure functions.

The file of activities has one row per premise and epígrafe. A premise is read once (its
access type, situation, district and barrio are the same on every row) with the epígrafes of
all its rows. What cannot be read goes to quarantine: an undeclared code blocks the run, and
the epígrafes the file marks as pending and the premises without a barrio are listed there
without blocking. Nothing unread is counted as 0.
"""

import re
from collections import Counter
from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.catalog.pipeline import MadridPremisesCensusPipeline, PremiseCode
from hi_domain.geo.codes import admin_unit_id
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    dims_key,
)

ANY_GROUP = "proximidad"  # any group: not a sum of the groups (a shop may be in two)
UNREAD_ACTIVITY = "sin_actividad"  # open premises whose activity cannot be read
_EPIGRAFE = re.compile(r"^\d{6}(\d{2})?$")
QUARANTINE_COLUMNS = ["source_row", "reason", "raw", "blocking"]


@dataclass
class Premise:
    """One premise of the file: what its rows say, read once."""

    access: str
    state: str
    distrito: str | None
    barrio: str | None
    activities: set[str] = field(default_factory=set[str])


@dataclass(frozen=True)
class PremisesObservations:
    """The observations, plus what the whole file says (for the quality checks and counts)."""

    obs: Observations
    rows: int
    premises: int
    counted: int
    not_counted: Mapping[str, int]
    pending: int
    unplaced: int
    blocking: int
    dates: frozenset[date]
    epigrafes: Mapping[str, str]


def clean(raw: Any) -> str:
    return " ".join(str(raw or "").split())


def read_code(code: str, label: str, declared: Mapping[str, PremiseCode], what: str) -> str:
    """The slug of a declared code whose literal is the declared one."""
    known = declared.get(code)
    if known is None or clean(known.label) != label:
        msg = f"{what} {code!r} «{label}» is not declared (read what it means before counting it)"
        raise RowError(msg)
    return known.slug


def read_epigrafe(
    code: str, division: str, label: str, spec: MadridPremisesCensusPipeline
) -> str | None:
    """The epígrafe, None for a premise without one or one the file marks as pending (with its
    declared literal: a pending code whose meaning changes is read by a person first)."""
    if not code:
        return None
    if code in spec.pending_epigrafes:
        if clean(spec.pending_epigrafes[code]) != label:
            msg = f"pending epígrafe {code!r} «{label}» is not the declared one"
            raise RowError(msg)
        return None
    if not _EPIGRAFE.match(code) or not code.startswith(division):
        msg = f"epígrafe {code!r} of division {division!r} does not read as one"
        raise RowError(msg)
    return code


def zone_codes(row: Mapping[str, Any], spec: MadridPremisesCensusPipeline) -> tuple[str, str]:
    """District «2» and barrio «5» -> ('2807902', '28079025')."""
    district, barrio = clean(row.get(spec.district_column)), clean(row.get(spec.barrio_column))
    if not (district.isdigit() and 1 <= int(district) <= 99 and barrio.isdigit()):
        msg = f"premise without a readable district or barrio ({district!r}, {barrio!r})"
        raise RowError(msg)
    if not 1 <= int(barrio) <= 9:  # a Madrid barrio is one digit inside its district
        msg = f"barrio {barrio!r} is not one of a district"
        raise RowError(msg)
    code = f"{spec.municipio_ine}{int(district):02d}"
    return code, f"{code}{int(barrio)}"


def load_date(raw: Any) -> date:
    try:
        return datetime.strptime(clean(raw), "%d/%m/%Y").date()
    except ValueError as exc:
        msg = f"unreadable load date {raw!r}"
        raise RowError(msg) from exc


@dataclass
class _Reading:
    premises: dict[str, Premise] = field(default_factory=dict[str, Premise])
    broken: set[str] = field(default_factory=set[str])
    unplaced: set[str] = field(default_factory=set[str])
    quarantine: list[dict[str, Any]] = field(default_factory=list[dict[str, Any]])
    dates: set[date] = field(default_factory=set[date])
    epigrafes: dict[str, str] = field(default_factory=dict[str, str])

    def bad(self, index: int, reason: str, row: Mapping[str, Any], *, blocking: bool) -> None:
        raw = {k: row.get(k) for k in ("id_local", "id_epigrafe", "desc_epigrafe")}
        self.quarantine.append(
            {"source_row": index, "reason": reason, "raw": str(raw)[:300], "blocking": blocking}
        )


def _premise(row: Mapping[str, Any], spec: MadridPremisesCensusPipeline) -> Premise:
    access = read_code(
        clean(row.get(spec.access_column)),
        clean(row.get(spec.access_label_column)),
        spec.access,
        "access type",
    )
    state = read_code(
        clean(row.get(spec.state_column)),
        clean(row.get(spec.state_label_column)),
        spec.states,
        "situation",
    )
    try:
        distrito, barrio = zone_codes(row, spec)
    except RowError:
        distrito = barrio = None
    return Premise(access, state, distrito, barrio)


def _same_premise(known: Premise | None, read: Premise, key: str) -> Premise:
    """A premise is counted once: every row of it must say the same access, situation and
    zone, or the run blocks (the census promises it; a broken file would count it twice)."""
    if known is None:
        return read
    if (known.access, known.state, known.distrito, known.barrio) != (
        read.access,
        read.state,
        read.distrito,
        read.barrio,
    ):
        msg = f"premise {key} has rows with another access, situation or zone"
        raise RowError(msg)
    return known


def _read_row(
    index: int, row: Mapping[str, Any], spec: MadridPremisesCensusPipeline, reading: _Reading
) -> None:
    key = clean(row.get(spec.premise_column))
    try:
        if not key:
            raise RowError("a row without premise id")
        reading.dates.add(load_date(row.get(spec.date_column)))
        premise = _same_premise(reading.premises.get(key), _premise(row, spec), key)
        reading.premises.setdefault(key, premise)
        code = clean(row.get(spec.epigrafe_column))
        label = clean(row.get(spec.epigrafe_label_column))
        epigrafe = read_epigrafe(code, clean(row.get(spec.division_column)), label, spec)
    except RowError as exc:
        reading.broken.add(key)
        reading.bad(index, str(exc), row, blocking=True)
        return
    if epigrafe is None:
        if code:  # pending: listed, not blocking
            label = clean(row.get(spec.epigrafe_label_column))
            reading.bad(
                index, f"epígrafe pending in the file: {code} «{label}»", row, blocking=False
            )
        return
    premise.activities.add(epigrafe)
    reading.epigrafes.setdefault(epigrafe, clean(row.get(spec.epigrafe_label_column)))


def _observation(
    spec: MadridPremisesCensusPipeline, metric: str, code: str, period: date, dims: dict[str, str]
) -> dict[str, Any]:
    level = TerritoryLevel.BARRIO if len(code) == len("28079011") else TerritoryLevel.DISTRITO
    return dict.fromkeys(OBS_COLUMNS) | {
        "metric_id": metric,
        "territory_level": level.value,
        "territory_code": code,
        "admin_unit_id": admin_unit_id(level.value, code),
        "period_start": period,
        "period_end": period,
        "dims": dims,
        "dims_key": dims_key(dims),
        "unit": "locales",
    }


def _proximity_groups(premise: Premise, spec: MadridPremisesCensusPipeline) -> set[str]:
    groups = {g for g, codes in spec.proximity.items() if premise.activities & set(codes)}
    if groups:
        groups.add(ANY_GROUP)
    if not premise.activities:  # no epígrafe, or only pending ones: activity unknown
        groups.add(UNREAD_ACTIVITY)
    return groups


def _counts(
    counted: list[Premise], spec: MadridPremisesCensusPipeline
) -> tuple[Counter[tuple[str, str]], Counter[tuple[str, str]], set[str]]:
    states: Counter[tuple[str, str]] = Counter()
    groups: Counter[tuple[str, str]] = Counter()
    zones: set[str] = set()
    for premise in counted:
        for zone in (premise.distrito, premise.barrio):
            assert zone is not None  # noqa: S101 - unplaced premises are not counted
            zones.add(zone)
            states[(zone, premise.state)] += 1
            if premise.state == "abierto":
                for group in _proximity_groups(premise, spec):
                    groups[(zone, group)] += 1
    return states, groups, zones


def _rows(
    counted: list[Premise], spec: MadridPremisesCensusPipeline, period: date
) -> list[dict[str, Any]]:
    """Every zone with premises gets every state and group, 0 included (exhaustive census)."""
    states, groups, zones = _counts(counted, spec)
    all_groups = [*spec.proximity, ANY_GROUP, UNREAD_ACTIVITY]
    rows: list[dict[str, Any]] = []
    for zone in sorted(zones):
        for state in spec.counted_states:
            dims = {"situacion": state}
            obs = _observation(spec, spec.premises_metric_id, zone, period, dims)
            rows.append(obs | {"value": float(states[(zone, state)])})
        for group in all_groups:
            dims = {"grupo": group}
            obs = _observation(spec, spec.proximity_metric_id, zone, period, dims)
            rows.append(obs | {"value": float(groups[(zone, group)])})
    return rows


def normalize_premises(
    frame: pd.DataFrame, spec: MadridPremisesCensusPipeline
) -> PremisesObservations:
    reading = _Reading()
    records: list[dict[str, Any]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    for index, row in enumerate(records):
        _read_row(index, row, spec, reading)
    not_counted: Counter[str] = Counter()
    counted: list[Premise] = []
    for key, premise in reading.premises.items():
        if key in reading.broken:
            continue
        if premise.access not in spec.counted_access:
            not_counted[f"access:{premise.access}"] += 1
        elif premise.state not in spec.counted_states:
            not_counted[f"state:{premise.state}"] += 1
        elif premise.barrio is None:
            reading.unplaced.add(key)
            reason = "counted premise without district or barrio"
            reading.bad(-1, reason, {"id_local": key}, blocking=False)
        else:
            counted.append(premise)
    period = max(reading.dates) if reading.dates else date.min
    quarantine = pd.DataFrame(reading.quarantine, columns=QUARANTINE_COLUMNS)
    obs = Observations(
        pd.DataFrame(_rows(counted, spec, period), columns=OBS_COLUMNS),
        quarantine,
        len(records),
    )
    blocking = sum(1 for q in reading.quarantine if q["blocking"])
    return PremisesObservations(
        obs=obs,
        rows=len(records),
        premises=len(reading.premises),
        counted=len(counted),
        not_counted=dict(not_counted),
        pending=len(reading.quarantine) - blocking - len(reading.unplaced),
        unplaced=len(reading.unplaced),
        blocking=blocking,
        dates=frozenset(reading.dates),
        epigrafes=reading.epigrafes,
    )
