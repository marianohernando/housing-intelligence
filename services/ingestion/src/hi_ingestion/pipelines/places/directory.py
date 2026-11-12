"""Entity resolution of a register's places against an official directory (D-218).

The register (Comunidad de Madrid) stays the source of every place: the directory only adds
the institutional name and the capacity it publishes. Places and entries share no code, so they
are matched by postal address with five declared rules, strongest first, one to one:

1. `direccion` (1.0): same postal code, same street and the register's house number appears in
   the directory's address.
2. `calle` (0.9): same postal code and street, and it is the only entry on that street.
3. `direccion_municipio` (0.85): same municipality, street and house number; the postal code may
   differ (the two sources disagree on it at district borders).
4. `codigo_postal` (0.7): the only entry of the same kind in that postal code.
5. `municipio` (0.6): the only entry of the same kind in that municipality (a village that
   shares its postal code with others).

"Only" is judged among every entry of the postal code (or of the municipality). Public and
private never match, nor (below rule 1) two municipalities. An entry two places
claim at the same rule goes to neither (ambiguous) and no weaker rule can take it; an entry
already taken by a stronger rule is never offered again. Streets compare by their words, with
the spellings both catalogues use (abbreviations, plurals, corners, the Ministry's «CALLE» for
every «CL»). Pure logic.
"""

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from pathlib import Path

import pandas as pd

from hi_domain.facilities import dependency
from hi_ingestion.pipelines.places.coordinates import fold_name

ADDRESS, STREET, MUNICIPALITY, POSTCODE, ONLY_IN_MUNICIPALITY = (
    "direccion",
    "calle",
    "direccion_municipio",
    "codigo_postal",
    "municipio",
)
# A pair set by hand in the versioned corrections, with an official source (D-218 §10).
CORRECTION = "correccion"
SCORES = {
    CORRECTION: 1.0,
    ADDRESS: 1.0,
    STREET: 0.9,
    MUNICIPALITY: 0.85,
    POSTCODE: 0.7,
    ONLY_IN_MUNICIPALITY: 0.6,
}
RULES = (ADDRESS, STREET, MUNICIPALITY, POSTCODE, ONLY_IN_MUNICIPALITY)

# Street types, fillers and number markers that registers and directories write differently.
_NOT_A_NAME = frozenset(
    {
        "de", "del", "la", "las", "los", "el", "y", "a", "al",
        "calle", "cl", "avenida", "avda", "av", "plaza", "pza", "pl", "paseo", "po", "pso",
        "glorieta", "gta", "carretera", "ctra", "camino", "ronda", "travesia", "urbanizacion",
        "urb", "poligono", "sector", "plazuela", "pasaje", "km", "sn", "no", "num", "numero",
        "bis", "bajo", "local", "bulevar", "bulev", "blvr", "callejon", "carrera", "cra", "con",
    }
)  # fmt: skip
# «Mª Ángeles», «Ntra. Sra. de Fátima»: the words they stand for.
_ABBREVIATIONS = {
    "ma": "maria", "ntra": "nuestra", "ntro": "nuestro", "sra": "senora", "sta": "santa",
    "sto": "santo",
}  # fmt: skip
# The Ministry's primary care catalogue expanded «CL» to «CALLE» and «AV» to «AVENIDA» wherever
# they appear, also inside words: «SAN CALLEAUDIO», «VALLE INCALLEÁN», «ISLA DE JAVENIDAA».
_EXPANDED = {"cl": "calle", "av": "avenida"}
_EXPANSION = re.compile("|".join(_EXPANDED))
# ... and once glued to the street: «CALLEFUENTESPINA».
_GLUED_TYPE = re.compile(r"\b(?:calle|avenida)(?=[a-z]{4,})")
# «CALLE ZEUS, esq JOAQUÍN BLUME S/N» is on both streets.
_CORNER = re.compile(r"\besq(?:uina)?\b\.?", re.IGNORECASE)
# «Clínica La Luz, S.L.», «Clínica Isadora S.A.», «… Móstoles Sa»: the company, not the place.
_LEGAL_FORM = re.compile(r"[,\s]+s\.?\s?[al]\.?(\s?u\.?)?\s*$", re.IGNORECASE)
# A hospital name says what the place is; an operator («Servicio Madrileño de Salud», «HM
# Hospitales 1989») or a company («Alm Univass») does not, and is never shown as its name.
_FACILITY_WORDS = frozenset(
    {"hospital", "clinica", "sanatorio", "centro", "complejo", "instituto", "fundacion"}
)
_LOWER_WORDS = frozenset({"de", "del", "la", "las", "los", "el", "y", "e", "en", "a", "al"})
_ROMAN = re.compile(r"^[IVXL]+$")


