"""Buildability of the normas zonales of Madrid's Plan General (PGOUM 97), Título 8 of its
Normas Urbanísticas (NNUU): the versioned table the parcel search (D-250) assumes from.

Text used: the consolidated NNUU of the Dirección General de Planeamiento (June 2022, file
135-2021-00796), checked against the articles the final approval changed (BOCM 27-11-2023, nº 282,
anuncio 34): 8.5.8, 8.8.9 and 8.9.9 did not change; 8.7.9 changed but keeps its coefficients;
8.1.10 changed and is read from the BOCM. Later corrections are not reviewed. Pages are the PDF's
physical pages, for `#page=` links.

Only NZ 5, 7, 8 and 9 give a coefficient per grado in their text; NZ 1 gives a formula
(E = S × Z × C, Z from the 1997 plan of building conditions). The others give none: the
buildability is that of the type of building, the street width or a plan, and the person types it.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

NNUU_VERSION = "nnuu-pgoum97-refundido-2022-bocm-2023-11-27"
REFUNDIDO_URL = (
    "https://transparencia.madrid.es/UnidadesDescentralizadas/UrbanismoyVivienda/Urbanismo/"
    "Transparencia/Planeamiento%20urban%C3%ADstico/PUInformacionPublica/Planeamiento/Ficheros/"
    "3.%20Refundido%20de%20las%20normas%20urban%C3%ADsticas.pdf"
)
BOCM_2023_URL = "https://www.bocm.es/boletin/CM_Orden_BOCM/2023/11/27/BOCM-20231127-34.PDF"
NNUU_CITATION = (
    "Normas Urbanísticas del PGOUM 1997 (refundido de la Dirección General de Planeamiento; "
    "BOCM 27-11-2023)"
)


@dataclass(frozen=True)
class Article:
    """An article of the NNUU and the page of the official PDF that has it."""

    number: str
    page: int
    in_bocm: bool = False

    @property
    def url(self) -> str:
        return f"{BOCM_2023_URL if self.in_bocm else REFUNDIDO_URL}#page={self.page}"


@dataclass(frozen=True)
class ZoneRule:
    """One norma zonal: its name, the article on its buildability and, when its text gives
    them, the m² buildable per m² of parcel by grado. `none_reason` says why there is none."""

    nz: int
    name: str
    article: Article
    coefficients: Mapping[int, float] = field(default_factory=dict[int, float])
    none_reason: str | None = None


# NZ 8 grado 6º: 0,7 m²/m² up to 500 m² of parcel and 0,5 on what exceeds it (art. 8.8.9.1.f)
NZ8_G6_LIMIT_M2 = 500.0
NZ8_G6_EXCESS = 0.5
# NZ 1: E = S × Z × C (art. 8.1.10, BOCM 2023); C by grado. Grado 5º keeps what is built.
NZ1_FACTORS: Mapping[int, float] = {1: 0.875, 2: 0.66, 3: 0.90, 4: 0.75}

RULES: Mapping[int, ZoneRule] = {
    1: ZoneRule(
        1,
        "Protección del Patrimonio Histórico",
        Article("8.1.10", 150, in_bocm=True),
        none_reason="La norma zonal 1 calcula la edificabilidad con el plano de condiciones de "
        "la edificación (Z) y un factor por grado (C); en el grado 5º es la existente.",
    ),
    2: ZoneRule(
        2,
        "Protección de Colonias Históricas",
        Article("8.2.15", 331),
        none_reason="La norma zonal 2 no fija un coeficiente: es la del tipo de edificio de la "
        "colonia, en su área de planeamiento específico.",
    ),
    3: ZoneRule(
        3,
        "Volumetría específica",
        Article("8.3.2", 333),
        none_reason="La norma zonal 3 no fija un coeficiente: es la de su ordenación específica "
        "o la existente.",
    ),
    4: ZoneRule(
        4,
        "Edificación en manzana cerrada",
        Article("8.4.9", 349),
        none_reason="La norma zonal 4 no fija un coeficiente: sale del número de plantas según "
        "el ancho de la calle y del fondo edificable.",
    ),
    5: ZoneRule(
        5,
        "Edificación en bloques abiertos",
        Article("8.5.8", 355),
        {1: 2.0, 2: 1.6, 3: 1.4},
    ),
    6: ZoneRule(
        6,
        "Edificación en cascos anexionados",
        Article("8.6.11", 362),
        none_reason="La norma zonal 6 no fija un coeficiente: sale de la altura y el fondo de "
        "cada área de planeamiento específico.",
    ),
    7: ZoneRule(
        7,
        "Edificación en baja densidad",
        Article("8.7.9", 367),
        {1: 0.8, 2: 0.5, 3: 0.7},
    ),
    8: ZoneRule(
        8,
        "Edificación en vivienda unifamiliar",
        Article("8.8.9", 375),
        {1: 0.3, 2: 0.5, 3: 0.7, 4: 1.0, 5: 0.8, 6: 0.7},
    ),
    9: ZoneRule(
        9,
        "Actividades económicas",
        Article("8.9.9", 386),
        {1: 2.4, 2: 2.4, 3: 1.6, 4: 2.4, 5: 2.0},
    ),
    10: ZoneRule(
        10,
        "Ejes terciarios",
        Article("8.10.1", 392),
        none_reason="La norma zonal 10 se superpone a otra y no cambia su edificabilidad.",
    ),
    11: ZoneRule(
        11,
        "Remodelación",
        Article("8.11.2", 394),
        none_reason="La norma zonal 11 remite a un plan especial o a un estudio de detalle.",
    ),
}


def coefficient_area(nz: int, grado: int, area_m2: float) -> float | None:
    """m² buildable on `area_m2` of parcel by the coefficient of its norma zonal and grado; None
    when the norm gives no coefficient for it. NZ 8 grado 6º counts the excess over 500 m² at
    0,5."""
    rule = RULES.get(nz)
    coefficient = None if rule is None else rule.coefficients.get(grado)
    if coefficient is None:
        return None
    if nz == 8 and grado == 6 and area_m2 > NZ8_G6_LIMIT_M2:
        return coefficient * NZ8_G6_LIMIT_M2 + NZ8_G6_EXCESS * (area_m2 - NZ8_G6_LIMIT_M2)
    return coefficient * area_m2
