"""The search by parcel of the investor version (D-250): pure rules, without I/O.

- The cadastral reference: 14 characters for the parcel (18 or 20 for one unit of it).
- The planning code of the Ayuntamiento (`AMB_TX_ETIQ` of «Urbanismo. Destino urbanístico del
  suelo»): a norma zonal with its grado and nivel («8.3.a», «1.2», «4») or a planning area
  («APR.02.06», «UZPp.02.04-RP», «NUP.1»).
- Whether a parcel has nothing built, from the Catastro's use and built area (never «solar»: that
  is a legal condition, with services, that no open data gives per parcel).
- The units of a building in horizontal division, summarised by use (never floor and door).
- The buildable m² the calculator starts from, by priority: the official figure of the parcel
  (VEDA, then the Portal del Suelo), the coefficient of its norma zonal, the NZ 1 formula, or none.
  Always editable; an assumption says so and cites its article.
- D-252: the plan's buildable m² by use (tables 4 and 5 of USOS_SUELO), the state of the
  planning area (203200 and VEDA) and the cautions that keep a figure from passing for housing
  ready to build: another use, an area not finished, protected housing, a single-family home.
"""

import re
import unicodedata
from bisect import bisect_right
from collections.abc import Iterable, Mapping
from dataclasses import dataclass

from hi_contracts.pro.investors import BuildabilityKind, PlanningKind, UseClass, UseOwnership
from hi_domain import ambit_status as ambits
from hi_domain import plan_uses_data as plan_data
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


# --- Uses (D-252) ---

# The first words of a use, as the planning layer (USOS_SUELO, `USP_TX_DENOM`), VEDA
# (`TIPO_SUELO`) or the Portal del Suelo (`uso_principal_codigo` in words) write it. Checked
# against the 137 values of the planning layer read on 19 Nov (VEDA writes «INDUSTRIA …» too).
_USE_PREFIXES: tuple[tuple[str, UseClass], ...] = (
    ("residencial", UseClass.RESIDENCIAL),
    ("servicios terciario", UseClass.TERCIARIO),  # also «SERVICIOS TERCIARIO OFICINAS» (VEDA)
    ("terciario", UseClass.TERCIARIO),
    ("industria", UseClass.INDUSTRIAL),
    ("dotacional zonas verdes", UseClass.ZONA_VERDE),
    ("dotacional via publica", UseClass.INFRAESTRUCTURA),
    ("dotacional transporte", UseClass.INFRAESTRUCTURA),
    ("dotacional servicios infraestructurales", UseClass.INFRAESTRUCTURA),
    ("dotacional", UseClass.DOTACIONAL),
    ("sin uso", UseClass.SIN_USO),
)
_OWNED_CLASSES = frozenset({UseClass.DOTACIONAL, UseClass.ZONA_VERDE, UseClass.INFRAESTRUCTURA})


def classify_use(use: str | None) -> tuple[UseClass | None, UseOwnership | None]:
    """A use's class, and whether a dotacional use is public or private when the words say it
    («DOTACIONAL EQUIPAMIENTO PRIVADO EDUCATIVO»: dotacional, privado). Housing «de protección
    pública» is a price regime, not public ownership: no owner. None for no use; «otro» for words
    of no known class (the Portal del Suelo's «Otros», a mixed use)."""
    if not use or not use.strip():
        return None, None
    words = " ".join(fold(use).split())
    kind = next((k for prefix, k in _USE_PREFIXES if words.startswith(prefix)), UseClass.OTRO)
    if kind not in _OWNED_CLASSES:
        return kind, None
    tokens = set(words.split())
    owner = None
    if "privado" in tokens:
        owner = UseOwnership.PRIVADO
    elif "publico" in tokens or "administracion publica" in words:
        owner = UseOwnership.PUBLICO
    return kind, owner


@dataclass(frozen=True)
class UseFigureResult:
    """One source's figure for the parcel with the use it gives (never split by use)."""

    use_class: UseClass
    use: str
    value_m2: float
    source: str
    dataset_id: str
    residential: bool


# D-252c: the snapshot of tables 4 and 5 of USOS_SUELO, by CODIGO (= UBOV_ID)
PLAN_USES_AS_OF = plan_data.AS_OF


