"""D-252c: hi_domain.plan_uses_data is what scripts/export_investor_data.py renders from the
versioned tables (the same check as `export_investor_data.py --check` in `make lint`)."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_the_plan_uses_module_is_generated_from_the_versioned_tables() -> None:
    spec = importlib.util.spec_from_file_location(
        "export_investor_data", ROOT / "scripts" / "export_investor_data.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    rendered = module.render_plan_uses(
        module.PLAN_FIGURES_SOURCE, module.PLAN_PARCELS_SOURCE, module.PLAN_USE_NAMES_SOURCE
    )
    assert module.PLAN_USES_TARGET.read_text() == rendered
    assert "68695: (" in rendered and "AS_OF = " in rendered
