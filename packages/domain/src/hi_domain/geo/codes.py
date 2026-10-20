"""Administrative code normalisation (INE codes are the canonical identifiers)."""

import re

MADRID_PROVINCE_CODE = "28"
_CM_MUNICIPALITY_CODE = re.compile(r"^\d{4}$")
_INE_MUNICIPALITY_CODE = re.compile(r"^\d{5}$")
_INE_SECTION_CODE = re.compile(r"^\d{10}$")


def ine_municipality_from_cm(cm_code: str) -> str:
    """Comunidad de Madrid uses CMUN (3 digits) + INE check digit, e.g. '0796' -> '28079'."""
    code = cm_code.strip()
    if not _CM_MUNICIPALITY_CODE.match(code):
        msg = f"CM municipality code must have 4 digits, got {cm_code!r}"
        raise ValueError(msg)
    return MADRID_PROVINCE_CODE + code[:3]


def admin_unit_id(level: str, code: str) -> str:
    """Canonical id, e.g. ('municipio', '28079') -> 'ES.28.MUN.28079'."""
    prefixes = {
        "municipio": ("MUN", _INE_MUNICIPALITY_CODE),
        "distrito": ("DIS", re.compile(r"^\d{7}$")),
        "barrio": ("BAR", re.compile(r"^\d{8}$")),
        "seccion_censal": ("SEC", _INE_SECTION_CODE),
    }
    if level not in prefixes:
        msg = f"Unsupported admin level {level!r}"
        raise ValueError(msg)
    prefix, pattern = prefixes[level]
    if not pattern.match(code) or not code.startswith(MADRID_PROVINCE_CODE):
        msg = f"Invalid {level} code {code!r}"
        raise ValueError(msg)
    return f"ES.{MADRID_PROVINCE_CODE}.{prefix}.{code}"


_GSECCION = re.compile(r"^(\d{3})-(\d{2})-(\d{3})$")


def parse_gseccion(value: str) -> tuple[str, str, str]:
    """CM seccionado 'MMM-DD-SSS' -> INE (municipio 5d, distrito 7d, seccion 10d)."""
    match = _GSECCION.match(value.strip())
    if not match:
        msg = f"Unparseable section code {value!r} (expected MMM-DD-SSS)"
        raise ValueError(msg)
    muni, dist, sec = match.groups()
    municipio = MADRID_PROVINCE_CODE + muni
    return municipio, municipio + dist, municipio + dist + sec


def barrio_from_shp(cdtbarrio: str | None, municipio_code: str) -> str | None:
    """SHP CDTBARRIO 'MMMDDB' (6 digits, Madrid capital only) -> 8-digit barrio code."""
    if not cdtbarrio or len(cdtbarrio.strip()) != 6 or not cdtbarrio.strip().isdigit():
        return None
    code = MADRID_PROVINCE_CODE + cdtbarrio.strip()
    return code if code.startswith(municipio_code) else None


def barrio_from_cm_csv(barrio_codigo: str) -> str:
    """CM barrios CSV 'MMMC' + 'DD' + 'B' (e.g. '0796011') -> '28079011'."""
    code = barrio_codigo.strip()
    if not re.match(r"^\d{7}$", code):
        msg = f"CM barrio code must have 7 digits, got {barrio_codigo!r}"
        raise ValueError(msg)
    return ine_municipality_from_cm(code[:4]) + code[4:]
