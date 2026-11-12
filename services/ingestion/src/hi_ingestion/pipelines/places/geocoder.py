"""CartoCiudad (IGN) address geocoder with an on-disk cache (D-216).

Only used for register rows whose coordinates are missing or contradict their address. Every
answer is cached by query, so a reload makes no new requests and gives the same places.
"""

import json
from pathlib import Path
from typing import Any

import httpx

from hi_ingestion.http import get_json, make_client
from hi_ingestion.pipelines.places.coordinates import GeocodeHit

FIND_URL = "https://www.cartociudad.es/geocoder/api/geocoder/find"
SOURCE_ID = "ign_cartociudad"


def hit_from_answer(answer: dict[str, Any] | None) -> GeocodeHit | None:
    """The fields we trust from a CartoCiudad `find` answer; None without a point."""
    if not answer:
        return None
    lon, lat, municipio = answer.get("lng"), answer.get("lat"), answer.get("muniCode")
    if not lon or not lat or not municipio:
        return None
    portal = answer.get("portalNumber")
    return GeocodeHit(
        float(lon),
        float(lat),
        str(municipio),
        str(answer.get("type") or ""),
        int(portal) if isinstance(portal, int | float) else None,
    )


class CachedGeocoder:
    def __init__(self, cache_path: Path, client: httpx.Client | None = None) -> None:
        self.cache_path = cache_path
        self.client = client
        self.cache: dict[str, dict[str, Any] | None] = (
            json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
        )
        self.requests = 0

    def _ask(self, query: str) -> dict[str, Any] | None:
        self.client = self.client or make_client(timeout=30.0)
        self.requests += 1
        try:
            data, _ = get_json(self.client, FIND_URL, params={"q": query})
        except ValueError:  # an empty body for addresses it cannot parse: no answer
            return None
        if not isinstance(data, dict):
            return None
        keep = ("lng", "lat", "muniCode", "muni", "type", "address", "portalNumber", "postalCode")
        return {k: data.get(k) for k in keep}  # pyright: ignore[reportUnknownMemberType]

    def __call__(self, query: str) -> GeocodeHit | None:
        if query not in self.cache:
            self.cache[query] = self._ask(query)
            self.save()
        return hit_from_answer(self.cache[query])

    def save(self) -> None:
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        text = json.dumps(self.cache, ensure_ascii=False, indent=1, sort_keys=True)
        self.cache_path.write_text(text, encoding="utf-8")
