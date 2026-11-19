"""The search by parcel of the investor version (D-250): pure rules, without I/O.

- The cadastral reference: 14 characters for the parcel (18 or 20 for one unit of it).
- The planning code of the Ayuntamiento (`AMB_TX_ETIQ` of «Urbanismo. Destino urbanístico del
  suelo»): a norma zonal with its grado and nivel («8.3.a», «1.2», «4») or a planning area
  («APR.02.06», «UZPp.02.04-RP», «NUP.1»).
- Whether a parcel is a plot with nothing built (solar), from the Catastro's use and built area.
- The units of a building in horizontal division, summarised by use (never floor and door).
- The buildable m² the calculator starts from, by priority: the official figure of the parcel
  (VEDA, then the Portal del Suelo), the coefficient of its norma zonal, the NZ 1 formula, or none.
  Always editable; an assumption says so and cites its article.
"""

import re
import unicodedata
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from hi_contracts.pro.investors import BuildabilityKind, PlanningKind
from hi_domain.gaps import es_number
from hi_domain.geo.bounds import BBox
from hi_domain.geo.names import LOWER_PARTICLES, title_case
from hi_domain.zonal_norms import NNUU_CITATION, NZ1_FACTORS, RULES, coefficient_area

PARCELS_VERSION = "parcels-0.1"
# The longest a lookup may take: past it, the Catastro counts as failed and the planning as not
# read (D-250, review R-06). «Cómo lo calculamos» says it (D-251).
LOOKUP_BUDGET_S = 15.0

# The municipio of Madrid (EPSG:4326), padded ~1 km: the cheap filter before PostGIS
MADRID_CITY_BBOX = BBox(min_lon=-3.90, min_lat=40.30, max_lon=-3.51, max_lat=40.65)
# Catastro codes of Madrid: province 28, INE municipio 079, Catastro municipio 900
MADRID_INE_MUNICIPIO = "79"
MADRID_CATASTRO_MUNICIPIO = "900"

_RC = re.compile(r"^([0-9A-Z]{14})(?:[0-9]{4}(?:[A-Z]{2})?)?$")
_RC_NOISE = re.compile(r"[\s.\-]")


def normalize_rc(raw: str) -> str:
    """The parcel's reference (14 characters) from what was typed: upper case, without spaces,
    dots or hyphens; 18 or 20 characters (a unit) give their parcel. ValueError otherwise."""
    match = _RC.fullmatch(_RC_NOISE.sub("", raw).upper())
    if match is None:
        msg = "a cadastral reference has 14, 18 or 20 letters and digits"
        raise ValueError(msg)
    return match.group(1)


def in_madrid_bbox(lat: float, lon: float) -> bool:
    return MADRID_CITY_BBOX.contains(lon, lat)


# --- Planning ---

_NZ = re.compile(r"^(\d{1,2})(?:\.(\d))?(?:\.([a-z]))?$")
_AREA_PREFIX = re.compile(r"^([A-Za-z]+)[.\s]")
_AREA_KINDS: Mapping[str, PlanningKind] = {
    "API": PlanningKind.API,
    "APE": PlanningKind.APE,
    "APR": PlanningKind.APR,
    "APD": PlanningKind.APD,
    "UZI": PlanningKind.UZI,
    "UZP": PlanningKind.UZP,
    "UZPP": PlanningKind.UZP,
    "UNP": PlanningKind.UNP,
    "NUP": PlanningKind.NUP,
    "AOE": PlanningKind.AOE,
}


@dataclass(frozen=True)
class ZoneCode:
    """A norma zonal read from its code: «8.3.a» is NZ 8, grado 3º, nivel a."""

    nz: int
    grado: int | None
    nivel: str | None


def classify_planning(code: str) -> tuple[PlanningKind, ZoneCode | None]:
    """What a planning code is. A norma zonal also comes back read; a planning area by its
    prefix (API, APE, APR, UZI, UZP and UZPp, NUP, AOE…); anything else is «otro»."""
    text = code.strip()
    if (match := _NZ.fullmatch(text)) is not None:
        nz = int(match.group(1))
        if nz in RULES:
            grado = int(match.group(2)) if match.group(2) else None
            return PlanningKind.NORMA_ZONAL, ZoneCode(nz, grado, match.group(3))
        return PlanningKind.OTRO, None
    prefix = _AREA_PREFIX.match(text)
    kind = _AREA_KINDS.get(prefix.group(1).upper()) if prefix else None
    return (kind or PlanningKind.OTRO), None


# --- The parcel ---

VACANT_USE = "suelos sin edificar"


