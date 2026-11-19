"""Named response envelopes, so generated TypeScript types get readable names."""

from hi_contracts.api.envelope import Envelope
from hi_contracts.pro.investors import (
    InvestorZone,
    InvestorZoneList,
    ParcelCandidates,
    ParcelSheet,
    ViabilityResult,
)
from hi_contracts.public.common import DatasetList
from hi_contracts.public.explanation import ZoneExplanation, ZoneLookup
from hi_contracts.public.gaps import GapImpact, GapRowMap, ZoneGapList
from hi_contracts.public.places import PlaceCollection
from hi_contracts.public.search import BarrioSearchResult, SearchResult


class ZoneGapListResponse(Envelope[ZoneGapList]):
    """GET /api/v1/gaps/{level}/{code}"""


class GapRowMapResponse(Envelope[GapRowMap]):
    """GET /api/v1/gaps?level=&row="""


class GapImpactResponse(Envelope[GapImpact]):
    """GET /api/v1/gaps/impact"""


class SearchResponse(Envelope[SearchResult]):
    """POST /api/v1/search"""


class BarrioSearchResponse(Envelope[BarrioSearchResult]):
    """POST /api/v1/search/barrios (D-232)"""


class DatasetListResponse(Envelope[DatasetList]):
    """GET /api/v1/datasets"""


class PlacesResponse(Envelope[PlaceCollection]):
    """GET /api/v1/places"""


class ZoneExplanationResponse(Envelope[ZoneExplanation]):
    """MCP tool explicar_zona (MCP-001)"""


class ZoneLookupResponse(Envelope[ZoneLookup]):
    """MCP tool encontrar_zona (MCP-001)"""


class InvestorZoneListResponse(Envelope[InvestorZoneList]):
    """GET /api/v1/investors/zones (D-248)"""


class InvestorZoneResponse(Envelope[InvestorZone]):
    """GET /api/v1/investors/zones/{admin_unit_id} (D-248)"""


class ViabilityResponse(Envelope[ViabilityResult]):
    """POST /api/v1/investors/viability (D-248)"""


class ParcelSheetResponse(Envelope[ParcelSheet]):
    """GET /api/v1/investors/parcels (D-250)"""


class ParcelCandidatesResponse(Envelope[ParcelCandidates]):
    """GET /api/v1/investors/parcels/candidates (D-250)"""
