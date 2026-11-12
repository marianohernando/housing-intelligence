"""Per-zone list of what is missing (GAP-001): feature values against the municipios of the
zone's type in the region (D-213, services/gap_reference.py).

Rows come from the features bound to a gap row in the Feature Dictionary (`gap_row`), so no
feature id is hardcoded here. Parameterised SQL only.
"""

from collections.abc import Iterable
from typing import Any, NamedTuple

from sqlalchemy import Connection, text

from hi_api.services.attribution import GEOCODER_SOURCE, attribution_text
from hi_api.services.gap_reference import (
    Assessment,
    References,
    assess,
    group_sentence,
    judge,
    load_references,
)
from hi_contracts.api.envelope import ErrorCode
from hi_contracts.catalog.enums import GapRowKey, TerritoryLevel
from hi_contracts.public import (
    DatasetRef,
    GapRow,
    IndicatorValue,
    PeopleCount,
    ZoneGapList,
    ZoneRef,
)
from hi_domain.gap_impact import ROW_PEOPLE, people_in
from hi_domain.gaps import (
    GAP_METHOD,
    REGION_TEXT,
    UnclassifiableError,
    explanation,
    oriented_ratio,
)
from hi_domain.geo.names import display_name

REGION_LEVEL, REGION_CODE = "ccaa", "28"
SIGNIFICANT_DIGITS = 4


def significant(value: float) -> float:
    """Round for display without erasing small ratios (0.00287 stays 0.002871)."""
    return float(f"{value:.{SIGNIFICANT_DIGITS}g}")


ROW_ORDER = list(GapRowKey)

_ZONE = text(
    """
    SELECT u.admin_unit_id, u.code_official, u.name, m.code_official AS municipio_ine,
           m.name AS municipio_name, ST_X(c) AS lon, ST_Y(c) AS lat
      FROM (SELECT *, ST_PointOnSurface(geom_4326) AS c FROM geo_admin_unit
             WHERE level = :level AND code_official = :code) u
      LEFT JOIN geo_admin_unit m
        ON m.level = 'municipio' AND m.code_official = left(u.code_official, 5)
    """
)
_BOUND_FEATURES = text(
    """
    SELECT feature_id, human_name, unit, direction, spec->'gap_row' AS gap_row,
           spec->'formula' AS formula
      FROM feature_registry
     WHERE spec->'gap_row' IS NOT NULL AND spec->'gap_row' <> 'null'::jsonb
    """
)
_VALUES = text(
    """
    SELECT feature_id, territory_level, value, null_reason, confidence, inputs, computed_at
      FROM feature_value
     WHERE feature_id = ANY(:features)
       AND ((territory_level = :level AND territory_code = :code)
            OR (territory_level = :region_level AND territory_code = :region_code))
    """
)
_DATASETS = text(
    """
    SELECT d.dataset_id, d.name, d.owner, coalesce(d.portal_url, d.landing_url) AS url,
           d.is_cm_open_data, s.license_name,
           s.attribution_text,
           EXISTS (SELECT 1 FROM place_master p
                    WHERE p.official_dataset_id = d.dataset_id
                      AND p.attributes->'coordinates'->>'origin' = 'geocoded') AS geocoded,
           (SELECT g.attribution_text FROM source_registry g
             WHERE g.source_id = :geocoder) AS geocoder_attribution
      FROM dataset_registry d JOIN source_registry s ON s.source_id = d.source_id
     WHERE d.dataset_id = ANY(:ids)
     ORDER BY d.dataset_id
    """
)


class ZoneNotFoundError(LookupError):
    pass


def zone_ref(conn: Connection, level: TerritoryLevel, code: str) -> ZoneRef:
    row = conn.execute(_ZONE, {"level": level.value, "code": code}).mappings().first()
    if row is None:
        msg = f"No {level.value} with code {code}"
        raise ZoneNotFoundError(msg)
    municipio_name = display_name(row["municipio_name"]) if row["municipio_name"] else None
    if level is TerritoryLevel.SECCION_CENSAL:  # sections have no official name
        name = f"Sección {code[5:7]}-{code[7:]}" + (
            f" · {municipio_name}" if municipio_name else ""
        )
    else:
        name = display_name(row["name"]) if row["name"] else code
    return ZoneRef(
        level=level,
        code=code,
        admin_unit_id=row["admin_unit_id"],
        name=name,
        municipio_ine=row["municipio_ine"],
        municipio_name=municipio_name,
        center_lon=round(row["lon"], 5),
        center_lat=round(row["lat"], 5),
    )