@dataclass(frozen=True)
class Entry:
    external_id: str
    name: str
    address: str
    postal_code: str
    kind: str
    dependency: str | None
    capacity: float | None
    municipality: str | None = None


@dataclass(frozen=True)
class RegisterPlace:
    external_id: str
    subcategory: str
    postal_code: str | None
    street: str | None
    number: int | None
    dependency: str | None = None  # publica | privada, as the register says (hi_domain.facilities)
    municipality: str | None = None


@dataclass(frozen=True)
class Match:
    place_id: str
    entry: Entry
    method: str

    @property
    def score(self) -> float:
        return SCORES[self.method]


@dataclass(frozen=True)
class Resolution:
    matches: list[Match]
    unmatched: dict[str, str]  # register id -> why it has no entry


def _plain(text: str | None) -> str:
    """Folded, punctuation as spaces and numbers apart from words: «Nº12» -> «no 12»."""
    return re.sub(r"(\d+)", r" \1 ", re.sub(r"[^a-z0-9 ]", " ", fold_name(text or "")))


def _singular(word: str) -> str:
    """«Américas» and «América»: a plural in -as or -os, both sources the same way. Short words
    keep their «s» («Ríos» is not «Río»)."""
    return word[:-1] if len(word) > 4 and word[-2:] in ("as", "os") else word


def _words(plain: str) -> frozenset[str]:
    words = (_ABBREVIATIONS.get(w, w) for w in plain.split())
    return frozenset(
        _singular(w) for w in words if w not in _NOT_A_NAME and not w.isdigit() and len(w) > 1
    )


def address_words(text: str | None) -> frozenset[str]:
    return _words(_plain(text))


# «KM.17,900» is a road position and a 5-digit number a postal code: neither is a house number.
_KILOMETRE = re.compile(r"\bkm\.?\s*[\d.,]+", re.IGNORECASE)


def address_numbers(text: str) -> frozenset[int]:
    numbers = re.findall(r"\d+", _KILOMETRE.sub(" ", text))
    return frozenset(int(n) for n in numbers if len(n) < 5)


_PARENTHESES = re.compile(r"\([^)]*\)")


def _spellings(text: str) -> set[frozenset[str]]:
    """One street as both catalogues may write it (see _EXPANDED and _GLUED_TYPE)."""
    plain = _plain(text)
    expanded = _EXPANSION.sub(lambda m: _EXPANDED[m.group()], plain)
    return {_words(plain), _words(expanded), _words(_GLUED_TYPE.sub("", plain))}


@cache
def _street_forms(text: str | None, corners: bool = False) -> frozenset[frozenset[str]]:
    """The street's words, with and without what goes in brackets: «de la Paloma (El Vellón)»
    names the village, «M-515 (POZUELO)» is part of the road's name. With `corners`, a corner
    («Zeus esq. Joaquín Blume») also gives one form per street."""
    forms: set[frozenset[str]] = set()
    for variant in (text or "", _PARENTHESES.sub(" ", text or "")):
        for part in _CORNER.split(variant) if corners else [variant]:
            forms |= _spellings(part)
    return frozenset(f for f in forms if f)


