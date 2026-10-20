"""Shared helpers for harvesters."""

import json
import re
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol

import httpx

from hi_contracts.catalog.candidate import BronzeRef, CandidateRecord
from hi_ingestion.bronze import BronzeWriter


@dataclass
class HarvestResult:
    source_id: str
    candidates: list[CandidateRecord] = field(default_factory=list[CandidateRecord])
    pages: int = 0
    status: str = "OK"  # OK | MAINTENANCE | PARTIAL
    message: str | None = None


class Harvester(Protocol):
    source_id: str

    def harvest(self, client: httpx.Client, bronze: BronzeWriter) -> HarvestResult: ...


def slugify(text: str, max_len: int = 60) -> str:
    ascii_text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "_", ascii_text.lower()).strip("_")
    return slug[:max_len].rstrip("_")


def dedupe(values: list[str]) -> list[str]:
    seen: dict[str, None] = {}
    for value in values:
        cleaned = value.strip()
        if cleaned:
            seen.setdefault(cleaned, None)
    return list(seen)


def snapshot_page(
    bronze: BronzeWriter, page: int, payload: Any, response: httpx.Response
) -> BronzeRef:
    content = json.dumps(payload, ensure_ascii=False, sort_keys=True).encode()
    artifact = bronze.write(
        f"page_{page:04d}.json",
        content,
        str(response.url),
        response.status_code,
        dict(response.headers),
    )
    return BronzeRef(path=artifact.path, sha256=artifact.sha256)


def iter_pages(total: int, page_size: int) -> Iterator[int]:
    yield from range(0, max(total, 0), page_size)