def dataset_refs(conn: Connection, versions: dict[str, str]) -> list[DatasetRef]:
    params = {"ids": sorted(versions), "geocoder": GEOCODER_SOURCE}
    rows = conn.execute(_DATASETS, params).mappings().all()
    return [
        DatasetRef.model_validate(
            {
                "dataset_id": r["dataset_id"],
                "name": r["name"],
                "publisher": r["owner"],
                "is_cm_open_data": r["is_cm_open_data"],
                "url": r["url"],
                "version": versions.get(r["dataset_id"]),
                "license": r["license_name"],
                "attribution_text": attribution_text(r),
            }
        )
        for r in rows
    ]


def _indicator(
    feature: dict[str, Any], row: dict[str, Any], level: TerritoryLevel
) -> IndicatorValue:
    return IndicatorValue(
        feature_id=feature["feature_id"],
        label=feature["human_name"],
        value=None if row["value"] is None else significant(float(row["value"])),
        unit=feature["unit"],
        confidence=float(row["confidence"]),
        null_reason=row["null_reason"],
        level=level,
        datasets=sorted(row["inputs"].get("dataset_versions", {})),
    )


def row_people(
    key: GapRowKey, feature: dict[str, Any], row: dict[str, Any], level: TerritoryLevel
) -> PeopleCount | None:
    """Who the row serves in the zone: its indicator's denominator, in people (D-229)."""
    count = people_in((row["inputs"] or {}).get("counts"), feature["formula"] or {}, level.value)
    return None if count is None else PeopleCount(count=count, label=ROW_PEOPLE[key].people)


class Measured(NamedTuple):
    """A feature bound to a gap row, with its value row for one zone."""

    feature: dict[str, Any]
    value: dict[str, Any]


class ZoneContext(NamedTuple):
    """Where the rows are computed: level, zone code and the references by type (D-213)."""

    level: TerritoryLevel
    code: str
    references: References


def _gap_row(
    conn: Connection,
    main: Measured,
    reference_row: dict[str, Any] | None,
    extras: list[Measured],
    zone: ZoneContext,
) -> GapRow:
    feature, row = main
    binding = feature["gap_row"]
    indicator = _indicator(feature, row, zone.level)
    ref = zone.references.for_zone(feature["feature_id"], zone.code, reference_row)
    judged = Assessment(None, True)
    if indicator.value is None:
        ratio, text_ = None, "Sin datos para esta zona"
    elif ref is None:
        msg = f"{feature['feature_id']}: no regional reference"
        raise UnclassifiableError(msg)
    else:
        ratio = oriented_ratio(indicator.value, ref.value, feature["direction"])
        judged = assess(row, ref, feature["direction"])
        text_ = explanation(indicator.value, ref.value, binding["phrase"], ref.phrase, ref.regional)
    versions = merged_versions(row, reference_row, [e.value for e in extras])
    if ref is not None and ref.regional is not None:  # the type comes from population and area
        versions = zone.references.versions | versions
    verdict = judge(ratio, judged, zone.references, feature["feature_id"], zone.code)
    if verdict.group is not None:
        text_ += "; " + group_sentence(verdict.group)
    return GapRow(
        row=binding["row"],
        label=binding["label"],
        status=verdict.status,
        indicator=indicator,
        reference=None if ref is None else significant(ref.value),
        reference_label=REGION_TEXT.label if ref is None else ref.label,
        regional_reference=None
        if ref is None or ref.regional is None
        else significant(ref.regional),
        direction=feature["direction"],
        ratio_to_reference=None if ratio is None else significant(ratio),
        explanation=text_,
        proxy_note=binding.get("proxy_note"),
        reliable=verdict.reliable,
        comparison_group=verdict.group,
        extra_indicators=[_indicator(e.feature, e.value, zone.level) for e in extras],
        people=row_people(GapRowKey(binding["row"]), feature, row, zone.level),
        datasets=dataset_refs(conn, versions),
    )


def merged_versions(
    row: dict[str, Any], reference_row: dict[str, Any] | None, extra_rows: list[dict[str, Any]]
) -> dict[str, str]:
    """The datasets behind the zone's value, behind the reference it is compared with (e.g. a
    district uses the padrón, the region the CM census) and behind the extra indicators."""
    versions: dict[str, str] = {}
    for source in [reference_row, *extra_rows, row]:  # the zone's own value wins a clash
        if source is not None:
            versions.update(source["inputs"].get("dataset_versions", {}))
    return versions