def fold(text: str) -> str:
    """Lower case without accents, to compare the Catastro's words."""
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def is_vacant(use: str | None, built_m2: float | None, has_constructions: bool) -> bool | None:
    """A plot with nothing built: its use says «suelos sin edificar», or nothing is built and
    there is no construction. None when the Catastro says neither its use nor its area."""
    if use and VACANT_USE in fold(use):
        return True
    if use is None and built_m2 is None:
        return None
    return built_m2 == 0 and not has_constructions


def catastro_number(value: object) -> float | None:
    """«1207», «100,000000», «444893.09» or 1207 as a number; None when empty or not a number."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    text = str(value).strip()
    if "," in text:  # Spanish decimals: a dot before them is a thousands separator
        text = text.replace(".", "").replace(",", ".")
    try:
        return float(text) if text else None
    except ValueError:
        return None


@dataclass(frozen=True)
class Unit:
    """One unit of a building, as much as the sheet needs: its use, area and year."""

    use: str | None
    built_m2: float | None
    year: int | None


@dataclass(frozen=True)
class UseGroup:
    use: str
    count: int
    built_m2: float | None


@dataclass(frozen=True)
class UnitsSummary:
    total: int
    by_use: tuple[UseGroup, ...]
    built_m2: float | None
    year_built: int | None
    main_use: str | None


UNKNOWN_USE = "Sin uso declarado"


def summarize_units(units: Iterable[Unit]) -> UnitsSummary:
    """The units by use (most built area first), their total built area, the oldest year and the
    use with the most built area. Floors and doors never enter here."""
    items = list(units)
    groups: dict[str, list[Unit]] = {}
    for unit in items:
        groups.setdefault(unit.use or UNKNOWN_USE, []).append(unit)

    def total(units: list[Unit]) -> float | None:
        known = [u.built_m2 for u in units if u.built_m2 is not None]
        return sum(known) if known else None

    by_use = sorted(
        (UseGroup(use, len(group), total(group)) for use, group in groups.items()),
        key=lambda g: (-(g.built_m2 or 0), -g.count, g.use),
    )
    years = [u.year for u in items if u.year]
    return UnitsSummary(
        total=len(items),
        by_use=tuple(by_use),
        built_m2=total(items),
        year_built=min(years) if years else None,
        main_use=by_use[0].use if by_use and by_use[0].use != UNKNOWN_USE else None,
    )


STREET_TYPES: Mapping[str, str] = {
    "CL": "Calle",
    "AV": "Avenida",
    "PZ": "Plaza",
    "PS": "Paseo",
    "GV": "Gran Vía",
    "CR": "Carretera",
    "TR": "Travesía",
    "RD": "Ronda",
    "CM": "Camino",
    "GL": "Glorieta",
    "CT": "Cuesta",
    "PJ": "Pasaje",
    "CJ": "Calleja",
    "CU": "Costanilla",
    "PQ": "Parque",
    "BO": "Barrio",
    "CO": "Colonia",
}


def street_address(
    street_type: str | None, street: str | None, number: str | None, postal_code: str | None
) -> str | None:
    """«Calle Mendez Alvaro 47, 28045 Madrid» from the parts of a Catastro address (never its
    floor or door). None without a street."""
    if not street:
        return None
    kind = STREET_TYPES.get((street_type or "").strip().upper(), (street_type or "").strip())
    name = title_case(street.strip())
    first, _, rest = name.partition(" ")
    if rest and first.lower() in LOWER_PARTICLES:  # «Avenida de la Albufera», after its type
        name = f"{first.lower()} {rest}"
    digits = (number or "").strip().lstrip("0")
    head = " ".join(p for p in (kind, name, digits) if p)
    return f"{head}, {postal_code} Madrid" if postal_code else f"{head}, Madrid"


# --- Addresses typed by a person (the Catastro's street index, when CartoCiudad fails) ---

_TYPED_TYPES: Mapping[str, str] = {
    "calle": "CL",
    "c": "CL",
    "c/": "CL",
    "cl": "CL",
    "avenida": "AV",
    "avda": "AV",
    "av": "AV",
    "plaza": "PZ",
    "pza": "PZ",
    "pl": "PZ",
    "paseo": "PS",
    "ps": "PS",
    "carretera": "CR",
    "ctra": "CR",
    "travesia": "TR",
    "ronda": "RD",
    "camino": "CM",
    "glorieta": "GL",
    "cuesta": "CT",
    "pasaje": "PJ",
    **{code.lower(): code for code in STREET_TYPES},
}
_POSTAL = re.compile(r"^28\d{3}$")


@dataclass(frozen=True)
class TypedAddress:
    street_type: str
    street: str
    number: int


def typed_number(text: str) -> int | None:
    """The portal number of a typed address: the last whole number that is not a postal code."""
    numbers = [n for n in re.findall(r"\b\d{1,5}\b", text) if not _POSTAL.fullmatch(n)]
    return int(numbers[-1]) if numbers else None


def street_words(text: str) -> list[str]:
    """The words of a street as typed or written, without its type, number, postal code or what
    follows a comma: «Calle de Abegondo 1, Madrid» -> ["de", "abegondo"]."""
    head = fold(text.split(",")[0])
    words = [w for w in re.split(r"[\s./]+", head) if w and not w.isdigit()]
    return words[1:] if words and words[0] in _TYPED_TYPES else words


def same_street(typed: str, candidate: str) -> bool:
    """Whether a candidate's street has every word typed (accents, case, particles and the street
    type aside). A geocoder's fuzzy match («calle abegondo 1» -> «BEGONIAS 1») is not."""
    wanted = [w for w in street_words(typed) if w not in LOWER_PARTICLES]
    found = set(street_words(candidate))
    return bool(wanted) and all(w in found for w in wanted)


