"""Golden fixtures are synthetic, consistent and inside Comunidad de Madrid."""

import json
from pathlib import Path
from typing import Any

import h3
import yaml

from hi_domain.geo.bounds import is_within_madrid

GOLDEN = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "golden"
REQUIRED_PROFILES = {
    "golden_single",
    "golden_couple",
    "golden_family",
    "golden_senior",
    "golden_student",
    "golden_visual_accessibility",
    "golden_reduced_mobility",
    "golden_sensory_preferences",
}
PII_KEYS = {"name", "first_name", "surname", "email", "phone", "dni", "nie", "address", "iban"}
DIAGNOSIS_TERMS = {"autism", "autismo", "ciego", "blind", "tea", "tdah", "adhd", "discapacidad"}


def _profiles() -> list[dict[str, Any]]:
    return yaml.safe_load((GOLDEN / "user_profiles.yaml").read_text())["profiles"]


def _keys(obj: Any) -> set[str]:
    if isinstance(obj, dict):
        return set(obj) | {k for v in obj.values() for k in _keys(v)}
    if isinstance(obj, list):
        return {k for v in obj for k in _keys(v)}
    return set()


def test_required_profiles_present_and_unique() -> None:
    ids = [p["profile_id"] for p in _profiles()]
    assert len(ids) == len(set(ids))
    assert set(ids) >= REQUIRED_PROFILES


def test_profiles_contain_no_pii_fields() -> None:
    assert not (_keys(_profiles()) & PII_KEYS)


def test_sensitive_needs_are_explicit_needs_not_diagnoses() -> None:
    for profile in _profiles():
        for need in profile["sensitive_needs"]:
            assert need["consent"] == "explicit"
            assert not any(term in need["need"].lower().split("_") for term in DIAGNOSIS_TERMS)


def test_profile_anchors_inside_madrid() -> None:
    for profile in _profiles():
        for anchor in profile["anchors"]:
            assert is_within_madrid(anchor["lon"], anchor["lat"]), anchor["label"]


def test_golden_zones_h3_are_frozen_and_correct() -> None:
    zones = json.loads((GOLDEN / "madrid_zones.json").read_text())["zones"]
    assert len(zones) >= 5
    for zone in zones:
        assert is_within_madrid(zone["lon"], zone["lat"])
        assert zone["municipio_ine"].startswith("28")
        assert h3.latlng_to_cell(zone["lat"], zone["lon"], 8) == zone["expected_h3_r8"]
        assert h3.latlng_to_cell(zone["lat"], zone["lon"], 9) == zone["expected_h3_r9"]
        assert h3.cell_to_parent(zone["expected_h3_r9"], 8) == zone["expected_h3_r8"]


def test_golden_zones_have_frozen_sections() -> None:
    zones = json.loads((GOLDEN / "madrid_zones.json").read_text())["zones"]
    for zone in zones:
        code = zone["expected_seccion_censal"]
        assert code and len(code) == 10 and code.startswith(zone["municipio_ine"]), zone["zone_id"]