def split_bound(
    features: Iterable[dict[str, Any]],
) -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    """The main feature of each row, by feature_id, and the extra features of each row, by row
    key; both in feature_id order."""
    ordered = sorted(features, key=lambda f: f["feature_id"])
    primaries = {f["feature_id"]: f for f in ordered if f["gap_row"]["role"] == "primary"}
    extras: dict[str, list[dict[str, Any]]] = {}
    for f in ordered:
        if f["gap_row"]["role"] == "extra":
            extras.setdefault(f["gap_row"]["row"], []).append(f)
    return primaries, extras


def extras_at(
    level: TerritoryLevel,
    extras: list[dict[str, Any]],
    values: dict[tuple[str, str], dict[str, Any]],
) -> list[Measured]:
    """The extra indicators computed at this level; one not computed there yet is left out."""
    return [
        Measured(feature, value)
        for feature in extras
        if (value := values.get((feature["feature_id"], level.value))) is not None
    ]


def missing_row_warnings(present: Iterable[GapRowKey], level: TerritoryLevel) -> list[str]:
    """One warning per expected row the list does not carry because it is not computed at this
    level yet. That is not SIN_DATOS, which is a row computed with no data for the zone."""
    carried = set(present)
    return [
        f"{ErrorCode.INSUFFICIENT_DATA.value}: row {key.value} not computed at {level.value} "
        "level yet"
        for key in ROW_ORDER
        if key not in carried
    ]


def _union(refs: Iterable[DatasetRef]) -> list[DatasetRef]:
    unique = {r.dataset_id: r for r in refs}
    return [unique[k] for k in sorted(unique)]


def _values(
    conn: Connection, features: list[str], level: TerritoryLevel, code: str
) -> dict[tuple[str, str], dict[str, Any]]:
    params = {
        "features": features,
        "level": level.value,
        "code": code,
        "region_level": REGION_LEVEL,
        "region_code": REGION_CODE,
    }
    return {
        (r["feature_id"], r["territory_level"]): dict(r)
        for r in conn.execute(_VALUES, params).mappings().all()
    }


def _build_rows(
    conn: Connection,
    zone: ZoneContext,
    primaries: dict[str, dict[str, Any]],
    extras: dict[str, list[dict[str, Any]]],
    values: dict[tuple[str, str], dict[str, Any]],
) -> tuple[list[GapRow], list[str], list[dict[str, Any]]]:
    """The rows computed at this level in display order, warnings for rows not computed or not
    classifiable, and the value rows the list uses (they set its data version)."""
    rows: list[GapRow] = []
    warnings: list[str] = []
    used: list[dict[str, Any]] = []
    computed_rows: set[GapRowKey] = set()
    level = zone.level
    for feature_id, feature in primaries.items():
        row = values.get((feature_id, level.value))
        if row is None:
            continue  # not computed at this level yet: the row is absent, not SIN_DATOS
        key = GapRowKey(feature["gap_row"]["row"])
        computed_rows.add(key)
        reference_row = values.get((feature_id, REGION_LEVEL))
        row_extras = extras_at(level, extras.get(key.value, []), values)
        try:
            rows.append(_gap_row(conn, Measured(feature, row), reference_row, row_extras, zone))
        except UnclassifiableError as exc:
            warnings.append(str(exc))
            continue
        used.extend([row, *(e.value for e in row_extras)])
        if reference_row is not None:
            used.append(reference_row)
    warnings.extend(missing_row_warnings(computed_rows, level))
    rows.sort(key=lambda r: ROW_ORDER.index(r.row))
    return rows, warnings, used


def zone_gap_list(
    conn: Connection, level: TerritoryLevel, code: str
) -> tuple[ZoneGapList, list[str], str | None]:
    """The list, warnings for rows not computed at this level or that could not be classified,
    and the data version (the latest computation among the values the list shows)."""
    zone = zone_ref(conn, level, code)
    primaries, extras = split_bound(dict(f) for f in conn.execute(_BOUND_FEATURES).mappings().all())
    queried = sorted([*primaries, *(f["feature_id"] for fs in extras.values() for f in fs)])
    values = _values(conn, queried, level, code)
    context = ZoneContext(level, code, load_references(conn, sorted(primaries)))
    rows, warnings, used = _build_rows(conn, context, primaries, extras, values)
    computed = [v["computed_at"] for v in used]
    data_version = max(computed).date().isoformat() if computed else None
    gap_list = ZoneGapList(
        zone=zone,
        method=GAP_METHOD,
        rows=rows,
        datasets=_union(d for r in rows for d in r.datasets),
    )
    return gap_list, warnings, data_version
