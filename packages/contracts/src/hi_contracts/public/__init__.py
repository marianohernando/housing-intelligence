"""PUBLIC contracts (Vida Fácil): the people search and the per-zone list of what is missing.

Shared with the web (TypeScript types are generated from data/schemas/api/*.schema.json).
Version 2 (11 Nov): rent or purchase budget, household with older people in care, the six
«Me importa» priorities, Madrid capital by district and % of fit with tangible facts.
"""

from hi_contracts.public.common import DatasetList, DatasetRef, IndicatorValue, ZoneRef
from hi_contracts.public.gaps import (
    ComparisonGroup,
    GapMethod,
    GapRow,
    GapRowKey,
    GapRowMap,
    GapStatus,
    GapStatusCounts,
    ZoneGapList,
    ZoneGapStatus,
)
from hi_contracts.public.scenario import (
    Anchor,
    AnchorKind,
    Budget,
    BudgetKind,
    Household,
    NearbyNeed,
    NeedKey,
    PriorityKey,
    ScenarioState,
)
from hi_contracts.public.search import (
    ConstraintCheck,
    ConstraintStatus,
    Fact,
    FactKind,
    FactTopic,
    GapHighlight,
    RankedZone,
    RealityCheck,
    Relaxation,
    SearchResult,
    ZoneMatch,
)

__all__ = [
    "Anchor",
    "AnchorKind",
    "Budget",
    "BudgetKind",
    "ComparisonGroup",
    "ConstraintCheck",
    "ConstraintStatus",
    "DatasetList",
    "DatasetRef",
    "Fact",
    "FactKind",
    "FactTopic",
    "GapHighlight",
    "GapMethod",
    "GapRow",
    "GapRowKey",
    "GapRowMap",
    "GapStatus",
    "GapStatusCounts",
    "Household",
    "IndicatorValue",
    "NearbyNeed",
    "NeedKey",
    "PriorityKey",
    "RankedZone",
    "RealityCheck",
    "Relaxation",
    "ScenarioState",
    "SearchResult",
    "ZoneGapList",
    "ZoneGapStatus",
    "ZoneMatch",
    "ZoneRef",
]
