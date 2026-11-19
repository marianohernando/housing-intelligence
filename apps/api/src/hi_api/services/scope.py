"""POST /api/v1/search by «Dónde buscar» (D-238): the whole region or its surroundings and
villages by municipio (hi_api.services.search), and Madrid capital by its barrios
(hi_api.services.barrios). The same engine ranks them all."""

from sqlalchemy import Connection

from hi_api.services.barrios import load_barrios
from hi_api.services.search import answer, load
from hi_contracts.public import ScenarioState, SearchResult, SearchScope


def search(conn: Connection, scenario: ScenarioState) -> tuple[SearchResult, list[str], str | None]:
    """The result, warnings and the data version of the search in its scope."""
    if scenario.scope == SearchScope.MADRID:
        return answer(conn, scenario, load_barrios(conn, scenario, None), "barrios")
    return answer(conn, scenario, load(conn, scenario))