def parse_address(text: str) -> TypedAddress | None:
    """«calle mayor 61, madrid» -> CL, MAYOR, 61 (upper case, without accents, as the Catastro's
    street index wants it). The street type defaults to «calle». None without a street or a
    number."""
    number = typed_number(text)
    head = fold(text.split(",")[0])
    words = [w for w in re.split(r"[\s.]+", head) if w and not w.isdigit()]
    if number is None or not words:
        return None
    street_type = _TYPED_TYPES.get(words[0])
    if street_type is not None:
        words = words[1:]
    if not words:
        return None
    return TypedAddress(street_type or "CL", " ".join(words).upper(), number)


# --- Buildability ---


@dataclass(frozen=True)
class OfficialFigure:
    """A parcel's buildable m² published by a source (VEDA, the Portal del Suelo)."""

    value_m2: float
    source: str
    dataset_id: str
    use: str | None = None

    @property
    def residential(self) -> bool:
        return self.use is None or fold(self.use).startswith("residencial")


@dataclass(frozen=True)
class BuildabilityResult:
    value_m2: float | None
    kind: BuildabilityKind
    source: str
    article: str | None = None
    article_url: str | None = None
    coefficient: float | None = None
    formula: str | None = None
    note: str | None = None
    assumed_m2: float | None = None
    dataset_ids: tuple[str, ...] = ()


@dataclass(frozen=True)
class Assumption:
    value_m2: float
    coefficient: float
    formula: str
    source: str
    article: str
    article_url: str
    note: str


NO_PLANNING = "Sin la calificación del Ayuntamiento no podemos suponer la edificabilidad."
NO_AREA = "Sin la superficie de la parcela no podemos suponer la edificabilidad."
RUSTIC = "Suelo rústico en el Catastro: no tiene edificabilidad residencial."
DOTACIONAL = "Uso dotacional: el planeamiento no le da edificabilidad residencial."
AREA_PLAN = (
    "Está en un ámbito de planeamiento: su edificabilidad la fija su plan, no un coeficiente de "
    "norma zonal. Consulta la ficha del expediente."
)
NON_BUILDABLE = "Suelo no urbanizable de protección: no es edificable para vivienda."
TYPE_IT = "Pon tú los m² edificables."
OTHER_USE = "La calculadora es para vivienda: pon tú los m² residenciales que quieras estudiar."
ASSUMED_NOTE = (
    "La norma aplica el coeficiente a la parcela edificable, que puede ser menor que la "
    "superficie del Catastro (cesiones, retranqueos)."
)
NZ1_NOTE = (
    "Aproximado: la norma multiplica Z (plano de condiciones de la edificación de 1997) y C por "
    "el fondo edificable o la parcela edificable, no siempre por la parcela entera."
)


def m2_text(value: float) -> str:
    return es_number(value, 0 if value >= 100 or value == int(value) else 1)


def coefficient_text(value: float) -> str:
    return es_number(value, 3).rstrip("0").rstrip(",")


