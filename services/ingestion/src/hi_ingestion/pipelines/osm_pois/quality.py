"""QA for OSM points of interest: a plausible number, unique ids, every declared class present
and few places without a usable point."""

from hi_contracts.catalog.pipeline import OsmPoisPipeline
from hi_ingestion.pipelines.places.normalize import Places
from hi_ingestion.pipelines.places.quality import CheckResult, QualityReport

MAX_QUARANTINE_RATIO = 0.02


def run_pois_quality(places: Places, spec: OsmPoisPipeline) -> QualityReport:
    frame = places.frame
    kept = len(frame) + len(places.quarantine)
    by_class = frame["subcategory"].value_counts().to_dict() if len(frame) else {}
    counts = {c.subcategory: int(by_class.get(c.subcategory, 0)) for c in spec.classes}
    return QualityReport(
        [
            CheckResult(
                "place_count_plausible",
                True,
                spec.min_places <= len(frame) <= spec.max_places,
                {"places": len(frame), "min": spec.min_places, "max": spec.max_places},
            ),
            CheckResult(
                "ids_unique",
                True,
                bool(frame["external_id"].is_unique) if len(frame) else True,
            ),
            CheckResult("every_class_has_places", True, all(counts.values()), counts),
            CheckResult(
                "quarantine_ratio",
                True,
                len(places.quarantine) <= MAX_QUARANTINE_RATIO * max(kept, 1),
                {"quarantined": len(places.quarantine), "max_ratio": MAX_QUARANTINE_RATIO},
            ),
        ]
    )
