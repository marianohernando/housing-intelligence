"""Capacity reachable on foot per person, by zone: the 2SFCA features of the gap rows (D-217).

One computation per feature covers the whole region (catchments cross every boundary); the
zone level only changes how the per-street access is added up. People are placed on the
streets where they live (D-210 origins): each municipio's population, and in Madrid each
district's, scaled to the census total of Madrid so both sources never count twice (D-216).
"""

import json
from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import cache
from typing import Any

import numpy as np
import pandas as pd
from scipy.spatial import KDTree
from sqlalchemy import Engine, text

from hi_contracts.catalog.enums import NullReason
from hi_domain.access.fca import catchments, spread_demand, two_step, zone_totals
from hi_domain.access.graph import FloatArray, IntArray
from hi_features import loaders, methods, walk

MADRID = "28079"
SMALL_POPULATION_CONFIDENCE = methods.SMALL_POPULATION_CONFIDENCE
_FACILITIES = text(
    """
    SELECT subcategory, attributes, municipio_ine, ST_X(geom_25830) AS x, ST_Y(geom_25830) AS y
      FROM place_master
     WHERE category = :category AND status = 'ACTIVE'
     ORDER BY canonical_place_id
    """
)


@dataclass(frozen=True)
class NodeAccess:
    """Per origin node: people placed on it and the capacity per person it reaches."""

    demand: FloatArray
    access: FloatArray
    capacity_per_facility: float  # regional mean, turns capacity into facility-equivalents
    facilities: int
    unreached_capacity: float


@cache
def _all_nodes(path: Any) -> KDTree:
    net = walk.routable(path).network
    return KDTree(np.column_stack([net.node_x, net.node_y]))


def _population(
    engine: Engine, metric: str, dims: Mapping[str, Any], level: str
) -> dict[str, float]:
    pop = methods.population_by_code(loaders.observations(engine, metric, level), dims)
    return {code: float(value) for code, (_, value, _) in pop.items() if value is not None}


def demand_keys(section: Sequence[str]) -> list[str]:
    """Where each origin's people come from: its Madrid district, else its municipio."""
    return [s[:7] if s[:5] == MADRID else s[:5] for s in section]


def people_by_key(
    municipios: Mapping[str, float], districts: Mapping[str, float]
) -> dict[str, float]:
    """Municipio populations, with Madrid split by its districts and scaled to its total."""
    out = {code: value for code, value in municipios.items() if code != MADRID}
    madrid = {code: v for code, v in districts.items() if code.startswith(MADRID)}
    total = sum(madrid.values())
    if MADRID in municipios and total > 0:
        scale = municipios[MADRID] / total
        out |= {code: v * scale for code, v in madrid.items()}
    return out


def _demand(engine: Engine, f: Mapping[str, Any], origins: walk.Origins) -> FloatArray:
    district = f["district_population"]
    people = people_by_key(
        _population(engine, f["population_metric"], f["population_dims"], "municipio"),
        _population(engine, district["metric"], district["dims"], "distrito"),
    )
    keys = demand_keys(origins.section.tolist())
    index = {k: i for i, k in enumerate(people)}
    zone = np.array([index.get(k, -1) for k in keys], dtype=np.int64)
    return spread_demand(zone, origins.weight, np.array(list(people.values()), dtype=float))


def _facilities(engine: Engine, f: Mapping[str, Any]) -> list[dict[str, Any]]:
    with engine.connect() as conn:
        frame = pd.DataFrame(conn.execute(_FACILITIES, {"category": f["category"]}).mappings())
    if not len(frame):
        return []
    return methods.place_filter(frame, f.get("subcategories"), f.get("attributes"))


def supply_of(
    facilities: Sequence[Mapping[str, Any]], spec: Mapping[str, Any], shares: Mapping[Any, float]
) -> FloatArray:
    """Capacity per facility: 1 each, a published attribute, or a municipal total shared."""
    kind = spec["kind"]
    if kind == "count":
        return np.ones(len(facilities))
    if kind == "attribute":
        values = [_number((p["attributes"] or {}).get(spec["attribute"])) for p in facilities]
        return np.array([v if v is not None else np.nan for v in values])
    if kind == "municipal_share":
        key = spec["by_attribute"]
        groups = [(p["municipio_ine"], (p["attributes"] or {}).get(key)) for p in facilities]
        sizes = Counter(groups)
        return np.array([shares.get(g, 0.0) / sizes[g] for g in groups])
    msg = f"unknown supply kind {kind!r}"
    raise ValueError(msg)


def _number(raw: Any) -> float | None:
    try:
        value = float(str(raw).replace(",", "."))
    except ValueError:
        return None
    return value if value >= 0 else None


