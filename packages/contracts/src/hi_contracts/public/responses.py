"""Named response envelopes, so generated TypeScript types get readable names."""

from hi_contracts.api.envelope import Envelope
from hi_contracts.public.gaps import ZoneGapList
from hi_contracts.public.search import SearchResult


class ZoneGapListResponse(Envelope[ZoneGapList]):
    """GET /api/v1/gaps/{level}/{code}"""


class SearchResponse(Envelope[SearchResult]):
    """POST /api/v1/search"""
