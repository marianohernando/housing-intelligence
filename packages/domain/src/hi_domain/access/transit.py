"""Public transport commute on a time-expanded timetable (CORE-009): «to be there by 9:00,
leave at …».

Every stop time of the reference day is an event with three nodes: the vehicle arriving (A),
the vehicle departing with the traveller on board (D) and the traveller on the platform ready
to board it (B). Edges are moves a traveller can make, always forward in time: ride to the
next stop (D -> A), stay on board (A -> D of the same event), board (B -> D), wait on the
platform for a later departure (B -> next B at that stop) and change, at the same stop after
`transfer_s` or walking to another stop, to the first departure after it (A -> B).

An arrive-by search reverses the edges and walks back from the arrivals at the destination's
stops that are early enough: every platform node it reaches can still make it, so the latest
one at each stop is when one must board there. Times stay absolute, so only reachability
matters (no weights). Pure logic over arrays.
"""

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

IntArray = NDArray[np.int64]
FloatArray = NDArray[np.float64]
BoolArray = NDArray[np.bool_]
_KEY = 10**6  # > any time of a service day in seconds (GTFS days may run past 24:00)


@dataclass(frozen=True)
class StopTimes:
    """One row per call of a trip at a stop on the reference day, in travel order per trip."""

    trip: IntArray
    stop: IntArray
    time: IntArray  # seconds after the service day's midnight (arrival taken as departure)
    boardable: BoolArray  # False where the timetable allows no pickup
    n_stops: int


@dataclass(frozen=True)
class Footpaths:
    """Walks between stops for a change, in seconds (one direction per row)."""

    origin: IntArray
    target: IntArray
    seconds: IntArray


@dataclass(frozen=True)
class Access:
    """Walks from origins (homes) to the stops near them, in seconds."""

    origin: IntArray
    stop: IntArray
    seconds: IntArray
    n_origins: int


def _ordered(stop_times: StopTimes) -> StopTimes:
    order = np.argsort(stop_times.trip, kind="stable")
    return StopTimes(
        stop_times.trip[order],
        stop_times.stop[order],
        stop_times.time[order],
        stop_times.boardable[order],
        stop_times.n_stops,
    )


def _change_edges(
    events: StopTimes, footpaths: Footpaths, transfer_s: int, boarding: IntArray
) -> tuple[IntArray, IntArray]:
    """A_i -> first boardable D at the target stop no earlier than the walk allows."""
    stops = np.arange(events.n_stops, dtype=np.int64)
    origin = np.concatenate([stops, footpaths.origin])
    target = np.concatenate([stops, footpaths.target])
    seconds = np.concatenate([np.full(events.n_stops, transfer_s), footpaths.seconds])
    by_origin = np.argsort(origin, kind="stable")
    origin, target, seconds = origin[by_origin], target[by_origin], seconds[by_origin]
    counts = np.bincount(origin, minlength=events.n_stops)
    starts = np.cumsum(counts) - counts
    per_event = counts[events.stop]
    event = np.repeat(np.arange(len(events.stop), dtype=np.int64), per_event)
    offset = np.arange(per_event.sum()) - np.repeat(np.cumsum(per_event) - per_event, per_event)
    path = starts[events.stop[event]] + offset
    query = target[path] * _KEY + events.time[event] + seconds[path]
    board_key = events.stop[boarding] * _KEY + events.time[boarding]
    pos = np.searchsorted(board_key, query, side="left")
    inside = pos < len(boarding)
    found = np.zeros(len(query), dtype=bool)
    found[inside] = events.stop[boarding[pos[inside]]] == target[path[inside]]
    return event[found], boarding[pos[found]]


@dataclass(frozen=True)
class ArriveByNetwork:
    events: StopTimes
    reverse: csr_matrix  # A 0..n-1, D n..2n-1, B 2n..3n-1; edges pointing backwards in time

    @classmethod
    def build(
        cls, stop_times: StopTimes, footpaths: Footpaths, transfer_s: int
    ) -> "ArriveByNetwork":
        events = _ordered(stop_times)
        n = len(events.stop)
        idx = np.arange(n, dtype=np.int64)
        same_trip = np.flatnonzero(events.trip[1:] == events.trip[:-1])
        boardable = np.flatnonzero(events.boardable)
        boarding = boardable[np.lexsort((events.time[boardable], events.stop[boardable]))]
        waits = np.flatnonzero(events.stop[boarding[1:]] == events.stop[boarding[:-1]])
        change_from, change_to = _change_edges(events, footpaths, transfer_s, boarding)
        tails = np.concatenate(
            [n + same_trip, idx, 2 * n + boardable, 2 * n + boarding[waits], change_from]
        )
        heads = np.concatenate(
            [same_trip + 1, n + idx, n + boardable, 2 * n + boarding[waits + 1], 2 * n + change_to]
        )
        ones = np.ones(len(tails), dtype=np.float64)
        forward = csr_matrix((ones, (tails, heads)), shape=(3 * n, 3 * n))
        return cls(events, forward.T.tocsr())

    def latest_departures(self, stops: IntArray, walk_s: IntArray, arrive_by: int) -> FloatArray:
        """Per stop, the latest boardable departure that still arrives by `arrive_by` at the
        destination (walking `walk_s` from `stops`); -inf where none does."""
        events = self.events
        latest = np.full(events.n_stops, -np.inf)
        egress = np.full(events.n_stops, np.iinfo(np.int64).max // 4, dtype=np.int64)
        np.minimum.at(egress, stops, walk_s)
        sources = np.flatnonzero(events.time + egress[events.stop] <= arrive_by)
        if len(sources) == 0:
            return latest
        dist = dijkstra(self.reverse, indices=sources, min_only=True, unweighted=True)
        n = len(events.stop)
        reached = np.flatnonzero(np.isfinite(dist[2 * n :]) & events.boardable)
        np.maximum.at(latest, events.stop[reached], events.time[reached].astype(np.float64))
        return latest


def latest_leave(by_stop: FloatArray, access: Access) -> FloatArray:
    """Per origin, the latest time to leave home: board at the best stop minus the walk to it."""
    leave = np.full(access.n_origins, -np.inf)
    np.maximum.at(leave, access.origin, by_stop[access.stop] - access.seconds)
    return leave
