"""D-241: the plain stage of a Madrid planning area from the readings of its four phases."""

import pytest

from hi_domain.urbanism import DevelopmentStage, Reading, development_stage


@pytest.mark.parametrize(
    ("readings", "stage"),
    [
        (["done", "done", "done", "done"], None),
        (["done", "done", "done", "in_progress"], DevelopmentStage.WORKS),
        (["done", "in_progress", "done", "in_progress"], DevelopmentStage.WORKS),
        (["done", "in_progress", "in_progress", "not_started"], DevelopmentStage.PROCESSING),
        (["in_progress", "not_started", "not_started", "not_started"], DevelopmentStage.PROCESSING),
        (["done", "done", "done", "not_started"], DevelopmentStage.NOT_STARTED),
        (["not_started", "done", "done", "done"], DevelopmentStage.NOT_STARTED),
    ],
)
def test_stage_reads_the_most_advanced_phase_under_way(
    readings: list[Reading], stage: DevelopmentStage | None
) -> None:
    assert development_stage(readings) == stage


def test_an_area_needs_its_phases() -> None:
    with pytest.raises(ValueError, match="phases"):
        development_stage([])
