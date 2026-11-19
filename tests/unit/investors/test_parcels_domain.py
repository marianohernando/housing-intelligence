"""D-250: the pure rules of the search by parcel (hi_domain.parcels, hi_domain.zonal_norms)."""

import pytest

from hi_contracts.pro.investors import BuildabilityKind, PlanningKind, UseClass, UseOwnership
from hi_domain.parcels import (
    AREA_PLAN,
    DOTACIONAL,
    NO_PLANNING,
    NON_BUILDABLE,
    RUSTIC,
    OfficialFigure,
    Unit,
    ZoneCode,
    ambit_state,
    catastro_number,
    classify_planning,
    classify_use,
    in_madrid_bbox,
    initial_buildability,
    is_vacant,
    normalize_rc,
    parcel_cautions,
    parse_address,
    plan_use,
    same_street,
    street_address,
    summarize_units,
    typed_number,
)
from hi_domain.zonal_norms import BOCM_2023_URL, REFUNDIDO_URL, RULES, coefficient_area

VEDA = OfficialFigure(13121.0, "VEDA Madrid", "ayto_veda_parcelas")
PORTAL = OfficialFigure(516.6, "Portal del Suelo 4.0", "cm_parcelas_portal_suelo")


@pytest.mark.parametrize(
    ("typed", "rc14"),
    [
        ("2122202VK4722A", "2122202VK4722A"),
        ("2122202vk4722a", "2122202VK4722A"),
        (" 9943003 VK3794D ", "9943003VK3794D"),
        ("9943003-VK3794D-0001", "9943003VK3794D"),
        ("9943003VK3794D0001ZO", "9943003VK3794D"),
    ],
)
def test_a_reference_gives_its_parcel(typed: str, rc14: str) -> None:
    assert normalize_rc(typed) == rc14


@pytest.mark.parametrize(
    "typed", ["", "2122202VK4722", "2122202VK4722A0", "9943003VK3794D0001Z", "2122202VK4722Ñ"]
)
def test_a_malformed_reference_is_refused(typed: str) -> None:
    with pytest.raises(ValueError, match="14, 18 or 20"):
        normalize_rc(typed)


def test_the_bbox_is_madrid_capital() -> None:
    assert in_madrid_bbox(40.4768, -3.6497)  # Pinar del Rey
    assert not in_madrid_bbox(40.3, -3.0)  # Alcalá de Henares side
    assert not in_madrid_bbox(-3.6497, 40.4768)  # lat and lon swapped


@pytest.mark.parametrize(
    ("code", "kind", "zone"),
    [
        ("8.3.a", PlanningKind.NORMA_ZONAL, ZoneCode(8, 3, "a")),
        ("4", PlanningKind.NORMA_ZONAL, ZoneCode(4, None, None)),
        ("1.2", PlanningKind.NORMA_ZONAL, ZoneCode(1, 2, None)),
        ("9.4.b", PlanningKind.NORMA_ZONAL, ZoneCode(9, 4, "b")),
        ("APR.02.06", PlanningKind.APR, None),
        ("APE.19.08", PlanningKind.APE, None),
        ("API.16.10", PlanningKind.API, None),
        ("UZPp.02.04-RP", PlanningKind.UZP, None),
        ("UZI.0.07", PlanningKind.UZI, None),
        ("NUP.1", PlanningKind.NUP, None),
        ("AOE.00.06", PlanningKind.AOE, None),
        ("12", PlanningKind.OTRO, None),
        ("SG", PlanningKind.OTRO, None),
    ],
)
def test_planning_codes_are_classified(
    code: str, kind: PlanningKind, zone: ZoneCode | None
) -> None:
    assert classify_planning(code) == (kind, zone)


