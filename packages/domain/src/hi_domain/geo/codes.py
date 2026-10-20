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