def _same_street(place: RegisterPlace, entry: Entry, corners: bool = False) -> bool:
    """Same words once street types, fillers and numbers are left out: «de Arturo Soria» and
    «Calle De Arturo Soria 17». Equal sets, so «Real» is not «Real de Pozuelo»."""
    return bool(_street_forms(place.street) & _street_forms(entry.address, corners))


def _municipality_key(name: str | None) -> str:
    return fold_name(name or "")


def _compatible(place: RegisterPlace, entry: Entry, method: str) -> bool:
    """Public and private never match each other (when both sources say which it is). Below a
    full address, neither do two municipalities: a rural postal code covers several villages.
    Same postal code, street and number is enough even if the catalogue files the centre under
    its health area's municipality (Aravaca, in Madrid, under Pozuelo de Alarcón)."""
    other = dependency(entry.dependency)
    if place.dependency is not None and other is not None and place.dependency != other:
        return False
    if method != ADDRESS and place.municipality and entry.municipality:
        return _municipality_key(place.municipality) == _municipality_key(entry.municipality)
    return True


def _candidates(place: RegisterPlace, entries: list[Entry], method: str, kind: str) -> list[Entry]:
    """Below a full address the kind must agree too: a register consultorio on the street of a
    catalogue centro de salud is not that centre (Palma 54 and Palma 51, Madrid)."""
    entries = [e for e in entries if _compatible(place, e, method)]
    if method != ADDRESS:
        entries = [e for e in entries if e.kind == kind]
    if method in (POSTCODE, ONLY_IN_MUNICIPALITY):
        return entries
    # A corner entry is on both streets, but only a place without a house number (S/N, «esquina»)
    # can be the corner: «Blume 5» is not «Zeus esq. Blume», and its numbers belong to either.
    corners = method == STREET and place.number is None
    on_street = [e for e in entries if _same_street(place, e, corners)]
    if method == STREET:
        return on_street
    if place.number is None:
        return []
    return [e for e in on_street if place.number in address_numbers(e.address)]


@dataclass(frozen=True)
class _Pools:
    """Entries grouped by postal code and by municipality."""

    by_postcode: dict[str, list[Entry]]
    by_municipality: dict[str, list[Entry]]

    @classmethod
    def of(cls, entries: list[Entry]) -> "_Pools":
        by_postcode: dict[str, list[Entry]] = defaultdict(list)
        by_municipality: dict[str, list[Entry]] = defaultdict(list)
        for entry in entries:
            by_postcode[entry.postal_code].append(entry)
            if entry.municipality:
                by_municipality[_municipality_key(entry.municipality)].append(entry)
        return cls(by_postcode, by_municipality)

    def local(self, place: RegisterPlace, method: str) -> list[Entry]:
        if method not in (MUNICIPALITY, ONLY_IN_MUNICIPALITY):
            return self.by_postcode.get(place.postal_code or "", [])
        if not place.municipality:
            return []
        return self.by_municipality.get(_municipality_key(place.municipality), [])


def _claims(
    pending: dict[str, RegisterPlace],
    pools: _Pools,
    taken: set[str],
    method: str,
    kinds: dict[str, str],
) -> dict[str, list[str]]:
    """entry id -> the places for which it is the only candidate of this rule. Uniqueness is
    judged among every entry of the postal code (or municipality), taken or not: a place the
    directory lacks never inherits a leftover entry of its postal code."""
    claims: dict[str, list[str]] = defaultdict(list)
    for place_id, place in pending.items():
        local = pools.local(place, method)
        found = _candidates(place, local, method, kinds[place.subcategory])
        if len(found) == 1 and found[0].external_id not in taken:
            claims[found[0].external_id].append(place_id)
    return claims


