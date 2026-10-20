import json
from pathlib import Path
from typing import Any

import pytest

from hi_ingestion.bronze import BronzeWriter

FIXTURES = Path(__file__).parent / "fixtures"


def load_fixture(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text())


@pytest.fixture
def bronze(tmp_path: Path) -> BronzeWriter:
    return BronzeWriter("catalog/test", "2026-10-20", root=tmp_path)
