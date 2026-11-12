"""Entity resolution of a register's places against an official directory (D-218).

The register (Comunidad de Madrid) stays the source of every place: the directory only adds
the institutional name and the capacity it publishes. Places and entries share no code, so they
are matched by postal address with three declared rules, strongest first, one to one:

1. `direccion` (1.0): same postal code, same street and the register's house number appears in
   the directory's address.
2. `calle` (0.9): same postal code and street, and it is the only entry on that street.
3. `codigo_postal` (0.7): the only entry of the same kind in that postal code.

"Only" is judged among every entry of the postal code. Public and private never match. An entry
two places claim at the same rule goes to neither (ambiguous) and no weaker rule can take it; an
entry already taken by a stronger rule is never offered again. Pure logic.
"""

import math
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from hi_domain.facilities import dependency
from hi_ingestion.pipelines.places.coordinates import fold_name

ADDRESS, STREET, POSTCODE = "direccion", "calle", "codigo_postal"
SCORES = {ADDRESS: 1.0, STREET: 0.9, POSTCODE: 0.7}

# Street types, fillers and number markers that registers and directories write differently.
_NOT_A_NAME = frozenset(
    {
        "de", "del", "la", "las", "los", "el", "y", "a", "al",
        "calle", "cl", "avenida", "avda", "av", "plaza", "pza", "pl", "paseo", "po", "pso",
        "glorieta", "gta", "carretera", "ctra", "camino", "ronda", "travesia", "urbanizacion",
        "urb", "poligono", "sector", "km", "sn", "no", "num", "numero", "bis",
    }
)  # fmt: skip
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


@dataclass(frozen=True)
class RegisterPlace:
    external_id: str
    subcategory: str
    postal_code: str | None
    street: str | None
    number: int | None
    dependency: str | None = None  # publica | privada, as the register says (hi_domain.facilities)


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


def address_words(text: str | None) -> frozenset[str]:
    words = re.sub(r"[^a-z0-9 ]", " ", fold_name(text or "")).split()
    return frozenset(w for w in words if w not in _NOT_A_NAME and not w.isdigit() and len(w) > 1)


# «KM.17,900» is a road position and a 5-digit number a postal code: neither is a house number.
_KILOMETRE = re.compile(r"\bkm\.?\s*[\d.,]+", re.IGNORECASE)


def address_numbers(text: str) -> frozenset[int]:
    numbers = re.findall(r"\d+", _KILOMETRE.sub(" ", text))
    return frozenset(int(n) for n in numbers if len(n) < 5)


def _same_street(place: RegisterPlace, entry: Entry) -> bool:
    """Same words once street types, fillers and numbers are left out: «de Arturo Soria» and
    «Calle De Arturo Soria 17». Equal sets, so «Real» is not «Real de Pozuelo»."""
    words = address_words(place.street)
    return bool(words) and words == address_words(entry.address)


def _compatible(place: RegisterPlace, entry: Entry) -> bool:
    """Public and private never match each other (when both sources say which it is)."""
    other = dependency(entry.dependency)
    return place.dependency is None or other is None or place.dependency == other


def _candidates(place: RegisterPlace, entries: list[Entry], method: str, kind: str) -> list[Entry]:
    entries = [e for e in entries if _compatible(place, e)]
    if method == POSTCODE:
        return [e for e in entries if e.kind == kind]
    on_street = [e for e in entries if _same_street(place, e)]
    if method == STREET:
        return on_street
    if place.number is None:
        return []
    return [e for e in on_street if place.number in address_numbers(e.address)]


def _claims(
    pending: dict[str, RegisterPlace],
    by_postcode: dict[str, list[Entry]],
    taken: set[str],
    method: str,
    kinds: dict[str, str],
) -> dict[str, list[str]]:
    """entry id -> the places for which it is the only candidate of this rule. Uniqueness is
    judged among every entry of the postal code, taken or not: a place the directory lacks never
    inherits a leftover entry of its postal code."""
    claims: dict[str, list[str]] = defaultdict(list)
    for place_id, place in pending.items():
        local = by_postcode.get(place.postal_code or "", [])
        found = _candidates(place, local, method, kinds[place.subcategory])
        if len(found) == 1 and found[0].external_id not in taken:
            claims[found[0].external_id].append(place_id)
    return claims


def resolve_places(
    places: list[RegisterPlace], entries: list[Entry], kinds: dict[str, str]
) -> Resolution:
    """Match each place to at most one entry and each entry to at most one place."""
    by_postcode: dict[str, list[Entry]] = defaultdict(list)
    for entry in entries:
        by_postcode[entry.postal_code].append(entry)
    entry_by_id = {e.external_id: e for e in entries}
    pending = {p.external_id: p for p in places if p.subcategory in kinds and p.postal_code}
    unmatched = {
        p.external_id: "no postal code in the register"
        for p in places
        if p.subcategory in kinds and not p.postal_code
    }
    taken: set[str] = set()  # entries matched or contested: never offered to a weaker rule
    matches: list[Match] = []
    for method in (ADDRESS, STREET, POSTCODE):
        for entry_id, claimants in _claims(pending, by_postcode, taken, method, kinds).items():
            taken.add(entry_id)
            if len(claimants) == 1:
                matches.append(Match(claimants[0], entry_by_id[entry_id], method))
            else:
                for place_id in claimants:
                    unmatched[place_id] = f"ambiguous: {len(claimants)} places claim {entry_id}"
            for place_id in claimants:
                pending.pop(place_id, None)
    for place_id, place in pending.items():
        same_code = by_postcode.get(place.postal_code or "", [])
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
        "by_method": {m: methods.count(m) for m in (ADDRESS, STREET, POSTCODE)},
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
) -> Attached:
    """Name and size the rows (in place) with the entries they match; return the aliases."""
    by_id = {str(r["external_id"]): r for r in rows}
    links: list[dict[str, object]] = []
    report: dict[str, dict[str, object]] = {}
    for directory in directories:
        resolution = resolve_places(list(places.values()), directory.entries, directory.kinds)
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