def test_a_plot_with_nothing_built_is_a_solar() -> None:
    vacant = "Obras de urbanización y jardineria, suelos sin edificar"
    assert is_vacant(vacant, 0, has_constructions=False) is True
    assert is_vacant("OBRAS DE URBANIZACIÓN Y JARDINERÍA, SUELOS SIN EDIFICAR", None, False)
    assert is_vacant(None, 0, has_constructions=False) is True
    assert is_vacant("Residencial", 1207, has_constructions=True) is False
    assert is_vacant("Industrial", 0, has_constructions=True) is False
    assert is_vacant(None, None, has_constructions=False) is None


def test_catastro_numbers() -> None:
    assert catastro_number("1207") == 1207
    assert catastro_number("100,000000") == 100
    assert catastro_number("1.016,5") == 1016.5
    assert catastro_number(444893.09) == pytest.approx(444893.09)
    assert catastro_number("444893.09") == pytest.approx(444893.09)
    assert catastro_number("") is None
    assert catastro_number(None) is None
    assert catastro_number("n/a") is None


def test_units_are_summarised_by_use_never_one_by_one() -> None:
    units = [Unit("Comercial", 62, 1890)] + [Unit("Residencial", m2, 1890) for m2 in (66,) * 4]
    units.append(Unit("Residencial", 50, 1895))
    summary = summarize_units(units)
    assert summary.total == 6
    assert [(g.use, g.count, g.built_m2) for g in summary.by_use] == [
        ("Residencial", 5, 314),
        ("Comercial", 1, 62),
    ]
    assert summary.built_m2 == 376
    assert summary.year_built == 1890
    assert summary.main_use == "Residencial"


def test_units_without_area_or_use() -> None:
    summary = summarize_units([Unit(None, None, None), Unit(None, None, None)])
    assert summary.total == 2 and summary.built_m2 is None and summary.main_use is None
    assert summary.by_use[0].use == "Sin uso declarado"


def test_addresses_are_built_from_their_parts_without_floor_or_door() -> None:
    assert (
        street_address("CL", "MENDEZ ALVARO", "47", "28045")
        == "Calle Mendez Alvaro 47, 28045 Madrid"
    )
    albufera = street_address("AV", "DE LA ALBUFERA", "0005", None)
    assert albufera == "Avenida de la Albufera 5, Madrid"
    assert street_address("CL", None, "1", "28013") is None


@pytest.mark.parametrize(
    ("typed", "expected"),
    [
        ("calle mayor 61, madrid", ("CL", "MAYOR", 61)),
        ("Avda. de la Albufera 5", ("AV", "DE LA ALBUFERA", 5)),
        ("Méndez Álvaro 47, 28045 Madrid", ("CL", "MENDEZ ALVARO", 47)),
        ("PZ España 1", ("PZ", "ESPANA", 1)),
    ],
)
def test_typed_addresses_for_the_street_index(typed: str, expected: tuple[str, str, int]) -> None:
    parsed = parse_address(typed)
    assert parsed is not None
    assert (parsed.street_type, parsed.street, parsed.number) == expected


def test_an_address_without_number_is_not_parsed() -> None:
    assert parse_address("calle mayor") is None
    assert parse_address("61") is None
    assert typed_number("calle mayor, 28013") is None
    assert typed_number("mendez alvaro 47, 28045") == 47


# --- The table of the normas zonales ---


def test_only_nz_5_7_8_and_9_give_a_coefficient_and_every_rule_cites_its_page() -> None:
    assert sorted(nz for nz, rule in RULES.items() if rule.coefficients) == [5, 7, 8, 9]
    for rule in RULES.values():
        assert rule.article.number.startswith(f"8.{rule.nz}.")
        assert rule.article.url.endswith(f"#page={rule.article.page}")
        assert rule.coefficients or rule.none_reason
    assert RULES[1].article.url.startswith(BOCM_2023_URL)
    assert RULES[8].article.url.startswith(REFUNDIDO_URL)


@pytest.mark.parametrize(
    ("nz", "grado", "area", "expected"),
    [
        (5, 1, 1000, 2000),
        (7, 2, 1000, 500),
        (8, 3, 502, 351.4),
        (8, 4, 100, 100),
        (8, 6, 400, 280),
        (8, 6, 800, 0.7 * 500 + 0.5 * 300),
        (9, 3, 1000, 1600),
        (9, 5, 1000, 2000),
    ],
)
def test_coefficients_of_the_articles(nz: int, grado: int, area: float, expected: float) -> None:
    assert coefficient_area(nz, grado, area) == pytest.approx(expected)


