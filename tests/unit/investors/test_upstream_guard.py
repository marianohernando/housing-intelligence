"""D-250: the in-process cache and the per-IP guard of the parcel search, with a fake clock."""

import pytest
from starlette.requests import Request

from hi_api.services.upstream_guard import (
    MISSING,
    RateLimitedError,
    TTLCache,
    UpstreamGuard,
    client_ip,
)


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now


def test_entries_expire_with_their_own_ttl() -> None:
    clock = Clock()
    cache = TTLCache(maxsize=10, clock=clock)
    cache.set("catastro", 1, ttl_s=7 * 86_400)
    cache.set("planning", 2, ttl_s=86_400)
    clock.now += 86_400
    assert cache.get("planning") is MISSING
    assert cache.get("catastro") == 1
    clock.now += 6 * 86_400
    assert cache.get("catastro") is MISSING


def test_a_none_is_a_cached_answer_not_a_miss() -> None:
    cache = TTLCache()
    cache.set("planning", None, ttl_s=60)
    assert cache.get("planning") is None


def test_the_least_recently_used_goes_first() -> None:
    cache = TTLCache(maxsize=2)
    cache.set("a", 1, 60)
    cache.set("b", 2, 60)
    assert cache.get("a") == 1  # «a» is now the most recent
    cache.set("c", 3, 60)
    assert cache.get("b") is MISSING and cache.get("a") == 1 and len(cache) == 2


def test_the_guard_counts_per_ip_in_a_sliding_window() -> None:
    clock = Clock()
    guard = UpstreamGuard(limit=3, window_s=60, clock=clock)
    for _ in range(3):
        guard.take("203.0.113.7")
    with pytest.raises(RateLimitedError) as exc:
        guard.take("203.0.113.7")
    assert exc.value.retry_after_s == 60
    guard.take("198.51.100.4")  # another IP, another budget
    clock.now += 30
    with pytest.raises(RateLimitedError) as exc:
        guard.take("203.0.113.7")
    assert exc.value.retry_after_s == 30
    clock.now += 30
    guard.take("203.0.113.7")  # the first three have left the window


def test_the_guard_forgets_the_oldest_ips() -> None:
    guard = UpstreamGuard(limit=1, window_s=60, max_ips=2)
    guard.take("a")
    guard.take("b")
    guard.take("c")  # «a» is dropped, so it starts again
    guard.take("a")


def request(headers: dict[str, str], host: str = "10.0.0.9") -> Request:
    raw = [(k.lower().encode(), v.encode()) for k, v in headers.items()]
    return Request({"type": "http", "headers": raw, "client": (host, 1234)})


def test_the_client_ip_is_the_first_forwarded_address() -> None:
    assert client_ip(request({"X-Forwarded-For": "203.0.113.7, 10.0.0.1"})) == "203.0.113.7"
    assert client_ip(request({})) == "10.0.0.9"