def _table_4_runs() -> tuple[list[int], list[int], list[int]]:
    """The runs of table 4 decoded once: first CODIGO, last CODIGO and principal use index."""
    starts, ends, uses, last = [], [], [], -1
    for gap, span, use in plan_data.TABLE_4:
        low = last + gap + 1
        last = low + span
        starts.append(low)
        ends.append(last)
        uses.append(use)
    return starts, ends, uses


_TABLE_4_STARTS, _TABLE_4_ENDS, _TABLE_4_USES = _table_4_runs()


def plan_rows(urban_parcel_id: int) -> tuple[tuple[str, float, str, bool], ...]:
    """(use, figure, unit, principal) of the rows with a figure of an urban parcel; () if none."""
    return tuple(
        (plan_data.USES[use], value, plan_data.UNITS[unit], principal)
        for use, value, unit, principal in plan_data.ROWS.get(urban_parcel_id, ())
    )


def principal_use(urban_parcel_id: int) -> str | None:
    """Table 4's principal use of the urban parcel (with a figure or not); None if absent."""
    at = bisect_right(_TABLE_4_STARTS, urban_parcel_id) - 1
    if at < 0 or _TABLE_4_ENDS[at] < urban_parcel_id:
        return None
    return plan_data.USES[_TABLE_4_USES[at]]


def in_table_4(urban_parcel_id: int) -> bool:
    """Whether table 4 has the urban parcel (every one there has a principal use row)."""
    return principal_use(urban_parcel_id) is not None


@dataclass(frozen=True)
class PlanUseResult:
    """D-252: what the plan allows of one use on the urban parcel (USOS_SUELO, tables 4 and 5):
    m², or m²/m² times the urban parcel's area (an assumption)."""

    use: str
    use_class: UseClass
    use_ownership: UseOwnership | None
    principal: bool
    value_m2: float | None
    coefficient: float | None
    assumed: bool


def plan_use(
    use: str | None, value: float | None, unit: str | None, principal: bool, area_m2: float | None
) -> PlanUseResult | None:
    """One row of table 4 («uso cualificado principal») or 5 («otros usos cualificados»); None
    without a use or a figure (the plan does not publish one)."""
    if not use or not use.strip() or value is None or value <= 0:
        return None
    kind, owner = classify_use(use)
    per_m2 = "/" in (unit or "")
    if per_m2:
        total = None if not area_m2 else value * area_m2
        return PlanUseResult(
            " ".join(use.split()),
            kind or UseClass.OTRO,
            owner,
            principal,
            total,
            value,
            total is not None,
        )
    return PlanUseResult(
        " ".join(use.split()), kind or UseClass.OTRO, owner, principal, value, None, False
    )


DONE_PHASES = frozenset({"finalizado", "no necesita", "pgoum-85", "pgoum-97"})
PENDING_STAGES = frozenset(
    {"pendiente_sectorizacion", "pendiente_planeamiento", "gestion_urbanizacion"}
)
PHASE_LABELS = ("Planeamiento", "Gestión", "Proyecto de urbanización", "Obras de urbanización")
_SUFFIX = re.compile(r"(/M|-M|-RP|/UE-\d+|/C)$", re.IGNORECASE)


@dataclass(frozen=True)
class AmbitState:
    """D-252: the state of a planning area as the Ayuntamiento publishes it (203200 and VEDA);
    phases and stage None when it does not follow the area (the historic centre, the colonias,
    annulled areas)."""

    code: str
    phases: tuple[str, str, str, str] | None
    veda_stage: str | None

    @property
    def tracked(self) -> bool:
        return self.phases is not None or self.veda_stage is not None

    @property
    def pending(self) -> bool:
        """Planning, management or urbanization not finished, by either source."""
        undone = self.phases is not None and any(fold(p) not in DONE_PHASES for p in self.phases)
        return undone or self.veda_stage in PENDING_STAGES


def _base(code: str) -> str:
    return _SUFFIX.sub("", code.strip()).upper()


_BY_CODE = {code.upper(): code for code in ambits.AMBITS}
_BY_BASE: dict[str, list[str]] = {}
for _code in ambits.AMBITS:
    _BY_BASE.setdefault(_base(_code), []).append(_code)