def test_no_coefficient_without_grado_or_in_other_zones() -> None:
    assert coefficient_area(4, 1, 1000) is None
    assert coefficient_area(8, 9, 1000) is None
    assert coefficient_area(12, 1, 1000) is None


# --- Buildability by priority ---


def test_veda_wins_and_needs_no_assumption() -> None:
    result = initial_buildability(
        area_m2=2843, planning_code="APR.02.06", use="RESIDENCIAL", rustic=False, official=[VEDA]
    )
    assert result.kind is BuildabilityKind.OFICIAL
    assert result.value_m2 == 13121 and result.source == "VEDA Madrid"
    assert result.note is None and result.assumed_m2 is None
    assert result.dataset_ids == ("ayto_veda_parcelas",)


def test_an_official_figure_wins_and_the_norm_goes_in_the_note() -> None:
    result = initial_buildability(
        area_m2=502, planning_code="8.3.a", use="RESIDENCIAL", rustic=False, official=[PORTAL]
    )
    assert result.kind is BuildabilityKind.OFICIAL and result.value_m2 == 516.6
    assert result.assumed_m2 == pytest.approx(351.4)
    assert result.note is not None and "351" in result.note
    assert "manda la cifra oficial" in result.note


def test_the_coefficient_of_the_norma_zonal_is_an_assumption_with_its_article() -> None:
    result = initial_buildability(
        area_m2=502, planning_code="8.3.a", use="RESIDENCIAL VIVIENDA UNIFAMILIAR", rustic=False
    )
    assert result.kind is BuildabilityKind.SUPUESTO
    assert result.value_m2 == pytest.approx(351.4)
    assert result.coefficient == pytest.approx(0.7)
    assert result.article == "8.8.9"
    assert result.article_url is not None and result.article_url.endswith("#page=375")
    assert result.formula == "0,7 m²/m² × 502 m² de parcela"
    assert result.source.startswith("Supuesto: norma zonal 8 grado 3º, art. 8.8.9")


def test_nz1_is_area_times_z_times_c_and_approximate() -> None:
    result = initial_buildability(
        area_m2=68, planning_code="1.2", use="RESIDENCIAL", rustic=False, coef_z=5
    )
    assert result.kind is BuildabilityKind.SUPUESTO
    assert result.value_m2 == pytest.approx(68 * 5 * 0.66)
    assert result.source.startswith("Supuesto aproximado")
    assert result.formula == "68 m² de parcela × Z 5 × C 0,66"
    assert result.note is not None and result.note.startswith("Aproximado")
    without_z = initial_buildability(area_m2=68, planning_code="1.2", use=None, rustic=False)
    assert without_z.kind is BuildabilityKind.SIN_DATO and without_z.article == "8.1.10"
    grade_5 = initial_buildability(
        area_m2=68, planning_code="1.5", use=None, rustic=False, coef_z=5
    )
    assert grade_5.kind is BuildabilityKind.SIN_DATO


@pytest.mark.parametrize(
    ("code", "use", "rustic", "source"),
    [
        ("4", "RESIDENCIAL VIVIENDA COLECTIVA", False, RULES[4].none_reason),
        ("2", None, False, RULES[2].none_reason),
        ("APR.04.09", "SIN USO PORMENORIZADO", False, AREA_PLAN),
        ("NUP.1", "SIN USO PORMENORIZADO", False, NON_BUILDABLE),
        ("5.1", "DOTACIONAL ZONAS VERDES BARRIO BÁSICO", False, DOTACIONAL),
        ("APR.16.04", "DOTACIONAL ZONAS VERDES BARRIO BÁSICO", False, DOTACIONAL),
        (None, None, False, NO_PLANNING),
        ("8.3.a", None, True, RUSTIC),
    ],
)
def test_without_a_figure_the_person_types_it(
    code: str | None, use: str | None, rustic: bool, source: str | None
) -> None:
    result = initial_buildability(area_m2=601, planning_code=code, use=use, rustic=rustic)
    assert result.kind is BuildabilityKind.SIN_DATO
    assert result.value_m2 is None
    assert result.source == source


