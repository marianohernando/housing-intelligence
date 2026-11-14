"""Where a planning area of Madrid is in its development (pure, unit tested): D-241.

The Ayuntamiento's register (VEDA) gives each area the state of four phases, in order:
planning, management, urbanization project and urbanization works. Each state reads as done,
in progress or not started. The zone view says it in three plain stages.
"""

from collections.abc import Sequence
from enum import StrEnum
from typing import Literal

Reading = Literal["done", "in_progress", "not_started"]


class DevelopmentStage(StrEnum):
    """Plain stages of an unfinished area, from the most to the least advanced."""

    WORKS = "obras"  # the urbanization works are under way
    PROCESSING = "tramitacion"  # an earlier phase is under way (plan, management or project)
    NOT_STARTED = "sin_empezar"  # nothing under way: the next phase has not started


STAGE_ORDER: tuple[DevelopmentStage, ...] = tuple(DevelopmentStage)


def development_stage(readings: Sequence[Reading]) -> DevelopmentStage | None:
    """The stage of an area from its phases in order; None when every phase is done.

    Works under way (the last phase in progress) win over anything else; any other phase in
    progress is «en tramitación»; otherwise something is pending and nothing moves.
    """
    if not readings:
        msg = "an area needs the reading of its phases"
        raise ValueError(msg)
    if all(r == "done" for r in readings):
        return None
    if readings[-1] == "in_progress":
        return DevelopmentStage.WORKS
    if "in_progress" in readings:
        return DevelopmentStage.PROCESSING
    return DevelopmentStage.NOT_STARTED
