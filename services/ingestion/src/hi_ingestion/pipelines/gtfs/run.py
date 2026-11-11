"""GTFS feeds on the generic runner: stops become transport places with service attributes."""

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
from sqlalchemy import Engine

from hi_contracts.catalog.enums import PlaceCategory
from hi_contracts.catalog.pipeline import CsvFormat, GtfsFeedPipeline, PointsPipeline
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.common import DATA_DIR, RunSummary
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.gtfs.parse import parse_feed
from hi_ingestion.pipelines.places.normalize import Places, normalize_places
from hi_ingestion.pipelines.places.publish import replace_places
from hi_ingestion.pipelines.places.quality import CheckResult, QualityReport, run_quality
from hi_ingestion.pipelines.places.run import write_places_silver
from hi_ingestion.pipelines.runner import PipelineSteps, run_pipeline

PARSER_VERSION = "gtfs-1.1.0"
SERVICE_ATTRIBUTES = [
    "departures_day",
    "departures_peak_per_hour",
    "headway_peak_min",
    "headway_basis",
    "first_departure",
    "last_departure",
    "routes",
    "n_routes",
    "wheelchair_boarding",
    "service_date",
    "feed_end_date",
]
MAX_PEAK_DEPARTURES_PER_HOUR = 1200  # 20 a minute at one stop or station: beyond is a parse bug
MIN_HEADWAY_MIN = 0.5
MAX_INVALID_STOP_TIMES_RATIO = 0.001


@dataclass(frozen=True)
class TransportPlaces:
    places: Places
    feed: dict[str, Any]


def points_spec(spec: GtfsFeedPipeline) -> PointsPipeline:
    """The stop table produced by parse_feed, described as a point register."""
    return PointsPipeline(
        kind="points_csv",
        dataset_id=spec.dataset_id,
        resource_role=spec.resource_role,
        category=PlaceCategory.TRANSPORT,
        id_column="stop_id",
        name_column="stop_name",
        subcategory_column="mode",
        row_filters={"has_service": ["yes"]},
        x_column="stop_lon",
        y_column="stop_lat",
        crs="EPSG:4326",
        attribute_columns=SERVICE_ATTRIBUTES,
    )


def _feed_facts(frame: pd.DataFrame) -> dict[str, Any]:
    first = frame.iloc[0] if len(frame) else None
    return {
        "service_date": None if first is None else first["service_date"],
        "feed_end_date": None if first is None else first["feed_end_date"],
        "reference_trips": 0 if first is None else int(first["reference_trips"]),
        "candidate_days": 0 if first is None else int(first["reference_candidate_days"]),
        "stop_times": 0 if first is None else int(first["reference_stop_times"]),
        "invalid_stop_times": 0 if first is None else int(first["invalid_stop_times"]),
    }


def _normalize(frame: pd.DataFrame, spec: GtfsFeedPipeline) -> TransportPlaces:
    return TransportPlaces(normalize_places(frame, points_spec(spec)), _feed_facts(frame))


def _service_checks(result: TransportPlaces) -> list[CheckResult]:
    attrs: list[dict[str, Any]] = result.places.frame["attributes"].tolist()
    peak = max((float(a.get("departures_peak_per_hour", 0)) for a in attrs), default=0.0)
    headways = [float(a["headway_peak_min"]) for a in attrs if "headway_peak_min" in a]
    feed = result.feed
    rows = feed["stop_times"] or 1
    feed_end = feed["feed_end_date"] or ""
    return [
        CheckResult(
            "reference_service_day",
            True,
            feed["reference_trips"] > 0 and feed["candidate_days"] > 0,
            {k: feed[k] for k in ("service_date", "reference_trips", "candidate_days")},
        ),
        CheckResult(
            "stop_times_parsed",
            True,
            feed["invalid_stop_times"] / rows <= MAX_INVALID_STOP_TIMES_RATIO,
            {k: feed[k] for k in ("stop_times", "invalid_stop_times")},
        ),
        CheckResult(
            "peak_departures_plausible",
            True,
            peak <= MAX_PEAK_DEPARTURES_PER_HOUR,
            {"max_departures_peak_per_hour": peak, "limit": MAX_PEAK_DEPARTURES_PER_HOUR},
        ),
        CheckResult(
            "headway_plausible",
            True,
            min(headways, default=MIN_HEADWAY_MIN) >= MIN_HEADWAY_MIN,
            {
                "min_headway_peak_min": min(headways, default=None),
                "with_peak_service": len(headways),
            },
        ),
        CheckResult(
            "feed_current",
            False,
            feed_end >= datetime.now(UTC).date().isoformat(),
            {"feed_end_date": feed_end, "note": "expired feeds stay the latest official schedule"},
        ),
    ]


def run_transport_quality(result: TransportPlaces, spec: GtfsFeedPipeline) -> QualityReport:
    report = run_quality(result.places, points_spec(spec))
    return QualityReport([*report.checks, *_service_checks(result)])


def _counts(result: TransportPlaces) -> dict[str, Any]:
    return {
        "places_normalized": len(result.places.frame),
        "quarantined": len(result.places.quarantine),
        "without_service_on_reference_day": result.places.filtered_out.get(
            "has_service_not_allowed", 0
        ),
        "service_date": result.feed["service_date"],
    }


def run_gtfs_pipeline(
    engine: Engine,
    catalog: Catalog,
    spec: GtfsFeedPipeline,
    source: FetchedFile | None = None,
    *,
    evidence_root: Path | None,
    data_dir: Path = DATA_DIR,
) -> RunSummary:
    source_id = catalog.datasets[spec.dataset_id].source_id
    steps: PipelineSteps[TransportPlaces] = PipelineSteps(
        parser_version=PARSER_VERSION,
        csv=CsvFormat(),
        resource_role=spec.resource_role,
        normalize=lambda frame: _normalize(frame, spec),
        quarantine=lambda result: result.places.quarantine,
        quality=lambda result: run_transport_quality(result, spec).to_dict(),
        counts=_counts,
        write_silver=lambda result, directory: write_places_silver(result.places, directory),
        publish=lambda session, result, version_id: replace_places(
            session, result.places, spec.dataset_id, source_id, version_id
        ),
        parse=lambda path: parse_feed(path, spec),
    )
    return run_pipeline(
        engine,
        catalog,
        spec.dataset_id,
        steps,
        source,
        evidence_root=evidence_root,
        data_dir=data_dir,
    )
