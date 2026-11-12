"""Public transport arrive-by search on a time-expanded timetable (CORE-009)."""

import numpy as np
from hypothesis import given, settings
from hypothesis import strategies as st

from hi_domain.access.transit import (
    Access,
    ArriveByNetwork,
    Footpaths,
    StopTimes,
    latest_leave,
    zone_medians,
)

H = 3600
M = 60


def timetable(
    trips: list[list[tuple[int, int]]],
    n_stops: int,
    no_pickup: frozenset[tuple[int, int]] = frozenset(),
) -> StopTimes:
    """trips[i] = [(stop, time), ...] in order; no_pickup = {(trip, position)}."""
    trip, stop, time, boardable = [], [], [], []
    for i, calls in enumerate(trips):
        for k, (s, t) in enumerate(calls):
            trip.append(i)
            stop.append(s)
            time.append(t)
            boardable.append((i, k) not in no_pickup)
    return StopTimes(
        trip=np.array(trip, dtype=np.int64),
        stop=np.array(stop, dtype=np.int64),
        time=np.array(time, dtype=np.int64),
        boardable=np.array(boardable, dtype=bool),
        n_stops=n_stops,
    )


NO_FOOTPATHS = Footpaths(np.array([], np.int64), np.array([], np.int64), np.array([], np.int64))


def latest(
    tt: StopTimes,
    hub: list[tuple[int, int]],
    arrive_by: int,
    footpaths: Footpaths = NO_FOOTPATHS,
    transfer_s: int = 2 * M,
) -> list[float]:
    network = ArriveByNetwork.build(tt, footpaths, transfer_s)
    stops = np.array([s for s, _ in hub], dtype=np.int64)
    walk = np.array([w for _, w in hub], dtype=np.int64)
    return network.latest_departures(stops, walk, arrive_by).tolist()


TRIP_A = [(0, 8 * H), (1, 8 * H + 10 * M), (2, 8 * H + 20 * M)]


def test_one_change_with_time_to_make_it() -> None:
    tt = timetable([TRIP_A, [(2, 8 * H + 25 * M), (3, 8 * H + 35 * M)]], 4)
    got = latest(tt, [(3, 0)], arrive_by=8 * H + 40 * M)
    assert got[:3] == [8 * H, 8 * H + 10 * M, 8 * H + 25 * M]
    assert got[3] == -np.inf  # already there: walking only, not a departure


def test_arriving_after_the_deadline_reaches_nothing() -> None:
    tt = timetable([TRIP_A, [(2, 8 * H + 25 * M), (3, 8 * H + 35 * M)]], 4)
    assert latest(tt, [(3, 0)], arrive_by=8 * H + 30 * M) == [-np.inf] * 4


def test_a_change_needs_the_transfer_time() -> None:
    tt = timetable([TRIP_A, [(2, 8 * H + 21 * M), (3, 8 * H + 35 * M)]], 4)
    got = latest(tt, [(3, 0)], arrive_by=9 * H)
    assert got[0] == -np.inf and got[1] == -np.inf
    assert got[2] == 8 * H + 21 * M


def test_walking_between_stops_to_change() -> None:
    tt = timetable([TRIP_A, [(4, 8 * H + 26 * M), (3, 8 * H + 35 * M)]], 5)
    walk = Footpaths(np.array([2]), np.array([4]), np.array([5 * M]))
    assert latest(tt, [(3, 0)], 9 * H, walk)[0] == 8 * H
    slow = Footpaths(np.array([2]), np.array([4]), np.array([7 * M]))
    assert latest(tt, [(3, 0)], 9 * H, slow)[0] == -np.inf


def test_the_walk_from_the_last_stop_counts() -> None:
    tt = timetable([TRIP_A], 3)
    assert latest(tt, [(2, 10 * M)], arrive_by=8 * H + 30 * M)[0] == 8 * H
    assert latest(tt, [(2, 11 * M)], arrive_by=8 * H + 30 * M)[0] == -np.inf


def test_the_later_of_two_trips_is_the_latest_departure() -> None:
    later = [(0, 8 * H + 5 * M), (1, 8 * H + 15 * M), (2, 8 * H + 25 * M)]
    tt = timetable([TRIP_A, later], 3)
    assert latest(tt, [(2, 0)], arrive_by=9 * H)[0] == 8 * H + 5 * M


