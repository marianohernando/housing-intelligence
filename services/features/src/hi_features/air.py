"""Inputs of the air feature (D-237): the monitoring stations (places), their annual means and
the air quality zones (Silver), and the centre of each zone's residential streets."""

from collections.abc import Mapping, Sequence
from datetime import date
from typing import Any

import pandas as pd
from sqlalchemy import Engine, text

from hi_features import walk
from hi_features.loaders import silver_file
from hi_features.methods import STATION_COLUMNS
from hi_ingestion.pipelines.air_quality.run import MEANS_FILE, ZONES_FILE

_STATIONS = text(
    """
    SELECT p.official_entity_id AS code, p.canonical_name AS name, p.municipio_ine, p.attributes,
           coalesce(s.code_official, '') AS section,
           ST_X(p.geom_25830) AS x, ST_Y(p.geom_25830) AS y
      FROM place_master p
      LEFT JOIN geo_admin_unit s ON s.admin_unit_id = p.seccion_admin_unit_id
     WHERE p.category = :category AND p.subcategory = :subcategory AND p.status = 'ACTIVE'
    """
)


def air_zones(engine: Engine, dataset_id: str) -> dict[str, str]:
    """Municipio INE code -> air quality zone code."""
    table = pd.read_csv(silver_file(engine, dataset_id, ZONES_FILE), dtype=str)
    return dict(zip(table["municipio_ine"], table["zone_code"], strict=True))


def station_means(engine: Engine, dataset_ids: Sequence[str]) -> pd.DataFrame:
    frames = [
        pd.read_csv(silver_file(engine, d, MEANS_FILE), dtype={"station_code": str})
        for d in dataset_ids
    ]
    return pd.concat(frames, ignore_index=True)


def stations(
    engine: Engine, f: Mapping[str, Any], level: str, zones: Mapping[str, str]
) -> pd.DataFrame:
    """STATION_COLUMNS: each station with its zone at `level` and its annual mean."""
    params = {"category": f["station_category"], "subcategory": f["station_subcategory"]}
    with engine.connect() as conn:
        places = pd.DataFrame(conn.execute(_STATIONS, params).mappings().all())
    means = station_means(engine, f["means_datasets"])
    mean = dict(zip(means["station_code"], means["mean"], strict=True))
    capture = dict(zip(means["station_code"], means["capture"], strict=True))
    section = places["section"].to_numpy(dtype=str)
    codes: list[str] = places["code"].astype(str).tolist()
    municipios: list[str | None] = places["municipio_ine"].tolist()
    places["zone"] = walk.zone_of_node(section, level, walk.section_parents(engine, level))
    places["air_zone"] = [zones.get(m) if m else None for m in municipios]
    places["mean"] = [mean.get(c) for c in codes]
    places["capture"] = [capture.get(c, 0.0) for c in codes]
    places["traffic"] = [is_traffic(a, f["type_attributes"]) for a in places["attributes"].tolist()]
    return pd.DataFrame(places, columns=STATION_COLUMNS)


TRAFFIC = "tráfico"


def is_traffic(attributes: Mapping[str, Any] | None, keys: Sequence[str]) -> bool:
    """A traffic station by the type its network publishes: «Tráfico» (CM) or «Urbana tráfico»
    (Ayuntamiento); background, suburban and industrial ones are not."""
    return any(TRAFFIC in str((attributes or {}).get(k) or "").casefold() for k in keys)


def reference_period(engine: Engine, dataset_ids: Sequence[str]) -> date:
    years = set(station_means(engine, dataset_ids)["year"].astype(int))
    if len(years) != 1:
        msg = f"station means of different years: {sorted(years)}"
        raise ValueError(msg)
    return date(years.pop(), 1, 1)


def centres(
    engine: Engine, origin_highways: Sequence[str], level: str
) -> dict[str, tuple[float, float]]:
    """Each zone's centre: the street-length weighted mean of its residential street nodes."""
    version = walk.network_version(engine)
    origins = walk.origins(engine, version.path, tuple(origin_highways))
    network = walk.routable(version.path).network
    zone = walk.zone_of_node(origins.section, level, walk.section_parents(engine, level))
    frame = pd.DataFrame(
        {
            "zone": zone,
            "w": origins.weight,
            "wx": origins.weight * network.node_x[origins.node],
            "wy": origins.weight * network.node_y[origins.node],
        }
    )
    sums = frame.loc[frame["zone"] != ""].groupby("zone")[["w", "wx", "wy"]].sum()
    sums = sums.loc[sums["w"] > 0]
    x, y = (sums["wx"] / sums["w"]).to_numpy(), (sums["wy"] / sums["w"]).to_numpy()
    return {str(z): (float(a), float(b)) for z, a, b in zip(sums.index, x, y, strict=True)}


def air_zone_of(codes: Sequence[str], zones: Mapping[str, str]) -> dict[str, str]:
    """A district or barrio is in its municipio's air quality zone (its code starts with it)."""
    return {code: zones[code[:5]] for code in codes if code[:5] in zones}
