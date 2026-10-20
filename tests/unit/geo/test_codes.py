import pytest
from hypothesis import given
from hypothesis import strategies as st

from hi_domain.geo.codes import admin_unit_id, ine_municipality_from_cm


def test_madrid_cm_code_maps_to_ine() -> None:
    assert ine_municipality_from_cm("0796") == "28079"


@given(st.from_regex(r"^\d{4}$", fullmatch=True))
def test_cm_code_always_yields_madrid_ine_code(code: str) -> None:
    result = ine_municipality_from_cm(code)
    assert len(result) == 5
    assert result.startswith("28")
    assert result[2:] == code[:3]


@pytest.mark.parametrize("bad", ["079", "07961", "ABCD", ""])
def test_invalid_cm_codes_rejected(bad: str) -> None:
    with pytest.raises(ValueError, match="4 digits"):
        ine_municipality_from_cm(bad)


def test_admin_unit_ids() -> None:
    assert admin_unit_id("municipio", "28079") == "ES.28.MUN.28079"
    assert admin_unit_id("distrito", "2807901") == "ES.28.DIS.2807901"
    assert admin_unit_id("seccion_censal", "2807901001") == "ES.28.SEC.2807901001"


@pytest.mark.parametrize(
    ("level", "code"),
    [("municipio", "08019"), ("municipio", "2807"), ("barrio", "123"), ("distrito", "28079")],
)
def test_admin_unit_id_rejects_invalid(level: str, code: str) -> None:
    with pytest.raises(ValueError, match=r"(?i)invalid|unsupported"):
        admin_unit_id(level, code)