def test_a_stop_without_pickup_cannot_be_boarded_but_the_trip_goes_through() -> None:
    tt = timetable([TRIP_A], 3, no_pickup=frozenset({(0, 1)}))
    got = latest(tt, [(2, 0)], arrive_by=9 * H)
    assert got[0] == 8 * H
    assert got[1] == -np.inf


def test_leave_time_is_the_best_access_stop() -> None:
    by_stop = np.array([8 * H, 8 * H + 10 * M, -np.inf])
    access = Access(
        origin=np.array([0, 0, 1, 2], dtype=np.int64),
        stop=np.array([0, 1, 2, 0], dtype=np.int64),
        seconds=np.array([5 * M, 12 * M, 1 * M, 30 * M], dtype=np.int64),
        n_origins=4,
    )
    leave = latest_leave(by_stop, access).tolist()
    assert leave[0] == 8 * H - 2 * M  # stop 1 at 8:10 minus 12 min beats stop 0 at 8:00 minus 5
    assert leave[1] == -np.inf  # its only stop reaches nothing
    assert leave[2] == 8 * H - 30 * M
    assert leave[3] == -np.inf  # no stop within reach


@st.composite
def random_timetables(draw: st.DrawFn) -> tuple[StopTimes, int]:
    n_stops = draw(st.integers(3, 6))
    trips: list[list[tuple[int, int]]] = []
    for _ in range(draw(st.integers(1, 6))):
        stops = draw(st.lists(st.integers(0, n_stops - 1), min_size=2, max_size=4, unique=True))
        start = draw(st.integers(7 * H, 9 * H))
        gaps = draw(st.lists(st.integers(1 * M, 15 * M), min_size=len(stops), max_size=len(stops)))
        times = (start + np.cumsum(gaps) - gaps[0]).tolist()
        trips.append(list(zip(stops, times, strict=True)))
    return timetable(trips, n_stops), n_stops


@settings(max_examples=60, deadline=None)
@given(random_timetables(), st.integers(8 * H, 10 * H), st.integers(0, 10 * M))
def test_a_later_deadline_never_makes_a_departure_earlier(
    case: tuple[StopTimes, int], arrive_by: int, extra: int
) -> None:
    tt, n_stops = case
    hub = [(n_stops - 1, 0)]
    early = np.array(latest(tt, hub, arrive_by))
    late = np.array(latest(tt, hub, arrive_by + extra))
    assert np.all(late >= early)
    assert np.all(early <= arrive_by)


@settings(max_examples=60, deadline=None)
@given(random_timetables(), st.integers(8 * H, 10 * H))
def test_an_extra_trip_never_makes_a_departure_earlier(
    case: tuple[StopTimes, int], arrive_by: int
) -> None:
    tt, n_stops = case
    hub = [(n_stops - 1, 0)]
    before = np.array(latest(tt, hub, arrive_by))
    extra = timetable([[(0, 8 * H), (n_stops - 1, 8 * H + 20 * M)]], n_stops)
    more = StopTimes(
        trip=np.concatenate([tt.trip, extra.trip + tt.trip.max() + 1]),
        stop=np.concatenate([tt.stop, extra.stop]),
        time=np.concatenate([tt.time, extra.time]),
        boardable=np.concatenate([tt.boardable, extra.boardable]),
        n_stops=n_stops,
    )
    after = np.array(latest(more, hub, arrive_by))
    assert np.all(after >= before)


def test_a_zone_is_the_median_of_its_origins_and_unreachable_ones_are_the_slowest() -> None:
    values = np.array([10.0, 30.0, np.inf, 20.0, np.inf, np.inf, 5.0])
    zone = np.array([0, 0, 0, 1, 1, 1, 3], dtype=np.int64)
    medians, counts, reached = zone_medians(values, zone, 4)
    assert medians[0] == 30.0  # 10, 30, inf
    assert medians[1] == np.inf  # most of it cannot make it
    assert medians[2] == np.inf and counts[2] == 0  # no origins
    assert medians[3] == 5.0
    assert counts.tolist() == [3, 3, 0, 1]
    assert reached.tolist() == [2, 1, 0, 1]


def test_a_trip_that_goes_back_in_time_is_never_a_shortcut() -> None:
    """Bad data: a bus «arriving» before it left must not let anyone leave later."""
    back = [(0, 8 * H + 50 * M), (1, 7 * H + 30 * M)]
    train = [(1, 7 * H + 35 * M), (2, 8 * H + 10 * M)]
    got = latest(timetable([back, train], 3), [(2, 0)], arrive_by=9 * H)
    assert got[0] == -np.inf
    assert got[1] == 7 * H + 35 * M