def ambit_state(code: str | None) -> AmbitState | None:
    """The state of the planning area a code names: the same code in the Ayuntamiento's list
    (any case), else the one with the same code without its suffix (/M, -RP, /UE-n), if only
    one. None for a norma zonal; untracked (no phases) for an area the list does not follow."""
    if not code:
        return None
    kind, zone = classify_planning(code)
    if zone is not None or kind is PlanningKind.OTRO:
        return None
    key = _BY_CODE.get(code.strip().upper())
    if key is None:
        same = _BY_BASE.get(_base(code), [])
        key = same[0] if len(same) == 1 else None
    if key is None:
        return AmbitState(code.strip(), None, None)
    phases, stage = ambits.AMBITS[key]
    return AmbitState(key, phases, stage)


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
        return self.use is None or classify_use(self.use)[0] is UseClass.RESIDENCIAL

    def by_use(self) -> UseFigureResult:
        kind, _ = classify_use(self.use)
        return UseFigureResult(
            use_class=kind or UseClass.RESIDENCIAL,
            use=self.use or "Residencial",
            value_m2=self.value_m2,
            source=self.source,
            dataset_id=self.dataset_id,
            residential=self.residential,
        )


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
    by_use: tuple[UseFigureResult, ...] = ()


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
AMBIT_PENDING_NOTE = (
    "El ámbito no está terminado: la cifra es una referencia, no los m² de partida. Pon tú los "
    "m² si quieres hacer números."
)
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


# --- D-252: cautions ---

PHASE_WORDS = ("planeamiento", "gestión", "proyecto de urbanización", "obras de urbanización")
STAGE_WORDS: Mapping[str, str] = {
    "pendiente_sectorizacion": "pendiente de plan de sectorización",
    "pendiente_planeamiento": "pendiente de planeamiento de desarrollo",
    "gestion_urbanizacion": "en gestión o urbanización",
    "edificacion": "en fase de edificación",
}
AMBIT_PENDING = (
    "Faltan planeamiento, gestión o urbanización. Si es suelo urbano no consolidado o "
    "urbanizable, la ley pide ceder gratis al Ayuntamiento el suelo para el 10 % de la "
    "edificabilidad del ámbito y costear las obras de urbanización (Ley 9/2001 del Suelo de la "
    "Comunidad de Madrid, arts. 18.2.c, 18.2.d y 21.1). Ni eso ni los años de plazo entran en "
    "esta cuenta."
)
PROTECTED = (
    "Vivienda con protección pública: su precio de venta tiene un máximo legal por m² útil que "
    "fija la Comunidad de Madrid por orden (Decreto 74/2009, Reglamento de Viviendas con "
    "Protección Pública, art. 12). El precio libre del barrio no vale: pon el de su régimen."
)
SINGLE_FAMILY = (
    "Vivienda unifamiliar: el coste de partida es el de un bloque de pisos (bloque abierto) y el "
    "precio de venta, el de la vivienda del barrio en general. Una casa tiene otro coste y otro "
    "precio: cámbialos."
)


def ambit_pending_text(ambit: AmbitState) -> str:
    """«El ámbito APR.04.09 no está terminado según el Ayuntamiento: planeamiento, gestión… sin
    iniciar; en VEDA, pendiente de planeamiento de desarrollo.» and what that leaves out."""
    parts = []
    if ambit.phases is not None:
        undone = [
            f"{word} {state.lower()}"
            for word, state in zip(PHASE_WORDS, ambit.phases, strict=True)
            if fold(state) not in DONE_PHASES
        ]
        parts += undone
    if ambit.veda_stage in PENDING_STAGES:
        parts.append(f"en VEDA, {STAGE_WORDS[ambit.veda_stage or '']}")
    said = "; ".join(parts)
    return (
        f"El ámbito {ambit.code} no está terminado según el Ayuntamiento: {said}. {AMBIT_PENDING}"
    )


