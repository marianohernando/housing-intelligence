"""PUBLIC product contracts: the people search and the per-zone list of what is missing.

Shared with the web (TypeScript types are generated from data/schemas/api/*.schema.json).
"""

from hi_contracts.public.common import DatasetRef, IndicatorValue, ZoneRef
from hi_contracts.public.gaps import GapMethod, GapRow, GapRowKey, GapStatus, ZoneGapList
from hi_contracts.public.scenario import (
    Anchor,
    AnchorKind,
    Household,
    NearbyNeed,
    NeedKey,
    PriorityKey,
    ScenarioState,
    Tenure,
)
from hi_contracts.public.search import (
    ConstraintCheck,
    ConstraintStatus,
    RankedZone,
    RealityCheck,
    Reason,
    ReasonKind,
    Relaxation,
    SearchResult,
)

__all__ = [
    "Anchor",
    "AnchorKind",
    "ConstraintCheck",
    "ConstraintStatus",
    "DatasetRef",
    "GapMethod",
    "GapRow",
    "GapRowKey",
    "GapStatus",
    "Household",
    "IndicatorValue",
    "NearbyNeed",
    "NeedKey",
    "PriorityKey",
    "RankedZone",
    "RealityCheck",
    "Reason",
    "ReasonKind",
    "Relaxation",
    "ScenarioState",
    "SearchResult",
    "Tenure",
    "ZoneGapList",
    "ZoneRef",
]
