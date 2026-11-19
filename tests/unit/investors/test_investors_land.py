"""D-248 with line A's planning areas (D-247): an area that also covers other barrios counts whole
in the barrio of a point inside it, and says so in its note; the sheet carries the note and the
sum says how many such areas it includes (review of #95). No database."""

from datetime import date
from typing import Any

from hi_api.services.investors import (
    BARRIO,
    REMAINING,
    Place,
    Sources,
    land_block,
    shared_areas,
)

PLACE = Place("28079164", "2807916")
NOTE = "El ámbito ocupa también otros barrios: aquí está el 32 % de su superficie."


def _row(items: list[dict[str, Any]] | None) -> dict[str, Any]:
    return {
        "feature_id": REMAINING,
        "territory_level": BARRIO.value,
        "territory_code": PLACE.code,
        "value": sum(i["value"] for i in items or []) if items is not None else None,
        "null_reason": None,
        "confidence": 1.0,
        "period_start": date(2026, 7, 1),
        "inputs": {"detail": {"items": items}, "dataset_versions": {}},
        "unit": "m2",
    }


def _block(items: list[dict[str, Any]] | None) -> Any:
    values = {(REMAINING, BARRIO.value, PLACE.code): _row(items)}
    return land_block(values, PLACE, Sources({}))


def test_a_shared_area_carries_its_note_and_the_sum_says_it() -> None:
    items = [
        {
            "code": "APE.16.01",
            "name": "Un ámbito",
            "value": 12000.0,
            "note": NOTE,
            "use": "colectiva",
        },
        {"code": "APE.16.02", "name": "Otro ámbito", "value": 3000.0},
    ]
    block = _block(items)
    shared = next(i for i in block.remaining if i.code == "APE.16.01")
    assert shared.note == NOTE
    assert shared.use == "colectiva"
    assert next(i for i in block.remaining if i.code == "APE.16.02").note is None
    assert block.remaining_m2.value == 15000.0
    assert "Incluye 1 ámbito que ocupa también otros barrios: cuenta entero aquí" in (
        block.remaining_m2.source.text
    )
    assert shared_areas(_row(items)) == 1


def test_without_shared_areas_the_sum_says_nothing_more() -> None:
    block = _block([{"code": "APE.16.02", "name": "Otro ámbito", "value": 3000.0}])
    assert "otros barrios" not in block.remaining_m2.source.text
    assert shared_areas(_row([])) == 0
    assert shared_areas(None) is None
