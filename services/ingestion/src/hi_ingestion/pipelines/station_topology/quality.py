"""QA for a station topology: the whole network is there, ids are unique, every grade read."""

from hi_contracts.catalog.pipeline import StationTopologyPipeline
from hi_ingestion.pipelines.places.quality import CheckResult, QualityReport
from hi_ingestion.pipelines.station_topology.normalize import Topology

MAX_QUARANTINE_RATIO = 0.05


def run_topology_quality(topology: Topology, spec: StationTopologyPipeline) -> QualityReport:
    frame = topology.frame
    kept = len(frame) + len(topology.quarantine)
    ratio = len(topology.quarantine) / kept if kept else 1.0
    duplicated = int(frame["station_id"].duplicated().sum())
    return QualityReport(
        [
            CheckResult(
                "rows_in_range",
                True,
                spec.min_rows <= len(frame) <= spec.max_rows,
                {"stations": len(frame), "min": spec.min_rows, "max": spec.max_rows},
            ),
            CheckResult("unique_ids", True, duplicated == 0, {"duplicates": duplicated}),
            CheckResult(
                "grades_read",
                True,
                ratio <= MAX_QUARANTINE_RATIO,
                {
                    "quarantined": len(topology.quarantine),
                    "ratio": round(ratio, 4),
                    "rows": topology.quarantine.to_dict("records"),  # pyright: ignore[reportUnknownMemberType]
                },
            ),
            CheckResult(
                "step_free_counts",
                False,
                True,
                {"by_reading": frame["step_free"].value_counts().to_dict()},  # pyright: ignore[reportUnknownMemberType]
            ),
        ]
    )
