"""Shared pipeline plumbing: run summaries, CSV reading, evidence and Silver paths."""

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from hi_contracts.catalog.pipeline import CsvFormat
from hi_ingestion.bronze import REPO_ROOT

DATA_DIR = REPO_ROOT / "data"
EVIDENCE_GATE_01 = REPO_ROOT / "evidence" / "gate-01"


@dataclass
class RunSummary:
    status: str
    dataset_id: str
    checksum: str
    correlation_id: str
    version_label: str | None = None
    counts: dict[str, Any] = field(default_factory=dict[str, Any])
    quality: dict[str, Any] = field(default_factory=dict[str, Any])
    evidence_dir: Path | None = None


def read_csv(path: Path, fmt: CsvFormat) -> pd.DataFrame:
    """Read every column as text, trimmed; '' stays '' (missing markers are decided later)."""
    last_error: Exception | None = None
    for encoding in fmt.encodings:
        try:
            frame = pd.read_csv(
                path, sep=fmt.separator, dtype=str, encoding=encoding, keep_default_na=False
            )
        except UnicodeDecodeError as exc:
            last_error = exc
            continue
        frame.columns = [str(c).strip().lstrip("﻿") for c in frame.columns]
        for column in frame.columns:
            frame[column] = frame[column].str.strip()
        return frame
    msg = f"Cannot decode {path} with {fmt.encodings}"
    raise ValueError(msg) from last_error


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str) + "\n")


def evidence_dir(root: Path | None, dataset_id: str) -> Path | None:
    return root / date.today().isoformat() / dataset_id if root else None


def rel(path: Path) -> str:
    resolved = path.resolve()
    return (
        str(resolved.relative_to(REPO_ROOT))
        if resolved.is_relative_to(REPO_ROOT)
        else str(resolved)
    )


def schema_hash(frame: pd.DataFrame) -> str:
    import hashlib

    return hashlib.sha256(",".join(sorted(map(str, frame.columns))).encode()).hexdigest()