def test_nz4_cites_its_article() -> None:
    result = initial_buildability(area_m2=601, planning_code="4", use=None, rustic=False)
    assert result.article == "8.4.9"
    assert result.article_url is not None and result.article_url.endswith("#page=349")


def test_a_fuzzy_street_is_not_the_typed_one() -> None:
    # The geocoder matched «calle abegondo 1» with «BEGONIAS 1» (spike §9): never the same street
    assert not same_street("calle abegondo 1", "CALLE BEGONIAS 1, Madrid")
    assert same_street("calle mayor 61", "CALLE MAYOR 61, Madrid")
    assert same_street("Méndez Álvaro 47, 28045", "Calle Mendez Alvaro 47, Madrid")
    assert same_street("c/ mayor 61", "Calle de Mayor 61, Madrid")  # type and particles aside
    assert not same_street("calle mayor 61", "CALLE MAYO 61, Madrid")
    assert not same_street("61", "CALLE MAYOR 61, Madrid")  # no street typed


def test_a_residential_official_figure_wins_over_one_of_other_uses() -> None:
    industrial = OfficialFigure(3465.3, "VEDA Madrid", "ayto_veda_parcelas", "INDUSTRIAL")
    housing = OfficialFigure(
        800.0, "Portal del Suelo 4.0", "cm_parcelas_portal_suelo", "Residencial"
    )
    result = initial_buildability(
        area_m2=4000,
        planning_code="APE.20.10",
        use=None,
        rustic=False,
        official=[industrial, housing],
    )
    assert result.kind is BuildabilityKind.OFICIAL and result.value_m2 == 800
    assert result.dataset_ids == ("ayto_veda_parcelas", "cm_parcelas_portal_suelo")


def test_an_official_figure_of_other_uses_only_is_a_reference() -> None:
    industrial = OfficialFigure(3465.3, "VEDA Madrid", "ayto_veda_parcelas", "INDUSTRIAL")
    result = initial_buildability(
        area_m2=4000, planning_code="9.3", use="INDUSTRIAL", rustic=False, official=[industrial]
    )
    assert result.kind is BuildabilityKind.SIN_DATO and result.value_m2 is None
    assert "3.465 m² edificables de uso industrial, no residencial" in result.source
    assert result.dataset_ids == ("ayto_veda_parcelas",)


# --- D-252: uses ---


@pytest.mark.parametrize(
    ("use", "kind", "owner"),
    [
        ("RESIDENCIAL VIVIENDA COLECTIVA  ", UseClass.RESIDENCIAL, None),
        (
            "RESIDENCIAL VIVIENDA COLECTIVA PROTECCIÓN PÚBLICA",
            UseClass.RESIDENCIAL,
            None,
        ),
        ("Residencial", UseClass.RESIDENCIAL, None),
        ("SERVICIOS TERCIARIOS OFICINAS", UseClass.TERCIARIO, None),
        ("SERVICIOS TERCIARIO OFICINAS", UseClass.TERCIARIO, None),
        ("TERCIARIO COMERCIAL", UseClass.TERCIARIO, None),
        ("Terciario", UseClass.TERCIARIO, None),
        ("INDUSTRIAL", UseClass.INDUSTRIAL, None),
        ("INDUSTRIA INDUSTRIA TRADICIONAL", UseClass.INDUSTRIAL, None),
        ("DOTACIONAL EQUIPAMIENTO PRIVADO EDUCATIVO", UseClass.DOTACIONAL, UseOwnership.PRIVADO),
        ("DOTACIONAL EQUIPAMIENTO PÚBLICO SALUD BÁSICO", UseClass.DOTACIONAL, UseOwnership.PUBLICO),
        ("DOTACIONAL ADMINISTRACIÓN PÚBLICA", UseClass.DOTACIONAL, UseOwnership.PUBLICO),
        ("DOTACIONAL DEPORTIVO", UseClass.DOTACIONAL, None),
        ("DOTACIONAL ZONAS VERDES BARRIO BÁSICO", UseClass.ZONA_VERDE, None),
        ("DOTACIONAL VÍA PÚBLICA PRINCIPAL", UseClass.INFRAESTRUCTURA, None),
        ("DOTACIONAL TRANSPORTE FERROVIARIO", UseClass.INFRAESTRUCTURA, None),
        (
            "DOTACIONAL SERVICIOS INFRAESTRUCTURALES PRIVADO GAS",
            UseClass.INFRAESTRUCTURA,
            UseOwnership.PRIVADO,
        ),
        ("SIN USO PORMENORIZADO", UseClass.SIN_USO, None),
        ("Otros", UseClass.OTRO, None),
    ],
)
def test_uses_are_classified_with_their_ownership(
    use: str, kind: UseClass, owner: UseOwnership | None
) -> None:
    assert classify_use(use) == (kind, owner)


