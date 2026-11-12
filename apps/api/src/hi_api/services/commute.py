"""Minutes by public transport to the places of work of a search (CORE-009, D-220).

A place of work becomes a destination of the precomputed matrix: the rail station within
STATION_RADIUS_M (plus the walk from it), else the population centre of the Madrid district or
municipio that contains it. The web offers exactly those places in «Trabajo en».
"""

from dataclasses import dataclass
from typing import Any

import numpy as np
from sqlalchemy import Connection, text

from hi_contracts.public import Anchor
from hi_domain.access.transit import walk_seconds
from hi_domain.fit import Commute

STATION_RADIUS_M = 600
# Scheduled times, one reference weekday, medians of sections: a station is the exact place;
# a zone centre stands for anywhere in the zone, so it is less sure.
STATION_CONFIDENCE, ZONE_CONFIDENCE = 0.7, 0.6
UNREACHABLE_CONFIDENCE = 0.5  # «no trip by 9:00» may also be a gap in the timetables (D-220)
NO_TRIP = Commute(minutes=None, confidence=UNREACHABLE_CONFIDENCE)

_NEAREST_STATION = text(
    """
    SELECT h.hub_id, ST_Distance(h.geom_4326::geography, q.p::geography) AS metres
      FROM transit_hub h, (SELECT ST_SetSRID(ST_MakePoint(:lon, :lat), 4326) AS p) q
     WHERE h.kind = 'station'
     ORDER BY h.geom_4326 <-> q.p
     LIMIT 1
    """
)
_CONTAINING_ZONE = text(
    """
    SELECT h.hub_id
      FROM transit_hub h
      JOIN geo_admin_unit g ON g.admin_unit_id = h.admin_unit_id
     WHERE h.kind = 'zone'
       AND ST_Contains(g.geom_4326, ST_SetSRID(ST_MakePoint(:lon, :lat), 4326))
     ORDER BY (g.level = 'distrito') DESC
     LIMIT 1
    """
)
_TIMES = text("SELECT origin_admin_unit_id, minutes FROM commute_time WHERE hub_id = :hub")
_FEEDS = text("SELECT inputs->'feeds' AS feeds FROM transit_hub WHERE hub_id = :hub")


@dataclass(frozen=True)
class Destination:
    hub_id: str
    walk_minutes: float  # from the station to the place itself
    confidence: float


def destination(conn: Connection, anchor: Anchor) -> Destination | None:
    params = {"lon": anchor.lon, "lat": anchor.lat}
    station = conn.execute(_NEAREST_STATION, params).mappings().first()
    if station is not None and float(station["metres"]) <= STATION_RADIUS_M:
        walk = float(walk_seconds(np.array([float(station["metres"])]))[0]) / 60
        return Destination(str(station["hub_id"]), walk, STATION_CONFIDENCE)
    zone = conn.execute(_CONTAINING_ZONE, params).scalar()
    return None if zone is None else Destination(str(zone), 0.0, ZONE_CONFIDENCE)


@dataclass(frozen=True)
class Commutes:
    by_zone: dict[int, dict[str, Commute]]  # anchor index -> admin_unit_id -> trip
    versions: dict[str, str]  # GTFS dataset_id -> version label, for the provenance
    unresolved: list[int]  # anchors outside every zone: they keep the straight line


def commutes(conn: Connection, anchors: list[Anchor]) -> Commutes:
    by_zone: dict[int, dict[str, Commute]] = {}
    versions: dict[str, str] = {}
    unresolved: list[int] = []
    for i, anchor in enumerate(anchors):
        found = destination(conn, anchor)
        if found is None:
            unresolved.append(i)
            continue
        rows = conn.execute(_TIMES, {"hub": found.hub_id}).mappings().all()
        by_zone[i] = {str(r["origin_admin_unit_id"]): _trip(r, found) for r in rows}
        feeds: list[dict[str, Any]] = conn.execute(_FEEDS, {"hub": found.hub_id}).scalar() or []
        versions.update({str(f["dataset_id"]): str(f["version_label"]) for f in feeds})
    return Commutes(by_zone, versions, unresolved)


def _trip(row: Any, found: Destination) -> Commute:
    if row["minutes"] is None:
        return NO_TRIP
    return Commute(minutes=float(row["minutes"]) + found.walk_minutes, confidence=found.confidence)
