"""Load the versioned place corrections (D-218 §10) and add the file to a run's inputs."""

import hashlib
from datetime import UTC, datetime
from pathlib import Path

import yaml

from hi_contracts.catalog.corrections import PlaceCorrection, PlaceCorrections
from hi_ingestion.bronze import REPO_ROOT
from hi_ingestion.pipelines.fetch import FetchedFile

CORRECTIONS_FILE = REPO_ROOT / "data" / "catalog" / "corrections" / "places.yaml"
ROLE = "corrections"


def load_corrections(path: Path = CORRECTIONS_FILE) -> PlaceCorrections:
    if not path.exists():
        return PlaceCorrections(corrections=[])
    return PlaceCorrections.model_validate(yaml.safe_load(path.read_text()) or {"corrections": []})


def corrections_input(dataset_id: str, path: Path = CORRECTIONS_FILE) -> FetchedFile:
    """The corrections file as an input of the register's run: a change reprocesses it."""
    content = path.read_bytes()
    modified = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).isoformat()
    return FetchedFile(
        dataset_id=dataset_id,
        role=ROLE,
        path=path,
        sha256=hashlib.sha256(content).hexdigest(),
        bytes=len(content),
        url=path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else str(path),
        retrieved_at=modified,
    )


def correction_attribute(correction: PlaceCorrection) -> dict[str, object]:
    """What the place says about it: corrected, how and from which official source."""
    return {
        "kind": "address" if correction.address else "directory",
        "reason": correction.reason,
        "source": correction.source.publisher,
        "url": str(correction.source.url),
        "consulted": correction.source.consulted.isoformat(),
    }
