"""«Dónde buscar» (D-238): Madrid capital, its surroundings or the villages, by the statistical
zoning of the Comunidad de Madrid (data/catalog/zoning/search_scope.yaml)."""

from hi_contracts.public import SearchScope
from hi_domain.geo.zoning_data import SCOPE_BY_MUNICIPIO

MUNICIPIO_CODE_LENGTH = 5


def scope_of(code: str) -> SearchScope | None:
    """The part of the region a municipio, district or barrio is in, by its INE code (they all
    start with their municipio's). None for a municipio the zoning does not list."""
    scope = SCOPE_BY_MUNICIPIO.get(code[:MUNICIPIO_CODE_LENGTH])
    return None if scope is None else SearchScope(scope)


def in_scope(code: str, scope: SearchScope) -> bool:
    """Whether a zone is searched. The whole region keeps every zone, listed or not."""
    return scope == SearchScope.ALL or scope_of(code) == scope