def test_no_use_is_no_class() -> None:
    assert classify_use(None) == (None, None)
    assert classify_use("  ") == (None, None)


def test_every_official_figure_goes_by_use_and_none_is_split() -> None:
    industrial = OfficialFigure(3465.3, "VEDA Madrid", "ayto_veda_parcelas", "INDUSTRIAL")
    housing = OfficialFigure(
        800.0, "Portal del Suelo 4.0", "cm_parcelas_portal_suelo", "Residencial"
    )
    result = initial_buildability(
        area_m2=4000,
        planning_code="APE.20.10",
        use=None,
        rustic=False,
        official=[industrial, housing],
    )
    assert [(f.use_class, f.value_m2, f.residential) for f in result.by_use] == [
        (UseClass.INDUSTRIAL, 3465.3, False),
        (UseClass.RESIDENCIAL, 800.0, True),
    ]
    only_industrial = initial_buildability(
        area_m2=4000, planning_code="9.3", use=None, rustic=False, official=[industrial]
    )
    assert only_industrial.value_m2 is None and len(only_industrial.by_use) == 1
    assumed = initial_buildability(area_m2=502, planning_code="8.3.a", use=None, rustic=False)
    assert assumed.by_use == ()


# --- D-252 (audit): the plan by use, the state of the area and the cautions ---


def test_the_plan_gives_m2_or_m2_per_m2_by_use() -> None:
    housing = plan_use("RESIDENCIAL VIVIENDA COLECTIVA  ", 60230.88, "m²", True, 16600.2)
    assert housing is not None
    assert (housing.use, housing.use_class, housing.value_m2) == (
        "RESIDENCIAL VIVIENDA COLECTIVA",
        UseClass.RESIDENCIAL,
        60230.88,
    )
    assert housing.principal and not housing.assumed and housing.coefficient is None
    offices = plan_use("SERVICIOS TERCIARIOS", 1.2, "m²/m²", False, 1000.0)
    assert offices is not None and offices.assumed and offices.coefficient == 1.2
    assert offices.value_m2 == pytest.approx(1200.0)
    assert plan_use("SERVICIOS TERCIARIOS", 1.2, "m²/m²", False, None).value_m2 is None  # type: ignore[union-attr]
    assert plan_use("RESIDENCIAL", None, "m²", True, 100.0) is None  # the plan publishes none
    assert plan_use(None, 10.0, "m²", True, 100.0) is None


@pytest.mark.parametrize(
    ("code", "found", "pending"),
    [
        ("APR.04.09", "APR.04.09", True),  # all four phases «Sin Iniciar»
        ("APR.02.06", "APR.02.06", False),  # all «Finalizado»
        ("UZPP.02.04-RP", "UZPp.02.04-RP", True),  # other case; works «En Ejecución»
        ("APE.01.03", "APE.01.03/M", False),  # without its suffix, a single match
    ],
)
def test_the_state_of_an_area_is_found_by_its_code(code: str, found: str, pending: bool) -> None:
    state = ambit_state(code)
    assert state is not None and state.code == found and state.tracked
    assert state.pending is pending


