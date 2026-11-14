"""People search result v2 (CORE-003, decisions of 11 Nov).

Each zone gets a % of fit with 3-5 tangible facts underneath, each with its confidence; never
a grade over 100. Hard constraints are PASS / FAIL / UNKNOWN and UNKNOWN never counts as PASS
(CLAUDE.md §14); zones failing one constraint are only shown as explicit near misses. Zones
are municipios, with Madrid capital split into its 21 districts; inside a district, its
barrios (D-232).
"""

from enum import StrEnum
from typing import Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public.common import DatasetRef, IndicatorValue, ZoneRef
from hi_contracts.public.gaps import GapStatus
from hi_contracts.public.scenario import ScenarioState


class ConstraintStatus(StrEnum):
    PASS = "PASS"  # noqa: S105 - constraint status, not a credential
    FAIL = "FAIL"
    UNKNOWN = "UNKNOWN"


class ConstraintCheck(BaseModel):
    """One hard condition of the scenario evaluated on one zone."""

    model_config = ConfigDict(extra="forbid")

    constraint_id: str = Field(
        pattern=r"^(budget|near:[a-z_]+|commute:\d)$",
        examples=["budget", "near:colegio", "commute:0"],
    )
    label: str = Field(examples=["Alquiler hasta 1.500 €/mes"])
    status: ConstraintStatus
    value: float | None = None
    threshold: float | None = None
    unit: str | None = None
    confidence: float = Field(ge=0, le=1)
    explanation: str = Field(examples=["Un piso de 90 m² cuesta unos 1.420 €/mes aquí"])


class FactKind(StrEnum):
    STRENGTH = "strength"
    WEAKNESS = "weakness"
    UNKNOWN = "unknown"


class FactTopic(StrEnum):
    """Which icon the web shows next to a fact."""

    COSTE = "coste"
    TRANSPORTE = "transporte"
    SALUD = "salud"
    COLEGIOS = "colegios"
    ZONAS_VERDES = "zonas_verdes"
    SEGURIDAD = "seguridad"
    ACCESIBILIDAD = "accesibilidad"
    TRAYECTO = "trayecto"
    OTRO = "otro"


class Fact(BaseModel):
    """A tangible, plain-language fact («Colegio público a 6 min andando») with its confidence,
    always traceable to an indicator and its datasets."""

    model_config = ConfigDict(extra="forbid")

    kind: FactKind
    topic: FactTopic
    text: str = Field(examples=["Colegio con primaria a unos 6 min andando"])
    confidence: float = Field(ge=0, le=1)
    indicator: IndicatorValue | None = None


class GapHighlight(BaseModel):
    """One row of «Qué falta aquí» for the zone card; the full list is GET /gaps."""

    model_config = ConfigDict(extra="forbid")

    row: GapRowKey
    label: str
    status: GapStatus