def resolve_places(
    places: list[RegisterPlace],
    entries: list[Entry],
    kinds: dict[str, str],
    forced: dict[str, str] | None = None,
) -> Resolution:
    """Match each place to at most one entry and each entry to at most one place. `forced`
    (place id -> entry id) are the corrections: they go first and their entries are taken."""
    pools = _Pools.of(entries)
    entry_by_id = {e.external_id: e for e in entries}
    pending = {p.external_id: p for p in places if p.subcategory in kinds and p.postal_code}
    unmatched = {
        p.external_id: "no postal code in the register"
        for p in places
        if p.subcategory in kinds and not p.postal_code
    }
    taken: set[str] = set()  # entries matched or contested: never offered to a weaker rule
    matches: list[Match] = []
    for place_id, entry_id in (forced or {}).items():
        if place_id in pending and entry_id in entry_by_id and entry_id not in taken:
            matches.append(Match(place_id, entry_by_id[entry_id], CORRECTION))
            taken.add(entry_id)
            pending.pop(place_id)
    for method in RULES:
        for entry_id, claimants in _claims(pending, pools, taken, method, kinds).items():
            taken.add(entry_id)
            if len(claimants) == 1:
                matches.append(Match(claimants[0], entry_by_id[entry_id], method))
            else:
                for place_id in claimants:
                    unmatched[place_id] = f"ambiguous: {len(claimants)} places claim {entry_id}"
            for place_id in claimants:
                pending.pop(place_id, None)
    for place_id, place in pending.items():
        same_code = pools.by_postcode.get(place.postal_code or "", [])
        unmatched[place_id] = (
            f"no entry in postal code {place.postal_code}"
            if not same_code
            else f"no unique entry among {len(same_code)} in postal code {place.postal_code}"
        )
    return Resolution(sorted(matches, key=lambda m: m.place_id), unmatched)


def _capitalised(word: str) -> str:
    for i, char in enumerate(word):
        if char.isalpha():
            return word[:i] + char.upper() + word[i + 1 :].lower()
    return word


def title_case(text: str) -> str:
    """«LAS ROZAS / EL ABAJÓN» -> «Las Rozas / El Abajón»; «TRES CANTOS II» keeps «II»."""
    words: list[str] = []
    start = True
    for word in text.split():
        if _ROMAN.match(word):
            words.append(word)
        elif not start and word.casefold() in _LOWER_WORDS:
            words.append(word.casefold())
        else:
            words.append("-".join(_capitalised(part) for part in word.split("-")))
        start = word in {"/", "-", "·"}
    return " ".join(words)


def institutional_name(published: str, prefix: str | None) -> str | None:
    """The name to show, or None when the directory gives a company or an operator instead.

    With a prefix the published name is a bare place name (primary care: «ABRANTES» ->
    «Centro de salud Abrantes»); without one it must already say what the place is.
    """
    name = _LEGAL_FORM.sub("", " ".join(published.split())).strip(" ,.")
    if not name:
        return None
    if prefix:
        return f"{prefix} {title_case(name)}"
    words = set(re.sub(r"[^a-z0-9 ]", " ", fold_name(name)).split())
    return name if words & _FACILITY_WORDS else None


def read_entries(path: Path) -> list[Entry]:
    frame = pd.read_csv(path, dtype=str, keep_default_na=False)
    entries: list[Entry] = []
    for row in frame.to_dict("records"):
        raw = str(row["capacity"])
        capacity = float(raw) if raw else None
        entries.append(
            Entry(
                external_id=str(row["external_id"]),
                name=str(row["name"]),
                address=str(row["address"]),
                postal_code=str(row["postal_code"]),
                kind=str(row["kind"]),
                dependency=str(row["dependency"]) or None,
                capacity=capacity if capacity is not None and math.isfinite(capacity) else None,
                municipality=str(row.get("municipality") or "") or None,
            )
        )
    return entries


@dataclass(frozen=True)
class LoadedDirectory:
    """The last valid version of a directory a register declares (DirectoryLink)."""

    dataset_id: str
    source_id: str
    version_label: str
    capacity_unit: str | None
    kinds: dict[str, str]
    name_prefix: dict[str, str]
    entries: list[Entry]