def test_a_norma_zonal_has_no_area_and_an_untracked_area_says_so() -> None:
    assert ambit_state("8.3.a") is None
    assert ambit_state(None) is None
    centre = ambit_state("APE.00.01")  # the historic centre: the Ayuntamiento does not follow it
    assert centre is not None and not centre.tracked and not centre.pending


def test_an_official_figure_in_an_area_not_finished_is_a_reference() -> None:
    """Almería 1 (APR.04.09): 32.697 m² of the Portal del Suelo, but nothing started."""
    portal = OfficialFigure(
        32697.0, "Portal del Suelo 4.0", "cm_parcelas_portal_suelo", "Residencial"
    )
    result = initial_buildability(
        area_m2=20059,
        planning_code="APR.04.09",
        use="SIN USO PORMENORIZADO",
        rustic=False,
        official=[portal],
        ambit=ambit_state("APR.04.09"),
    )
    assert result.value_m2 is None and result.kind is BuildabilityKind.SIN_DATO
    assert "32.697 m² edificables de vivienda" in result.source
    assert "APR.04.09 no está terminado" in result.source
    assert len(result.by_use) == 1
    done = initial_buildability(
        area_m2=5000,
        planning_code="APR.02.06",
        use="RESIDENCIAL VIVIENDA COLECTIVA",
        rustic=False,
        official=[VEDA],
        ambit=ambit_state("APR.02.06"),
    )
    assert done.kind is BuildabilityKind.OFICIAL and done.value_m2 == 13121.0


def test_a_norm_assumption_for_another_use_is_never_housing() -> None:
    """NZ 9 with an industrial use: the coefficient gives m² of that use, not of housing."""
    result = initial_buildability(
        area_m2=63244, planning_code="9.4.a", use="INDUSTRIAL", rustic=False
    )
    assert result.value_m2 is None and result.kind is BuildabilityKind.SIN_DATO
    assert result.assumed_m2 is not None and result.assumed_m2 > 0
    assert "de uso industrial, no de vivienda" in result.source
    housing = initial_buildability(
        area_m2=502, planning_code="8.3.a", use="RESIDENCIAL VIVIENDA UNIFAMILIAR", rustic=False
    )
    assert housing.kind is BuildabilityKind.SUPUESTO


def test_the_cautions_say_what_the_figures_are_not() -> None:
    keys = [k for k, _ in parcel_cautions("INDUSTRIAL", [], None)]
    assert keys == ["otro_uso"]
    pending = dict(parcel_cautions("SIN USO PORMENORIZADO", [], ambit_state("APR.04.09")))
    text = pending["ambito_pendiente"]
    assert text.startswith("El ámbito APR.04.09 no está terminado según el Ayuntamiento")
    assert "obras de urbanización sin iniciar" in text and "arts. 18.2.c, 18.2.d y 21.1" in text
    protected = OfficialFigure(9692.0, "VEDA", "x", "RESIDENCIAL VIVIENDA COLECTIVA PROTEGIDA")
    keys = [k for k, _ in parcel_cautions("RESIDENCIAL VIVIENDA COLECTIVA", [protected], None)]
    assert keys == ["vivienda_protegida"]
    assert (
        "Decreto 74/2009"
        in dict(parcel_cautions("RESIDENCIAL PROTECCIÓN OFICIAL", [], None))["vivienda_protegida"]
    )
    assert [k for k, _ in parcel_cautions("RESIDENCIAL VIVIENDA UNIFAMILIAR", [], None)] == [
        "unifamiliar"
    ]
    assert parcel_cautions("RESIDENCIAL VIVIENDA COLECTIVA", [], ambit_state("APR.02.06")) == []
