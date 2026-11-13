"""One zone explained with its sources, and zones found by name (MCP-001).

What the MCP server gives an agent besides the search and the list of what is missing: the
zone as the search sees it for one scenario (the same % of fit, conditions and facts as its
card in POST /search), every indicator behind it and the datasets it reads, each with the
text its licence asks to show. Zones are found by name because agents do not know INE codes.
"""

from pydantic import BaseModel, ConfigDict, Field

from hi_contracts.public.common import DatasetRef, IndicatorValue, ZoneRef
from hi_contracts.public.scenario import ScenarioState
from hi_contracts.public.search import ConstraintCheck, Fact, GapHighlight


class ZoneExplanation(BaseModel):
    """A zone of the search explained for one scenario (the default scenario asks nothing, so
    the facts are the walking minutes the search shows as context)."""

    model_config = ConfigDict(extra="forbid")

    zone: ZoneRef
    scenario: ScenarioState
    match_pct: int | None = Field(
        ge=0,
        le=100,
        description="% of fit with the scenario, not a grade: 100 when it asks nothing, as in "
        "the search; None = no data for anything it asks",
    )
    confidence: float = Field(ge=0, le=1)
    facts: list[Fact] = Field(max_length=5, description="Same facts as the zone's search card")
    constraints: list[ConstraintCheck] = Field(description="PASS / FAIL / UNKNOWN per condition")
    estimated_cost_eur: float | None = Field(
        default=None,
        ge=0,
        description="Purchase price in € to buy (D-227), else monthly rent in €/month",
    )
    gap_highlights: list[GapHighlight] = Field(
        default_factory=list[GapHighlight], max_length=3, description="Full list: GET /gaps"
    )
    indicators: list[IndicatorValue] = Field(
        description="Every indicator the search reads for this zone, with its datasets"
    )
    datasets: list[DatasetRef] = Field(
        description="Datasets behind the indicators, facts and highlights, with attribution_text"
    )
    cm_open_data_count: int = Field(ge=0, description="How many of them are CM open data")
    methodology_version: str


class ZoneLookup(BaseModel):
    """Municipios and Madrid districts whose official name matches a query, best match first."""

    model_config = ConfigDict(extra="forbid")

    query: str
    zones: list[ZoneRef] = Field(description="The best matches, at most 10")
    total: int = Field(ge=0, description="Every match, also those left out of `zones`")
