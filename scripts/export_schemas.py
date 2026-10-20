"""Write JSON Schemas for catalog YAML files from the Pydantic contracts.

Usage: uv run python scripts/export_schemas.py [--check]
"""

import json
import sys
from pathlib import Path

from pydantic import BaseModel

from hi_contracts.catalog import DatasetSpec, FeatureSpec, SourceSpec

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "schemas"
MODELS: dict[str, type[BaseModel]] = {
    "source": SourceSpec,
    "dataset": DatasetSpec,
    "feature": FeatureSpec,
}


def render(name: str, model: type[BaseModel]) -> str:
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
