"""data/schemas/*.json must match the Pydantic contracts (run `make schemas`)."""

import importlib.util
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_json_schemas_are_up_to_date() -> None:
    spec = importlib.util.spec_from_file_location(
        "export_schemas", REPO_ROOT / "scripts" / "export_schemas.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name, model in module.MODELS.items():
        path = REPO_ROOT / "data" / "schemas" / f"{name}.schema.json"
        assert path.read_text() == module.render(name, model), f"{path.name} is stale: make schemas"
