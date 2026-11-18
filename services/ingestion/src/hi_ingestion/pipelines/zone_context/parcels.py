"""Portal del Suelo parcels -> metric observations (D-246). Pure functions.

One observation per residential parcel in its municipio and, for Madrid, in its district and
barrio, located beforehand from a versioned point inside each parcel (`Placement`). The value is
the parcel's buildable m²; its dimensions say what the zone view lists. Codes become a label
only when the CM publishes their meaning (the spec's `regimes` and `urbanization`).
"""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd

from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.catalog.pipeline import PublicLandParcelsPipeline
from hi_domain.geo.codes import admin_unit_id
from hi_domain.geo.names import name_key
from hi_ingestion.pipelines.stat_tables.normalize import (
    OBS_COLUMNS,
    Observations,
    RowError,
    dims_key,
    parse_value,
)
from hi_ingestion.pipelines.zone_context.normalize import observation

REF = "referencia_codigo"
MUNICIPIO = "municipio_codigo"
MUNICIPIO_NAME = "municipio_descripcion"
USE = "uso_principal_codigo"
REGIME = "regimen_codigo"
URBANIZATION = "urbanizacion_codigo"
LOCATION = "localizacion_descripcion"
PARCEL = "parcela_descripcion"
MANAGER = "gestor_descripcion"
BUILDABLE = "superficie_edificable"
VIEWER = "url_visor"
MISSING = ["", "-"]


@dataclass(frozen=True)
class Placement:
    """Where a Madrid parcel is: its district and barrio, or None when its point is in none."""

    distrito: str | None
    barrio: str | None


@dataclass(frozen=True)
class ParcelObservations:
    """The kept parcels, plus what the whole file says (its size and the rows of other uses)."""

    obs: Observations
    parcels: int
    out_of_scope: int
    municipios: frozenset[str]


def clean(raw: Any) -> str:
    """One line, single spaces: the file has line breaks and doubled spaces inside names."""
    return " ".join(str(raw or "").split())


def _code(raw: str, documented: Mapping[str, str], undocumented: list[str], what: str) -> str:
    """The slug of a code the CM explains; "" for one it uses without explaining it."""
    if raw in documented:
        return documented[raw]
    if raw in undocumented:
        return ""
    msg = f"{what} code {raw!r} is not declared (read what it means before showing it)"
    raise RowError(msg)


def municipio_code(
    row: Mapping[str, Any], spec: PublicLandParcelsPipeline, names: Mapping[str, str]
) -> str:
    """`28` + the code inside the province, whose name must be the geography's (no case, accents,
    signs or article order: «Molar, El» is «Molar (El)»)."""
    raw = clean(row.get(MUNICIPIO))
    code = f"{spec.province_ine}{raw}"
    if not (raw.isdigit() and len(raw) == len("079")) or code not in names:
        msg = f"municipio code {raw!r} is not a municipio of the geography"
        raise RowError(msg)
    name = clean(row.get(MUNICIPIO_NAME))
    if name_key(name) != name_key(names[code]):
        msg = f"municipio {code} is {names[code]!r} in the geography, not {name!r}"
        raise RowError(msg)
    return code


def _dims(row: Mapping[str, Any], spec: PublicLandParcelsPipeline) -> dict[str, str]:
    ref = clean(row.get(REF))
    if not ref:
        raise RowError("a parcel without reference")
    regime = _code(clean(row.get(REGIME)), spec.regimes, spec.undocumented_regimes, "regime")
    urbanized = clean(row.get(URBANIZATION))
    stage = _code(urbanized, spec.urbanization, spec.undocumented_urbanization, "urbanization")
    dims = {
        "item": ref,
        "name": clean(row.get(LOCATION)),
        "parcel": clean(row.get(PARCEL)),
        "regime": regime,
        "manager": clean(row.get(MANAGER)),
        "url": clean(row.get(VIEWER)),
        "stage": stage,
    }
    return {k: v for k, v in dims.items() if v}  # a dimension the parcel does not have is absent


def _places(
    ref: str, code: str, spec: PublicLandParcelsPipeline, placed: Mapping[str, Placement]
) -> list[tuple[str, str]]:
    places = [(TerritoryLevel.MUNICIPIO.value, code)]
    if code != spec.split_municipio_ine:
        return places
    where = placed.get(ref)
    if where is None:
        msg = f"parcel {ref} of {code} has no point: read the points again"
        raise RowError(msg)
    if where.distrito is None or where.barrio is None:
        msg = f"the point of parcel {ref} is in no district or barrio of {code}"
        raise RowError(msg)
    return [*places, ("distrito", where.distrito), ("barrio", where.barrio)]


def _parcel_rows(
    row: Mapping[str, Any],
    spec: PublicLandParcelsPipeline,
    names: Mapping[str, str],
    placed: Mapping[str, Placement],
    observed: date,
) -> list[dict[str, Any]]:
    code = municipio_code(row, spec, names)
    dims = _dims(row, spec)
    raw = clean(row.get(BUILDABLE))
    value, null_reason = parse_value(raw, MISSING, spec.csv.decimal)
    return [
        observation(
            metric_id=spec.metric_id,
            territory_level=level,
            territory_code=territory,
            territory_name=names[code] if level == TerritoryLevel.MUNICIPIO.value else None,
            admin_unit_id=admin_unit_id(level, territory),
            period_start=observed,
            period_end=observed,
            dims=dims,
            dims_key=dims_key(dims),
            value=value,
            null_reason=null_reason,
            unit="m2",
            raw_value=raw,
        )
        for level, territory in _places(dims["item"], code, spec, placed)
    ]


def normalize_parcels(
    frame: pd.DataFrame,
    spec: PublicLandParcelsPipeline,
    names: Mapping[str, str],
    placed: Mapping[str, Placement],
    observed: date,
) -> ParcelObservations:
    """`names`: INE code -> the geography's name. `placed`: Madrid's parcels by reference.
    Parcels of other uses are counted, never quarantined; a repeated reference is."""
    records: list[dict[str, Any]] = frame.to_dict("records")  # pyright: ignore[reportAssignmentType]
    kept = [(i, r) for i, r in enumerate(records) if clean(r.get(USE)) in spec.uses]
    rows: list[dict[str, Any]] = []
    bad: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, row in kept:
        try:
            ref = clean(row.get(REF))
            if ref in seen:
                raise RowError(f"parcel {ref} is repeated")
            seen.add(ref)
            rows.extend(_parcel_rows(row, spec, names, placed, observed))
        except (RowError, KeyError) as exc:
            bad.append({"source_row": index, "reason": str(exc), "raw": str(row)[:300]})
    frame_out = pd.DataFrame(rows, columns=OBS_COLUMNS)
    municipios = frame_out.loc[frame_out["territory_level"] == "municipio", "territory_code"]
    return ParcelObservations(
        Observations(
            frame_out, pd.DataFrame(bad, columns=["source_row", "reason", "raw"]), len(kept)
        ),
        len(records),
        len(records) - len(kept),
        frozenset(str(c) for c in municipios),
    )
