"""Named response envelopes, so generated TypeScript types get readable names."""

from hi_contracts.api.envelope import Envelope
from hi_contracts.public.common import DatasetList
from hi_contracts.public.gaps import GapRowMap, ZoneGapList
from hi_contracts.public.places import PlaceCollection
from hi_contracts.public.search import SearchResult


class ZoneGapListResponse(Envelope[ZoneGapList]):
    """GET /api/v1/gaps/{level}/{code}"""


class GapRowMapResponse(Envelope[GapRowMap]):
    """GET /api/v1/gaps?level=&row="""


class SearchResponse(Envelope[SearchResult]):
    """POST /api/v1/search"""


class DatasetListResponse(Envelope[DatasetList]):
    """GET /api/v1/datasets"""


class PlacesResponse(Envelope[PlaceCollection]):
    """GET /api/v1/places"""