class RankedZone(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rank: int = Field(ge=1)
    zone: ZoneRef
    match_pct: int = Field(ge=0, le=100, description="% of fit with the search, not a grade")
    confidence: float = Field(ge=0, le=1)
    facts: list[Fact] = Field(
        max_length=5,
        description="Up to 5 tangible facts, most important to the person first; unknown last",
    )
    constraints: list[ConstraintCheck]
    failed_constraints: list[str] = Field(
        default_factory=list[str], description="constraint_id values with FAIL (near misses)"
    )
    estimated_cost_eur: float | None = Field(
        default=None, ge=0, description="Monthly rent or purchase price for the needed area"
    )
    estimated_cost_confidence: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Confidence of `estimated_cost_eur`: that of its rent or price per m² (0,5 for "
        "the estimated purchase price of D-234); None without a cost",
    )
    gap_highlights: list[GapHighlight] = Field(default_factory=list[GapHighlight], max_length=3)


class ZoneMatch(BaseModel):
    """Every evaluated zone, for the choropleth («Encaje con tu búsqueda»)."""

    model_config = ConfigDict(extra="forbid")

    zone: ZoneRef
    match_pct: int | None = Field(default=None, ge=0, le=100, description="None = unknown")
    passes_all: bool
    failed_constraints: list[str] = Field(default_factory=list[str])
    estimated_cost_eur: float | None = Field(
        default=None,
        ge=0,
        description="Monthly rent or purchase price for the needed area, as in RankedZone: the "
        "zone card shows it for any zone (D-234); None without a cost",
    )
    estimated_cost_confidence: float | None = Field(
        default=None, ge=0, le=1, description="Confidence of `estimated_cost_eur`"
    )


class Relaxation(BaseModel):
    """How many more zones appear when one condition is relaxed and the rest stay.

    `relaxed_scenario` is the scenario with that change applied: the web sends it back to
    POST /search when the person taps the option.
    """

    model_config = ConfigDict(extra="forbid")

    constraint_id: str
    label: str = Field(examples=["+100 €/mes", "+10 min de trayecto"])
    zones_if_relaxed: int = Field(ge=0)
    added_zones: int = Field(ge=0)
    relaxed_scenario: ScenarioState


class RealityCheck(BaseModel):
    model_config = ConfigDict(extra="forbid")

    zones_evaluated: int = Field(ge=0)
    zones_passing: int = Field(ge=0, description="Every constraint PASS")
    zones_unknown: int = Field(ge=0, description="No FAIL but some UNKNOWN: not counted as passing")
    binding_constraint: str | None = Field(
        default=None,
        description="constraint_id that the most zones FAIL; None when no zone fails any. A "
        "zone where a condition is UNKNOWN is not counted here (D-234)",
    )
    unknown_by_constraint: dict[str, int] = Field(
        default_factory=dict[str, int],
        description="Among the `zones_unknown` zones, how many have each condition UNKNOWN "
        "(constraint_id -> zones): what is missing is data, so relaxing it is never offered",
    )
    relaxations: list[Relaxation] = Field(description="Sorted by added_zones, largest first")

    @model_validator(mode="after")
    def _counts_add_up(self) -> Self:
        if self.zones_passing + self.zones_unknown > self.zones_evaluated:
            msg = "passing + unknown zones cannot exceed the evaluated zones"
            raise ValueError(msg)
        for relaxation in self.relaxations:
            if relaxation.zones_if_relaxed != self.zones_passing + relaxation.added_zones:
                msg = f"{relaxation.constraint_id}: zones_if_relaxed = passing + added"
                raise ValueError(msg)
        return self


class SearchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenario: ScenarioState
    results: list[RankedZone] = Field(description="Zones passing every constraint, best first")
    near_misses: list[RankedZone] = Field(
        default_factory=list[RankedZone], description="Explicit alternatives failing one condition"
    )
    all_zones: list[ZoneMatch] = Field(description="Every evaluated zone, for the map")
    reality_check: RealityCheck
    datasets: list[DatasetRef] = Field(description="Every dataset behind this result")
    methodology_version: str


MADRID_DISTRICT_PATTERN = r"^28079\d{2}$"


class BarrioSearchRequest(BaseModel):
    """POST /api/v1/search/barrios (D-232): the same scenario as POST /search, inside one
    district of Madrid capital. A relaxed scenario of its Reality Check goes back here with
    the same `distrito`."""

    model_config = ConfigDict(extra="forbid")

    scenario: ScenarioState
    distrito: str = Field(
        pattern=MADRID_DISTRICT_PATTERN,
        description="INE code of a district of Madrid capital (28079 + its two digits)",
        examples=["2807920"],
    )


class BarrioSearchResult(SearchResult):
    """The barrios of one Madrid district ranked by the same engine as POST /search (D-232):
    the same conditions, % of fit, facts, near misses and Reality Check, with barrios as zones.
    `gap_highlights` stay empty: «Qué falta» is by district (GET /gaps/distrito/{code})."""

    distrito: ZoneRef

    @model_validator(mode="after")
    def _only_barrios_of_the_district(self) -> Self:
        if self.distrito.level != TerritoryLevel.DISTRITO:
            msg = f"distrito must be a district, got {self.distrito.level}"
            raise ValueError(msg)
        zones = [z.zone for z in [*self.results, *self.near_misses]] + [
            z.zone for z in self.all_zones
        ]
        for zone in zones:
            if zone.level != TerritoryLevel.BARRIO or not zone.code.startswith(self.distrito.code):
                msg = f"only barrios of {self.distrito.code}: got {zone.level} {zone.code}"
                raise ValueError(msg)
        return self
