"""The region's air quality zones (D-237): each municipio's name -> its INE code and its zone.

The CM file names municipios in capitals with the article first («EL ÁLAMO»); the geography
names them «Álamo (El)». Both are compared by the key a person would type (`name_key`) of the
readable name, so the accents do not matter. When that fails, a name may lack the article
(«ACEBEDA» is «Acebeda (La)») or the second part of a joint name («HORCAJO DE LA SIERRA» is
«Horcajo de la Sierra-Aoslos»): those keys only count when they point to one municipio.
"""

from dataclasses import dataclass

import pandas as pd

from hi_contracts.catalog.pipeline import AirQualityZonesPipeline
from hi_domain.geo.names import ARTICLES, display_name, name_key
from hi_ingestion.pipelines.places.quality import CheckResult, QualityReport

ZONE_COLUMNS = ["municipio_ine", "zone_code", "zone_name"]
PROBLEM_COLUMNS = ["municipio_name", "reason"]


@dataclass(frozen=True)
class ZoneTable:
    zones: pd.DataFrame
    problems: pd.DataFrame
    region_municipios: int


def _alias_keys(official: str) -> set[str]:
    """«Acebeda (La)» or «ACEBEDA, LA» -> «acebeda»; «Horcajo de la Sierra-Aoslos» ->
    «horcajo de la sierra»."""
    readable = display_name(official)
    article, _, rest = readable.partition(" ")
    base = rest if article in ARTICLES and rest else readable
    return {name_key(base), name_key(base.split("-")[0])} - {name_key(readable)}


def _index(municipios: dict[str, str]) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    exact: dict[str, list[str]] = {}
    alias: dict[str, list[str]] = {}
    for code, name in municipios.items():
        exact.setdefault(name_key(display_name(name)), []).append(code)
        for key in _alias_keys(name):
            alias.setdefault(key, []).append(code)
    return exact, alias


def zone_table(
    frame: pd.DataFrame, spec: AirQualityZonesPipeline, municipios: dict[str, str]
) -> ZoneTable:
    """`municipios` is the official geography: INE code -> name."""
    exact, alias = _index(municipios)
    rows: list[tuple[str, str, str]] = []
    problems: list[tuple[str, str]] = []
    for record in frame.to_dict("records"):
        name = str(record[spec.municipio_name_column])
        key = name_key(display_name(name))
        codes = exact.get(key) or alias.get(key, [])
        if len(codes) != 1:
            problems.append((name, "no municipio" if not codes else f"several: {codes}"))
            continue
        zone_name = display_name(str(record[spec.zone_name_column]))
        rows.append((codes[0], str(record[spec.zone_code_column]), zone_name))
    zones = pd.DataFrame(rows, columns=ZONE_COLUMNS).sort_values("municipio_ine")
    return ZoneTable(zones, pd.DataFrame(problems, columns=PROBLEM_COLUMNS), len(municipios))


def run_zones_quality(result: ZoneTable) -> QualityReport:
    repeated = result.zones.loc[result.zones["municipio_ine"].duplicated(), "municipio_ine"]
    covered = result.zones["municipio_ine"].nunique()
    return QualityReport(
        [
            CheckResult(
                "every_name_matched",
                True,
                result.problems.empty,
                {"problems": result.problems.to_dict("records")},  # pyright: ignore[reportUnknownMemberType]
            ),
            CheckResult(
                "one_zone_per_municipio", True, repeated.empty, {"repeated": repeated.tolist()}
            ),
            CheckResult(
                "every_municipio_in_a_zone",
                True,
                covered == result.region_municipios > 0,
                {"covered": covered, "region": result.region_municipios},
            ),
        ]
    )
