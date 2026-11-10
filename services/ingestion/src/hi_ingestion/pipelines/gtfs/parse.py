"""GTFS zip -> one row per stop or parent station with its service on the reference day."""

from pathlib import Path

import pandas as pd

from hi_contracts.catalog.pipeline import GtfsFeedPipeline
from hi_ingestion.pipelines.gtfs.feed import iter_stop_times, open_feed, read_tables
from hi_ingestion.pipelines.gtfs.frequency import (
    PeakWindow,
    boarding_events,
    expand_frequencies,
    stop_service_table,
)
from hi_ingestion.pipelines.gtfs.service_day import reference_day

# Feed-level facts kept on every row so quality checks can read them; never published.
FEED_STAT_COLUMNS = [
    "reference_trips",
    "reference_candidate_days",
    "reference_stop_times",
    "invalid_stop_times",
]


def parse_feed(path: Path, spec: GtfsFeedPipeline) -> pd.DataFrame:
    with open_feed(path) as archive:
        tables = read_tables(archive)
        day = reference_day(tables, spec.reference_weekday)
        trips = tables.trips.loc[tables.trips["service_id"].isin(sorted(day.services)), "trip_id"]
        chunks = list(iter_stop_times(archive, set(trips)))
    stop_times = pd.concat(chunks, ignore_index=True)
    events, invalid = boarding_events(stop_times)
    if spec.expand_frequencies:
        events = expand_frequencies(events, tables.frequencies)
    peak = PeakWindow.from_clock(spec.peak_start, spec.peak_end)
    table = stop_service_table(tables, events, peak, day, spec.mode)
    return table.assign(
        reference_trips=day.active_trips,
        reference_candidate_days=day.candidate_days,
        reference_stop_times=len(stop_times),
        invalid_stop_times=invalid,
    )