# D-253: the catalogue of protected buildings (NNUU, título 4, art. 4.3.4: nivel 1 singular e
# integral, nivel 2 estructural y volumétrico, nivel 3 parcial y ambiental)
CATALOG_LEVELS: Mapping[str, int] = {
    "singular": 1,
    "integral": 1,
    "estructural": 2,
    "volumetrico": 2,
    "parcial": 3,
    "ambiental": 3,
}


@dataclass(frozen=True)
class CatalogEntry:
    """D-253: the building of the parcel in the Plan General's catalogue (300158)."""

    number: str | None
    name: str | None
    protection: str | None
    url: str | None

    @property
    def level(self) -> int | None:
        words = fold(self.protection or "").split()
        return next((CATALOG_LEVELS[w] for w in words if w in CATALOG_LEVELS), None)


@dataclass(frozen=True)
class ExistingBuilding:
    """D-253: what is built on the parcel today, as the Catastro says it."""

    built_m2: float
    year: int | None = None
    units: int | None = None


def catalog_text(entry: CatalogEntry) -> str:
    """What a catalogued building means for a new-build account (NNUU arts. 4.3.4 and 4.3.7)."""
    protection = f", protección {entry.protection.lower()}" if entry.protection else ""
    number = f" (nº {entry.number})" if entry.number else ""
    head = f"Edificio catalogado por el Plan General{protection}{number}"
    if entry.level in (1, 2):
        return (
            f"{head}: está protegido en su conjunto, y ni siquiera en ruina puede tener orden o "
            "licencia de demolición (Normas Urbanísticas, arts. 4.3.4 y 4.3.7). La cuenta de "
            "obra nueva no vale."
        )
    if entry.level == 3:
        return (
            f"{head}: se protegen elementos concretos. En ruina, se puede rehabilitar o derribar, "
            "pero la licencia puede obligar a mantener esos elementos en el edificio nuevo "
            "(Normas Urbanísticas, arts. 4.3.4 y 4.3.7). La cuenta de obra nueva sobre suelo "
            "libre no vale tal cual."
        )
    return (
        f"{head}: las obras que se pueden hacer dependen de su protección (Normas Urbanísticas, "
        "título 4). La cuenta de obra nueva no vale tal cual."
    )


def existing_text(building: ExistingBuilding) -> str:
    """«Hay un edificio de 376 m² construidos (de 1890), con 6 inmuebles…»: data, no rule."""
    year = f" (de {building.year})" if building.year else ""
    units = (
        f", con {building.units} inmuebles en división horizontal"
        if building.units and building.units > 1
        else ""
    )
    left_out = (
        "el derribo, el desalojo ni la compra a los propietarios de sus inmuebles"
        if units
        else "el derribo ni el desalojo"
    )
    return (
        f"Hay un edificio de {m2_text(building.built_m2)} m² construidos{year}{units}. La "
        f"calculadora es de obra nueva sobre suelo libre: no cuenta {left_out}."
    )


def _says(words: str, *needles: str) -> bool:
    folded = fold(words)
    return any(n in folded for n in needles)


def parcel_cautions(
    use: str | None,
    official: Iterable[OfficialFigure],
    ambit: AmbitState | None,
    *,
    catalog: CatalogEntry | None = None,
    building: ExistingBuilding | None = None,
) -> list[tuple[str, str]]:
    """(key, text) of what keeps the sheet's figures from passing for free housing ready to
    build: another use in the plan, a planning area not finished or whose state is not
    published (with an official figure), protected housing (the plan's use or an official
    figure's) and a single-family home."""
    official = list(official)
    uses = [u for u in (use, *(f.use for f in official)) if u]
    cautions: list[tuple[str, str]] = []
    if (other := other_use(use)) is not None:
        cautions.append(
            (
                "otro_uso",
                f"El planeamiento da a esta parcela uso {other}, no de vivienda. La calculadora "
                "es solo de vivienda: comprueba en la ficha oficial si la parcela la admite "
                "antes de hacer números.",
            )
        )
    if ambit is not None and ambit.pending:
        cautions.append(("ambito_pendiente", ambit_pending_text(ambit)))
    if ambit is not None and not ambit.tracked and official:  # review of #109, R-05
        cautions.append(
            (
                "ambito_sin_estado",
                f"El Ayuntamiento no publica el estado del ámbito {ambit.code}: la cifra "
                "oficial no está contrastada con su desarrollo.",
            )
        )
    if any(_says(u, "proteg", "proteccion") for u in uses):
        cautions.append(("vivienda_protegida", PROTECTED))
    if any(_says(u, "unifamiliar") for u in uses):
        cautions.append(("unifamiliar", SINGLE_FAMILY))
    if catalog is not None:  # D-253 (audit D5)
        cautions.append(("edificio_catalogado", catalog_text(catalog)))
    if building is not None and building.built_m2 > 0:
        cautions.append(("edificio_existente", existing_text(building)))
    return cautions


