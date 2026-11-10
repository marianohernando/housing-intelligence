"""Pick the reference service day of a feed and the services running on it."""

from dataclasses import dataclass
from datetime import date, timedelta

from hi_ingestion.pipelines.gtfs.feed import GtfsFeedError, GtfsTables

WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
ADDED, REMOVED = "1", "2"


@dataclass(frozen=True)
class ServiceDay:
    service_date: date
    services: frozenset[str]
    active_trips: int
    candidate_days: int
    feed_start: date
    feed_end: date


def parse_gtfs_time(value: str) -> int | None:
    """'7:05:00' or '25:10:00' -> seconds after the service day's midnight; None if invalid."""
    parts = value.strip().split(":")
    if len(parts) != 3 or not all(p.isdigit() for p in parts):
        return None
    hours, minutes, seconds = (int(p) for p in parts)
    if minutes > 59 or seconds > 59:
        return None
    return hours * 3600 + minutes * 60 + seconds


def parse_gtfs_date(value: str) -> date:
    raw = value.strip()
    try:
        return date(int(raw[:4]), int(raw[4:6]), int(raw[6:8]))
    except ValueError as exc:
        msg = f"invalid GTFS date {value!r}"
        raise GtfsFeedError(msg) from exc


def validity_window(tables: GtfsTables) -> tuple[date, date]:
    added = tables.calendar_dates.loc[tables.calendar_dates["exception_type"].str.strip() == ADDED]
    raw = [
        *tables.calendar["start_date"].tolist(),
        *tables.calendar["end_date"].tolist(),
        *added["date"].tolist(),
    ]
    dates = [parse_gtfs_date(v) for v in raw if str(v).strip()]
    if not dates:
        raise GtfsFeedError("feed declares no service dates")
    return min(dates), max(dates)


def active_services(tables: GtfsTables, day: date) -> set[str]:
    key = day.strftime("%Y%m%d")
    calendar = tables.calendar
    runs = (
        (calendar[WEEKDAYS[day.weekday()]].str.strip() == "1")
        & (calendar["start_date"].str.strip() <= key)
        & (calendar["end_date"].str.strip() >= key)
    )
    exceptions = tables.calendar_dates.loc[tables.calendar_dates["date"].str.strip() == key]
    kind = exceptions["exception_type"].str.strip()
    added = set(exceptions.loc[kind == ADDED, "service_id"])
    removed = set(exceptions.loc[kind == REMOVED, "service_id"])
    return (set(calendar.loc[runs, "service_id"]) | added) - removed


def reference_day(tables: GtfsTables, weekday: str) -> ServiceDay:
    """Median `weekday` (by active trips) inside the feed's own validity window.

    The median skips holidays (few trips) and one-off special days (extra trips), and depends
    only on the feed, so the same file always yields the same reference day.
    """
    start, end = validity_window(tables)
    trips_per_service = tables.trips["service_id"].value_counts()
    day = start + timedelta(days=(WEEKDAYS.index(weekday) - start.weekday()) % 7)
    candidates: list[tuple[int, date, frozenset[str]]] = []
    while day <= end:
        services = active_services(tables, day)
        trips = int(trips_per_service.reindex(sorted(services)).fillna(0).sum())
        if trips:
            candidates.append((trips, day, frozenset(services)))
        day += timedelta(days=7)
    if not candidates:
        msg = f"no {weekday} with service between {start} and {end}"
        raise GtfsFeedError(msg)
    candidates.sort(key=lambda c: (c[0], c[1]))
    trips, chosen, services = candidates[len(candidates) // 2]
    return ServiceDay(chosen, services, trips, len(candidates), start, end)
