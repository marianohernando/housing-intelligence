"""«Dónde buscar» (D-238): each municipio is in one part of the region, and so are the
districts and barrios of Madrid, by the start of their code."""

from collections import Counter

import pytest

from hi_contracts.public import SearchScope
from hi_domain.geo.scope import in_scope, scope_of
from hi_domain.geo.zoning_data import SCOPE_BY_MUNICIPIO


@pytest.mark.parametrize(
    ("code", "scope"),
    [
        ("28079", SearchScope.MADRID),
        ("2807920", SearchScope.MADRID),  # San Blas-Canillejas, a district
        ("28079201", SearchScope.MADRID),  # Simancas, a barrio
        ("28006", SearchScope.ALREDEDORES),  # Alcobendas (Norte Metropolitano)
        ("28092", SearchScope.ALREDEDORES),  # Móstoles (Sur Metropolitano)
        ("28013", SearchScope.ALREDEDORES),  # Aranjuez: metropolitan for the Institute
        ("28001", SearchScope.PUEBLOS),  # La Acebeda (Sierra Norte)
        ("28093", SearchScope.PUEBLOS),  # Navacerrada (Sierra Central)
    ],
)
def test_each_zone_is_in_the_part_its_municipio_is_in(code: str, scope: SearchScope) -> None:
    assert scope_of(code) is scope
    assert in_scope(code, scope)
    assert not any(in_scope(code, other) for other in SearchScope if other not in (scope, "all"))


def test_the_whole_region_keeps_every_zone_even_one_the_zoning_does_not_list() -> None:
    assert scope_of("28999") is None
    assert in_scope("28999", SearchScope.ALL)
    assert not in_scope("28999", SearchScope.PUEBLOS)


def test_the_179_municipios_are_one_capital_40_around_it_and_138_villages() -> None:
    assert Counter(SCOPE_BY_MUNICIPIO.values()) == {"madrid": 1, "alrededores": 40, "pueblos": 138}
    assert SCOPE_BY_MUNICIPIO["28079"] == "madrid"
    assert all(len(code) == 5 and code.startswith("28") for code in SCOPE_BY_MUNICIPIO)
