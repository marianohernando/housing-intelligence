"""HTTP client with polite defaults and bounded retries for external sources."""

from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

USER_AGENT = (
    "housing-intelligence/0.0.1 "
    "(+https://github.com/marianohernando/housing-intelligence; DATAMAD 2026 open-data research)"
)
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class SourceUnavailableError(RuntimeError):
    """The source answered, but not with usable data (maintenance page, 404, non-JSON)."""


def make_client(timeout: float = 60.0) -> httpx.Client:
    return httpx.Client(
        timeout=timeout,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
        follow_redirects=True,
    )


def is_retryable(exc: BaseException) -> bool:
    if isinstance(exc, httpx.HTTPStatusError):
        return exc.response.status_code in RETRYABLE_STATUS
    return isinstance(exc, httpx.TransportError)


polite_retry = retry(
    retry=retry_if_exception(is_retryable),
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True,
)


@polite_retry
def get_json(
    client: httpx.Client, url: str, params: dict[str, Any] | None = None
) -> tuple[Any, httpx.Response]:
    response = client.get(url, params=params)
    if response.status_code in RETRYABLE_STATUS:
        response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    if response.status_code >= 400 or "json" not in content_type:
        msg = f"{url} -> HTTP {response.status_code} ({content_type or 'no content-type'})"
        raise SourceUnavailableError(msg)
    return response.json(), response
