"""In-process cache and per-IP guard for the official services the parcel search calls (D-250).

- `TTLCache`: least recently used, each entry with its own time to live. It keeps our fields
  (transformed answers), never a raw answer of the Catastro, and only in memory.
- `UpstreamGuard`: how many lookups an IP may send to the Catastro or the Ayuntamiento in a
  window. Only cache misses count (a lookup that has to call them), so repeated lookups of the
  same parcel, such as the demo ones, never spend it. The Catastro can suspend an intensive user:
  this keeps one client from making us one.

Both live in each API instance: Vercel runs several, so the guard is per instance (a ceiling,
not a quota).
"""

import time
from collections import OrderedDict, deque
from collections.abc import Callable, Hashable
from typing import Any

from starlette.requests import Request

Clock = Callable[[], float]
MISSING = object()


class TTLCache:
    def __init__(self, maxsize: int = 2000, clock: Clock = time.monotonic) -> None:
        self._data: OrderedDict[Hashable, tuple[float, Any]] = OrderedDict()
        self._maxsize = maxsize
        self._clock = clock

    def get(self, key: Hashable) -> Any:
        """The value, or MISSING when absent or expired."""
        entry = self._data.get(key)
        if entry is None:
            return MISSING
        expires, value = entry
        if expires <= self._clock():
            del self._data[key]
            return MISSING
        self._data.move_to_end(key)
        return value

    def set(self, key: Hashable, value: Any, ttl_s: float) -> None:
        self._data[key] = (self._clock() + ttl_s, value)
        self._data.move_to_end(key)
        while len(self._data) > self._maxsize:
            self._data.popitem(last=False)

    def update(self, key: Hashable, value: Any) -> bool:
        """Replace a live value keeping its expiry (review of #111, R-02: a repair never renews
        the TTL of what it did not fetch again); False when absent or expired."""
        if self.get(key) is MISSING:
            return False
        expires, _ = self._data[key]
        self._data[key] = (expires, value)
        return True

    def clear(self) -> None:
        self._data.clear()

    def __len__(self) -> int:
        return len(self._data)


class RateLimitedError(RuntimeError):
    def __init__(self, retry_after_s: int) -> None:
        super().__init__(f"too many lookups: retry in {retry_after_s} s")
        self.retry_after_s = retry_after_s


class UpstreamGuard:
    """At most `limit` lookups that call the upstream services per IP in `window_s` seconds."""

    def __init__(
        self,
        limit: int,
        window_s: float = 60.0,
        clock: Clock = time.monotonic,
        max_ips: int = 10_000,
    ) -> None:
        self.limit = limit
        self.window_s = window_s
        self._clock = clock
        self._max_ips = max_ips
        self._hits: OrderedDict[str, deque[float]] = OrderedDict()

    def take(self, ip: str) -> None:
        """Count one lookup for `ip`, or raise RateLimitedError with the seconds to wait."""
        now = self._clock()
        hits = self._hits.setdefault(ip, deque())
        self._hits.move_to_end(ip)
        while hits and hits[0] <= now - self.window_s:
            hits.popleft()
        if len(hits) >= self.limit:
            raise RateLimitedError(max(1, int(hits[0] + self.window_s - now + 0.999)))
        hits.append(now)
        while len(self._hits) > self._max_ips:
            self._hits.popitem(last=False)

    def clear(self) -> None:
        self._hits.clear()


def client_ip(request: Request) -> str:
    """The client's IP. On Vercel the platform's proxy sets X-Forwarded-For to the client's
    address (it overwrites what the client sends), and the container trusts only that proxy
    (uvicorn --proxy-headers, infra/deploy/api/Dockerfile); its first entry is the client.
    Without the header (local runs), the socket's address."""
    forwarded = request.headers.get("x-forwarded-for", "")
    first = forwarded.split(",")[0].strip()
    if first:
        return first
    return request.client.host if request.client else "unknown"