_NOT_OTHER = frozenset({UseClass.RESIDENCIAL, UseClass.SIN_USO})


def other_use(use: str | None) -> str | None:
    """The plan's use in words when it is not housing nor undecided («industrial»), else None."""
    kind, owner = classify_use(use)
    if kind is None or kind in _NOT_OTHER:
        return None
    label = USE_WORDS[kind]
    if owner is not None and kind is UseClass.DOTACIONAL:
        label += " público" if owner is UseOwnership.PUBLICO else " privado"
    return label


USE_WORDS: Mapping[UseClass, str] = {
    UseClass.RESIDENCIAL: "residencial",
    UseClass.TERCIARIO: "terciario",
    UseClass.INDUSTRIAL: "industrial",
    UseClass.DOTACIONAL: "dotacional",
    UseClass.ZONA_VERDE: "de zona verde",
    UseClass.INFRAESTRUCTURA: "de vía pública, transporte o infraestructuras",
    UseClass.SIN_USO: "sin uso pormenorizado",
    UseClass.OTRO: "de otro tipo",
}


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
    ambit: AmbitState | None = None,
) -> BuildabilityResult:
    """The buildable m² the calculator starts from (D-250, spike §1.4), by priority:

    1. the parcel's official residential figure (the first given: VEDA, then the Portal del
       Suelo); a figure of other uses only is a reference, and the start is «sin dato»;
    2. the coefficient of its norma zonal and grado on the Catastro's area (NZ 5, 7, 8, 9);
    3. NZ 1 grados 1º–4º: area × Z × C, approximate;
    4. none («sin dato»), with the reason: the person types it.

    When an official figure wins and the norm would give another, the assumption goes in the note.
    D-252: an official figure in a planning area not finished, or a norm's assumption where the
    plan gives another use than housing, is a reference and the start is «sin dato» (as R-08).
    """
    official = list(official)
    residential = [f for f in official if f.residential]
    by_use = tuple(f.by_use() for f in official)
    kind, zone = classify_planning(planning_code) if planning_code else (None, None)
    assumption, reason = None, None
    if zone is not None and area_m2:
        if use and "DOTACIONAL" in use.upper():
            reason = DOTACIONAL
        else:
            assumption, reason = assume(zone, area_m2, coef_z)
    if residential and ambit is not None and ambit.pending:
        first = residential[0]
        return BuildabilityResult(
            value_m2=None,
            kind=BuildabilityKind.SIN_DATO,
            source=f"{first.source}: {m2_text(first.value_m2)} m² edificables de vivienda, pero "
            f"el ámbito {ambit.code} no está terminado.",
            note=AMBIT_PENDING_NOTE,
            dataset_ids=tuple(f.dataset_id for f in official),
            by_use=by_use,
        )
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
            by_use=by_use,
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
            by_use=by_use,
        )
    if rustic:
        return BuildabilityResult(None, BuildabilityKind.SIN_DATO, RUSTIC, note=TYPE_IT)
    other = other_use(use)
    if assumption is not None and other is not None:  # NZ 9 and the like: never housing m²
        return BuildabilityResult(
            value_m2=None,
            kind=BuildabilityKind.SIN_DATO,
            source=f"{assumption.source}: unos {m2_text(assumption.value_m2)} m² edificables de "
            f"uso {other}, no de vivienda.",
            article=assumption.article,
            article_url=assumption.article_url,
            coefficient=round(assumption.coefficient, 4),
            formula=assumption.formula,
            note=OTHER_USE,
            assumed_m2=round(assumption.value_m2, 1),
        )
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