LINK_COLUMNS = [
    "dataset_id",
    "external_id",
    "canonical_place_id",
    "source_id",
    "source_name",
    "source_address",
    "match_method",
    "match_score",
]


@dataclass(frozen=True)
class Attached:
    links: pd.DataFrame  # LINK_COLUMNS: one alias per matched entry (place_source_alias)
    report: dict[str, dict[str, object]]  # dataset_id -> counts and the places left as they were


def _directory_attribute(match: Match, directory: LoadedDirectory) -> dict[str, object]:
    entry = match.entry
    return {
        "dataset_id": directory.dataset_id,
        "version": directory.version_label,
        "external_id": entry.external_id,
        "name": entry.name,
        "kind": entry.kind,
        "dependency": entry.dependency,
        "capacity": entry.capacity,
        "capacity_unit": directory.capacity_unit if entry.capacity is not None else None,
        "match_method": match.method,
        "match_score": match.score,
    }


def _report(
    directory: LoadedDirectory,
    resolution: Resolution,
    places: dict[str, RegisterPlace],
    rejected: list[dict[str, str]],
) -> dict[str, object]:
    matched = {m.entry.external_id for m in resolution.matches}
    methods = [m.method for m in resolution.matches]
    return {
        "version": directory.version_label,
        "entries": len(directory.entries),
        "register_places": sum(p.subcategory in directory.kinds for p in places.values()),
        "matched": len(resolution.matches),
        "by_method": {m: methods.count(m) for m in (CORRECTION, *RULES)},
        "names_rejected": rejected,
        "unmatched_places": [
            {"external_id": pid, "subcategory": places[pid].subcategory, "reason": reason}
            for pid, reason in sorted(resolution.unmatched.items())
        ],
        "unmatched_entries": [
            {"external_id": e.external_id, "name": e.name, "kind": e.kind}
            for e in directory.entries
            if e.external_id not in matched
        ],
    }


def attach_directories(
    rows: list[dict[str, object]],
    places: dict[str, RegisterPlace],
    directories: list[LoadedDirectory],
    forced: dict[str, tuple[str, str]] | None = None,
) -> Attached:
    """Name and size the rows (in place) with the entries they match; return the aliases.
    `forced`: place id -> (directory dataset id, entry id), from the corrections."""
    by_id = {str(r["external_id"]): r for r in rows}
    links: list[dict[str, object]] = []
    report: dict[str, dict[str, object]] = {}
    for directory in directories:
        mine = {
            place_id: entry_id
            for place_id, (dataset_id, entry_id) in (forced or {}).items()
            if dataset_id == directory.dataset_id
        }
        resolution = resolve_places(list(places.values()), directory.entries, directory.kinds, mine)
        rejected: list[dict[str, str]] = []
        for match in resolution.matches:
            row = by_id[match.place_id]
            attributes = row["attributes"]
            assert isinstance(attributes, dict)  # noqa: S101 - built by normalize_places
            attributes["directory"] = _directory_attribute(match, directory)
            prefix = directory.name_prefix.get(places[match.place_id].subcategory)
            name = institutional_name(match.entry.name, prefix)
            if name is None:
                rejected.append({"external_id": match.place_id, "published": match.entry.name})
            else:
                row["canonical_name"] = name
            links.append(
                {
                    "dataset_id": directory.dataset_id,
                    "external_id": match.entry.external_id,
                    "canonical_place_id": row["canonical_place_id"],
                    "source_id": directory.source_id,
                    "source_name": match.entry.name,
                    "source_address": match.entry.address,
                    "match_method": match.method,
                    "match_score": match.score,
                }
            )
        report[directory.dataset_id] = _report(directory, resolution, places, rejected)
    return Attached(pd.DataFrame(links, columns=LINK_COLUMNS), report)
