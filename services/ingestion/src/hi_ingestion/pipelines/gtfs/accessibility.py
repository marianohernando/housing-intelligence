"""Step-free stations (D-223): a GTFS feed's stations read the CRTM topology by official code.

The GTFS `wheelchair_boarding` of the CRTM does not follow the GTFS meaning (2 is published for
every Metro Ligero stop, a network the CRTM and the Comunidad de Madrid declare 100 %
accessible), so it is never read. Each station takes instead the accessibility grade of the
topology station(s) it contains: an interchange is one place in the GTFS and one station per
line in the topology, so it takes the least accessible of them. A station whose key is missing
from the topology stays unknown: unknown is never step-free.
"""

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
from sqlalchemy import Engine, text

from hi_contracts.catalog.pipeline import (
    GtfsFeedPipeline,
    StationAccessibilityLink,
    StationTopologyPipeline,
)
from hi_ingestion.bronze import REPO_ROOT
from hi_ingestion.catalog.loader import Catalog
from hi_ingestion.pipelines.fetch import FetchedFile
from hi_ingestion.pipelines.places.run import directory_input
from hi_ingestion.pipelines.station_topology.normalize import TOPOLOGY_FILE, read_topology

STEP_FREE_ORDER = ("no", "partial", "yes")  # least accessible first
ACCESSIBILITY_ATTRIBUTES = ["step_free", "topology_station_ids", "step_free_source"]

_LAST_VALID = text(
    """
    SELECT bronze_manifest_path, version_label
      FROM dataset_version
     WHERE dataset_id = :dataset_id AND is_last_valid
    """
)


@dataclass(frozen=True)
class StationGrades:
    dataset_id: str
    version_label: str
    step_free: Mapping[str, str]  # topology key -> yes / partial / no

    @property
    def source(self) -> str:
        return f"{self.dataset_id} {self.version_label}"


def station_step_free(
    members: Sequence[str], pattern: re.Pattern[str], grades: StationGrades
) -> tuple[str | None, list[str]]:
    """The reading of a station (its stops' topology keys, least accessible first), or None
    when no stop has a key or one of its keys is not in the topology."""
    keys = sorted({m.group(1) for stop in members if (m := pattern.match(stop))})
    if not keys or any(k not in grades.step_free for k in keys):
        return None, keys
    return min((grades.step_free[k] for k in keys), key=STEP_FREE_ORDER.index), keys


def grades_from_frame(
    frame: pd.DataFrame, link: StationAccessibilityLink, version_label: str
) -> StationGrades:
    """Key -> reading. Two stations with the same key (an operator code shared by two lines)
    keep the least accessible, as an interchange does."""
    keys = frame[link.match].astype(str).str.strip()
    step_free: dict[str, str] = {}
    for key, value in zip(keys, frame["step_free"], strict=True):
        reading = str(value)
        if key:
            previous = step_free.get(key, reading)
            step_free[key] = min(previous, reading, key=STEP_FREE_ORDER.index)
    return StationGrades(link.dataset_id, version_label, step_free)


def attach_step_free(
    frame: pd.DataFrame, link: StationAccessibilityLink, grades: StationGrades | None
) -> pd.DataFrame:
    """Add the ACCESSIBILITY_ATTRIBUTES columns from each row's `member_stop_ids`."""
    pattern = re.compile(link.stop_id_pattern)
    readings: list[str | None] = []
    keys: list[list[str]] = []
    for members in frame["member_stop_ids"]:
        if grades is None:
            reading, found = None, []
        else:
            reading, found = station_step_free(list(members), pattern, grades)
        readings.append(reading)
        keys.append(found)
    return frame.assign(
        step_free=pd.Series(readings, index=frame.index, dtype=object),
        topology_station_ids=pd.Series(keys, index=frame.index, dtype=object),
        step_free_source=None if grades is None else grades.source,
    )


def load_station_grades(
    engine: Engine, catalog: Catalog, spec: GtfsFeedPipeline
) -> tuple[StationGrades | None, list[FetchedFile]]:
    """The last valid Silver of the topology the feed declares, and its Bronze input (lineage).
    A topology never ingested leaves every station unknown, and the quality report says so."""
    link = spec.station_accessibility
    if link is None:
        return None, []
    if not isinstance(catalog.pipelines.get(link.dataset_id), StationTopologyPipeline):
        msg = f"{spec.dataset_id}: {link.dataset_id} is not a station_topology pipeline"
        raise TypeError(msg)
    with engine.connect() as conn:
        row = conn.execute(_LAST_VALID, {"dataset_id": link.dataset_id}).first()
    if row is None:
        return None, []
    manifest_path = Path(str(row.bronze_manifest_path))
    if not manifest_path.is_absolute():
        manifest_path = REPO_ROOT / manifest_path
    manifest = json.loads(manifest_path.read_text())
    frame = read_topology(manifest_path.parent / TOPOLOGY_FILE)
    grades = grades_from_frame(frame, link, str(row.version_label))
    return grades, [directory_input(manifest, kind="topology")]
