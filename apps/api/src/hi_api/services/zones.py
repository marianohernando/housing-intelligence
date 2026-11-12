"""Zones found by their official name (MCP-001): municipios and the Madrid districts, the
zones an agent asks about («¿qué falta en Chamartín?»), returned as the same ZoneRef as GET
/gaps. Parameterised SQL only; the matching is hi_domain.geo.names.match_rank.
"""

from sqlalchemy import Connection, text

from hi_api.services.gaps import zone_ref
from hi_contracts.catalog.enums import TerritoryLevel
from hi_contracts.public import ZoneLookup
from hi_domain.geo.names import display_name, match_rank
from hi_domain.search import SPLIT_BY_DISTRICT

NAMED_LEVELS = (TerritoryLevel.MUNICIPIO, TerritoryLevel.DISTRITO)
MAX_MATCHES = 10
LOOKUP_VERSION = "zones-v1"  # official names, matched by hi_domain.geo.names.match_rank

# The zones of the product (D-200): every municipio and the districts of Madrid capital, not
# the census districts of the other municipios.
_NAMES = text(
    """
    SELECT level, code_official AS code, name
      FROM geo_admin_unit
     WHERE name IS NOT NULL
       AND (level = 'municipio' OR (level = 'distrito' AND left(code_official, 5) = ANY(:split)))
    """
)


def find_zones(conn: Connection, query: str, limit: int = MAX_MATCHES) -> ZoneLookup:
    """Best match first (same name, then starts with it, a word starts with it, inside it);
    ties go municipio before district, then by name."""
    ranked: list[tuple[int, int, str, TerritoryLevel, str]] = []
    for row in conn.execute(_NAMES, {"split": list(SPLIT_BY_DISTRICT)}).mappings():
        name = display_name(row["name"])
        rank = match_rank(query, name)
        if rank is not None:
            level = TerritoryLevel(row["level"])
            ranked.append((rank, NAMED_LEVELS.index(level), name, level, row["code"]))
    ranked.sort()
    zones = [zone_ref(conn, level, code) for _, _, _, level, code in ranked[:limit]]
    return ZoneLookup(query=query, zones=zones, total=len(ranked))
