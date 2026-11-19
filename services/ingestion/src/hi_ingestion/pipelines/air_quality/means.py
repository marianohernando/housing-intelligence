"""Hourly levels of a network -> the annual mean of one pollutant per station (D-237).

Both the CM and the Ayuntamiento de Madrid publish one row per station, pollutant and day with
H01..H24 and their flags V01..V24 (the CM in lower case, with a decimal comma). A station's code
is province (2) + municipio (3) + station (3): 28065014 is Getafe.
"""

import calendar
from dataclasses import dataclass

import numpy as np
import pandas as pd
from numpy.typing import NDArray

from hi_contracts.catalog.pipeline import AirQualityHourlyPipeline
from hi_ingestion.pipelines.places.quality import CheckResult, QualityReport

HOURS = range(1, 25)
KEY_COLUMNS = ["provincia", "municipio", "estacion", "magnitud", "ano", "mes", "dia"]
MEAN_COLUMNS = ["station_code", "year", "magnitude", "mean", "valid_hours", "capture"]
PROBLEM_COLUMNS = ["station_code", "mes", "dia", "hour", "raw", "reason"]
FloatGrid = NDArray[np.float64]
BoolGrid = NDArray[np.bool_]


@dataclass(frozen=True)
class StationMeans:
    """`means` has one row per station with the pollutant; `problems` lists the hours flagged
    valid whose value is not a number (they do not count)."""

    means: pd.DataFrame
    problems: pd.DataFrame
    missing_columns: list[str]
    rows_of_year: int


def hours_in_year(year: int) -> int:
    return (366 if calendar.isleap(year) else 365) * 24


def _station_code(frame: pd.DataFrame) -> pd.Series:
    return (
        frame["provincia"].str.zfill(2)
        + frame["municipio"].str.zfill(3)
        + frame["estacion"].str.zfill(3)
    )


def _values(frame: pd.DataFrame, spec: AirQualityHourlyPipeline) -> tuple[FloatGrid, BoolGrid]:
    """Rows x 24 hours: the level (NaN when unreadable) and whether the hour is flagged valid."""
    text = frame[[f"h{h:02d}" for h in HOURS]].to_numpy(dtype=str)
    flat = pd.Series(np.char.replace(text, spec.csv.decimal, ".").ravel())
    numbers = np.asarray(pd.to_numeric(flat, errors="coerce"), dtype=np.float64)
    flags = np.asarray(frame[[f"v{h:02d}" for h in HOURS]].to_numpy(dtype=str) == spec.valid_flag)
    return numbers.reshape(text.shape), flags.astype(np.bool_)


def _problems(
    frame: pd.DataFrame, codes: NDArray[np.str_], levels: FloatGrid, flags: BoolGrid
) -> pd.DataFrame:
    bad_rows, bad_hours = np.nonzero(flags & np.isnan(levels))
    raw = frame[[f"h{h:02d}" for h in HOURS]].to_numpy(dtype=str)
    return pd.DataFrame(
        {
            "station_code": codes[bad_rows],
            "mes": frame["mes"].to_numpy(dtype=str)[bad_rows],
            "dia": frame["dia"].to_numpy(dtype=str)[bad_rows],
            "hour": bad_hours + 1,
            "raw": raw[bad_rows, bad_hours],
            "reason": "valid flag without a number",
        },
        columns=PROBLEM_COLUMNS,
    )


def station_means(frame: pd.DataFrame, spec: AirQualityHourlyPipeline) -> StationMeans:
    frame = frame.rename(columns=str.lower)
    needed = [*KEY_COLUMNS, *(f"h{h:02d}" for h in HOURS), *(f"v{h:02d}" for h in HOURS)]
    missing = [c for c in needed if c not in frame.columns]
    if missing:
        empty = pd.DataFrame(columns=MEAN_COLUMNS)
        return StationMeans(empty, pd.DataFrame(columns=PROBLEM_COLUMNS), missing, 0)
    year = frame["ano"].to_numpy(dtype=int) == spec.year
    rows = frame.loc[year & (frame["magnitud"].to_numpy(dtype=int) == spec.magnitude)]
    if rows.empty:  # the quality gate says which: no row of the year, or no station
        empty = pd.DataFrame(columns=MEAN_COLUMNS)
        return StationMeans(empty, pd.DataFrame(columns=PROBLEM_COLUMNS), [], int(year.sum()))
    levels, flags = _values(rows, spec)
    valid = flags & ~np.isnan(levels)
    codes = _station_code(rows).to_numpy(dtype=str)
    stations, station_of_row = np.unique(codes, return_inverse=True)
    total = np.bincount(station_of_row, np.where(valid, levels, 0.0).sum(axis=1), len(stations))
    count = np.bincount(station_of_row, valid.sum(axis=1), len(stations))
    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.where(count > 0, total / count, np.nan)
    means = pd.DataFrame(
        {
            "station_code": stations,
            "year": spec.year,
            "magnitude": spec.magnitude,
            "mean": mean,
            "valid_hours": count.astype(int),
            "capture": count / hours_in_year(spec.year),
        },
        columns=MEAN_COLUMNS,
    )
    problems = _problems(rows, codes, levels, flags)
    return StationMeans(means, problems, [], int(year.sum()))


def run_means_quality(result: StationMeans, spec: AirQualityHourlyPipeline) -> QualityReport:
    means = result.means.dropna(subset=["mean"])
    implausible = means.loc[(means["mean"] < 0) | (means["mean"] > spec.max_mean)]
    return QualityReport(
        [
            CheckResult(
                "hourly_layout",
                True,
                not result.missing_columns,
                {"missing_columns": result.missing_columns},
            ),
            CheckResult(
                "year_published",
                True,
                result.rows_of_year > 0,
                {"year": spec.year, "rows": result.rows_of_year},
            ),
            CheckResult(
                "enough_stations",
                True,
                len(means) >= spec.min_stations,
                {"stations": len(means), "min": spec.min_stations},
            ),
            CheckResult(
                "plausible_means",
                True,
                implausible.empty,
                {"implausible": implausible["station_code"].tolist(), "max": spec.max_mean},
            ),
            CheckResult(
                "capture_by_station",
                False,
                True,
                {
                    "capture": dict(
                        zip(means["station_code"], means["capture"].round(3), strict=True)
                    )
                },
            ),
            CheckResult("unreadable_valid_hours", False, True, {"hours": len(result.problems)}),
        ]
    )
