"""Public parks OSM does not tag as parks, each with an official source (D-222 §5)."""

from pathlib import Path

import yaml

from hi_contracts.catalog.corrections import ParkInclusion, ParkInclusions
from hi_ingestion.bronze import REPO_ROOT

INCLUSIONS_FILE = REPO_ROOT / "data" / "catalog" / "corrections" / "parks.yaml"


def load_inclusions(path: Path = INCLUSIONS_FILE) -> ParkInclusions:
    if not path.exists():
        return ParkInclusions(parks=[])
    return ParkInclusions.model_validate(yaml.safe_load(path.read_text()) or {"parks": []})


def inclusion_attribute(inclusion: ParkInclusion) -> dict[str, object]:
    """What the park says about it: included, why and from which official source."""
    return {
        "reason": inclusion.reason,
        "source": inclusion.source.publisher,
        "url": str(inclusion.source.url),
        "consulted": inclusion.source.consulted.isoformat(),
    }