def municipal_shares(engine: Engine, spec: Mapping[str, Any]) -> dict[tuple[str, str], float]:
    """(municipio, register value) -> units of the metric, e.g. primary classrooms (D-217)."""
    if spec["kind"] != "municipal_share":
        return {}
    obs = methods.latest(loaders.observations(engine, spec["metric"], "municipio"))
    shares: dict[tuple[str, str], float] = {}
    for register_value, dim_value in spec["mapping"].items():
        dims = {**spec["dims"], spec["dim"]: [dim_value]}
        for code, (_, value, _) in methods.population_by_code(obs, dims).items():
            if value is not None:
                shares[(code, register_value)] = value
    return shares


@cache
def node_access(engine: Engine, key: str) -> NodeAccess:
    """The 2SFCA of one feature for every origin node (cached: one run serves every level)."""
    f = json.loads(key)
    version = walk.network_version(engine)
    origins = walk.origins(engine, version.path, tuple(f["origin_highways"]))
    net = walk.routable(version.path)
    facilities = _facilities(engine, f)
    supply = supply_of(facilities, f["supply"], municipal_shares(engine, f["supply"]))
    known = ~np.isnan(supply)
    kept = [p for p, ok in zip(facilities, known, strict=True) if ok]
    radius = float(f["catchment_minutes"]) * float(f["speed_kmh"]) * 1000 / 60
    catch = catchments(
        net,
        np.array([float(p["x"]) for p in kept]),
        np.array([float(p["y"]) for p in kept]),
        radius,
        _all_nodes(version.path),
    )
    demand_nodes = np.zeros(net.network.n_nodes)
    demand_at_origins = _demand(engine, f, origins)
    np.add.at(demand_nodes, origins.node, demand_at_origins)
    result = two_step(catch, supply[known], demand_nodes)
    mean = float(supply[known].mean()) if known.any() else 1.0
    return NodeAccess(
        demand_at_origins,
        result.access[origins.node],
        mean,
        int(known.sum()),
        result.unreached_capacity,
    )


def zone_index(section: Sequence[str], level: str, zones: Sequence[str]) -> IntArray:
    index = {code: i for i, code in enumerate(zones)}
    length = walk.CODE_LENGTH[level]
    return np.array([index.get(s[:length], -1) for s in section], dtype=np.int64)


def rows_for(
    zones: Sequence[str],
    capacity: FloatArray,
    people: FloatArray,
    period: Any,
    f: Mapping[str, Any],
    per_facility: float,
) -> list[dict[str, Any]]:
    per, base = float(f["per"]), float(f.get("confidence", 1.0))
    small = float(f.get("small_population_threshold", 0))
    rows: list[dict[str, Any]] = []
    for code, cap, pop in zip(zones, capacity, people, strict=True):
        if pop <= 0:
            rows.append(methods.null_row(code, period, NullReason.SOURCE_NO_COVERAGE))
            continue
        confidence = min(base, SMALL_POPULATION_CONFIDENCE) if pop < small else base
        rows.append(
            {
                "territory_code": code,
                "period_start": period,
                "value": per * cap / pop,
                "null_reason": None,
                "confidence": confidence,
                # Facility-equivalents: the Poisson test of D-213 counts facilities, not seats.
                "numerator": cap / per_facility,
                "denominator": pop / per,
            }
        )
    return rows


def fca_feature(engine: Engine, f: Mapping[str, Any], level: str, period: Any) -> pd.DataFrame:
    keyed = {k: v for k, v in f.items() if k != "levels"}
    result = node_access(engine, json.dumps(keyed, sort_keys=True, ensure_ascii=False))
    origins = walk.origins(engine, walk.network_version(engine).path, tuple(f["origin_highways"]))
    section = origins.section.tolist()
    zones = walk.zone_codes(engine, level)
    if level == "distrito":  # districts are Madrid capital's (D-200), as in the other gap rows
        zones = [z for z in zones if z.startswith(MADRID)]
    capacity, people = zone_totals(
        zone_index(section, level, zones), result.demand, result.access, len(zones)
    )
    in_region = np.array([0 if s else -1 for s in section], dtype=np.int64)
    region_cap, region_pop = zone_totals(in_region, result.demand, result.access, 1)
    rows = rows_for(zones, capacity, people, period, f, result.capacity_per_facility)
    region = rows_for(
        [methods.REGION_CODE], region_cap, region_pop, period, f, result.capacity_per_facility
    )
    return methods.result_frame(
        [*rows, *(r | {"territory_level": methods.REGION_LEVEL} for r in region)]
    )