def assume(
    zone: ZoneCode, area_m2: float, coef_z: float | None
) -> tuple[Assumption | None, str | None]:
    """The norm's buildability for a norma zonal on the Catastro's area, or why there is none."""
    rule = RULES[zone.nz]
    article = f"art. {rule.article.number} de las {NNUU_CITATION}"
    if zone.nz == 1:
        factor = NZ1_FACTORS.get(zone.grado or 0)
        if factor is None or coef_z is None or coef_z <= 0:
            return None, rule.none_reason
        value = area_m2 * coef_z * factor
        formula = (
            f"{m2_text(area_m2)} m² de parcela × Z {coefficient_text(coef_z)} × "
            f"C {coefficient_text(factor)}"
        )
        source = f"Supuesto aproximado: norma zonal 1 grado {zone.grado}º, {article}"
        return Assumption(
            value, coef_z * factor, formula, source, rule.article.number, rule.article.url, NZ1_NOTE
        ), None
    if zone.grado is None or (value := coefficient_area(zone.nz, zone.grado, area_m2)) is None:
        return None, rule.none_reason
    coefficient = value / area_m2 if area_m2 else 0.0
    formula = f"{coefficient_text(coefficient)} m²/m² × {m2_text(area_m2)} m² de parcela"
    source = f"Supuesto: norma zonal {zone.nz} grado {zone.grado}º, {article}"
    return Assumption(
        value, coefficient, formula, source, rule.article.number, rule.article.url, ASSUMED_NOTE
    ), None


def none_reason(kind: PlanningKind | None, use: str | None) -> str:
    if kind is None:
        return NO_PLANNING
    if use and "DOTACIONAL" in use.upper():
        return DOTACIONAL
    if kind is PlanningKind.NUP:
        return NON_BUILDABLE
    return AREA_PLAN


def initial_buildability(
    *,
    area_m2: float | None,
    planning_code: str | None,
    use: str | None,
    rustic: bool | None,
    official: Iterable[OfficialFigure] = (),
    coef_z: float | None = None,
) -> BuildabilityResult:
    """The buildable m² the calculator starts from (D-250, spike §1.4), by priority:

    1. the parcel's official residential figure (the first given: VEDA, then the Portal del
       Suelo); a figure of other uses only is a reference, and the start is «sin dato»;
    2. the coefficient of its norma zonal and grado on the Catastro's area (NZ 5, 7, 8, 9);
    3. NZ 1 grados 1º–4º: area × Z × C, approximate;
    4. none («sin dato»), with the reason: the person types it.

    When an official figure wins and the norm would give another, the assumption goes in the note.
    """
    official = list(official)
    residential = [f for f in official if f.residential]
    kind, zone = classify_planning(planning_code) if planning_code else (None, None)
    assumption, reason = None, None
    if zone is not None and area_m2:
        if use and "DOTACIONAL" in use.upper():
            reason = DOTACIONAL
        else:
            assumption, reason = assume(zone, area_m2, coef_z)
    if residential:
        first = residential[0]
        note = None
        if assumption is not None and abs(assumption.value_m2 - first.value_m2) >= 1:
            note = (
                f"La norma zonal daría unos {m2_text(assumption.value_m2)} m² "
                f"({assumption.formula}); manda la cifra oficial."
            )
        return BuildabilityResult(
            value_m2=first.value_m2,
            kind=BuildabilityKind.OFICIAL,
            source=first.source,
            note=note,
            assumed_m2=None if assumption is None else round(assumption.value_m2, 1),
            dataset_ids=tuple(f.dataset_id for f in official),
        )
    if official:  # only of other uses: a reference, never the calculator's start for housing
        first = official[0]
        return BuildabilityResult(
            value_m2=None,
            kind=BuildabilityKind.SIN_DATO,
            source=f"{first.source}: {m2_text(first.value_m2)} m² edificables de uso "
            f"{fold(first.use or 'no residencial')}, no residencial.",
            note=OTHER_USE,
            dataset_ids=tuple(f.dataset_id for f in official),
        )
    if rustic:
        return BuildabilityResult(None, BuildabilityKind.SIN_DATO, RUSTIC, note=TYPE_IT)
    if assumption is not None:
        return BuildabilityResult(
            value_m2=round(assumption.value_m2, 1),
            kind=BuildabilityKind.SUPUESTO,
            source=assumption.source,
            article=assumption.article,
            article_url=assumption.article_url,
            coefficient=round(assumption.coefficient, 4),
            formula=assumption.formula,
            note=assumption.note,
        )
    if zone is not None and not area_m2:
        reason = NO_AREA
    rule = RULES.get(zone.nz) if zone is not None else None
    return BuildabilityResult(
        value_m2=None,
        kind=BuildabilityKind.SIN_DATO,
        source=reason or none_reason(kind, use),
        article=rule.article.number if rule else None,
        article_url=rule.article.url if rule else None,
        note=TYPE_IT,
    )
