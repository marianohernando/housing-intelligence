"""Write JSON Schemas from the Pydantic contracts: catalog YAML files and API payloads.

API schemas (data/schemas/api/) are what the web generates its TypeScript types from.
Usage: uv run python scripts/export_schemas.py [--check]
"""

import json
import sys
from pathlib import Path

from pydantic import BaseModel, TypeAdapter

from hi_contracts.api.envelope import ErrorEnvelope
from hi_contracts.catalog import DatasetSpec, FeatureSpec, MetricSpec, PipelineSpec, SourceSpec
from hi_contracts.public import ScenarioState
from hi_contracts.public.responses import (
    DatasetListResponse,
    GapRowMapResponse,
    PlacesResponse,
    SearchResponse,
    ZoneGapListResponse,
)

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "schemas"
MODELS: dict[str, type[BaseModel] | TypeAdapter[object]] = {
    "source": SourceSpec,
    "dataset": DatasetSpec,
    "feature": FeatureSpec,
    "metric": MetricSpec,
    "pipeline": TypeAdapter(PipelineSpec),
    "api/scenario_state": ScenarioState,
    "api/search_response": SearchResponse,
    "api/zone_gap_list_response": ZoneGapListResponse,
    "api/gap_row_map_response": GapRowMapResponse,
    "api/dataset_list_response": DatasetListResponse,
    "api/places_response": PlacesResponse,
    "api/error_response": ErrorEnvelope,
}


def render(name: str, model: type[BaseModel] | TypeAdapter[object]) -> str:
    if isinstance(model, TypeAdapter):
        schema = model.json_schema(by_alias=True)
    else:
        schema = model.model_json_schema(by_alias=True)
    schema["$schema"] = "https://json-schema.org/draft/2020-12/schema"
    schema["$id"] = f"https://housing-intelligence/schemas/{name}.schema.json"
    return json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def main() -> int:
    check = "--check" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stale: list[str] = []
    for name, model in MODELS.items():
        path = OUT_DIR / f"{name}.schema.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        content = render(name, model)
        if check:
            if not path.exists() or path.read_text() != content:
                stale.append(path.name)
        else:
            path.write_text(content)
            print("wrote", path.relative_to(OUT_DIR.parents[1]))
    if stale:
        print("stale schemas (run make schemas):", stale)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
