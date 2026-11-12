"""Reality Check (CORE-003, D-215): how many more zones appear when one condition is relaxed
and the others stay. Each option carries the relaxed scenario, so the web can apply it.

Relaxing never removes a zone (a property test checks it): more budget, a few more minutes
on foot, a wish instead of a must, or no time limit for a trip that is not computed yet.
"""

import math
from collections.abc import Sequence

from hi_contracts.public import (
    BudgetKind,
    ConstraintStatus,
    NeedKey,
    RealityCheck,
    Relaxation,
    ScenarioState,
)
from hi_contracts.public.scenario import BUY_RANGE_EUR, RENT_RANGE_EUR
from hi_domain.affordability import euros
from hi_domain.fit import NEED_TEXT, ZoneData, ZoneFit, statuses

BUDGET_STEP_SHARE, BUDGET_STEP_ROUND = 0.10, 50  # +10 % of the rent, rounded up to 50 €
BUY_STEP_ROUND = 10_000  # buying: +10 % of the budget, rounded up to 10.000 € (D-227)
WALK_STEP_MINUTES, WALK_MAX_MINUTES = 5, 60


def budget_step(amount: int, rounding: int = BUDGET_STEP_ROUND) -> int:
    steps = math.ceil(amount * BUDGET_STEP_SHARE / rounding)
    return max(rounding, steps * rounding)


def relaxed(scenario: ScenarioState, constraint_id: str) -> tuple[str, ScenarioState] | None:
    """The scenario with one condition relaxed and its label; None if it cannot relax more."""
    if constraint_id == "budget" and scenario.budget is not None:
        return _relax_budget(scenario)
    if constraint_id.startswith("near:"):
        return _relax_near(scenario, NeedKey(constraint_id.removeprefix("near:")))
    if constraint_id.startswith("commute:"):
        return _relax_commute(scenario, int(constraint_id.removeprefix("commute:")))
    return None


def _relax_budget(scenario: ScenarioState) -> tuple[str, ScenarioState] | None:
    budget = scenario.budget
    if budget is None:
        return None
    buying = budget.kind is BudgetKind.BUY
    rounding, top = (
        (BUY_STEP_ROUND, BUY_RANGE_EUR[1]) if buying else (BUDGET_STEP_ROUND, RENT_RANGE_EUR[1])
    )
    amount = min(budget.amount_eur + budget_step(budget.amount_eur, rounding), top)
    if amount == budget.amount_eur:
        return None
    step = amount - budget.amount_eur
    new_budget = budget.model_copy(update={"amount_eur": amount})
    label = f"+{euros(step)}" if buying else f"+{euros(step)}/mes"
    return label, scenario.model_copy(update={"budget": new_budget})


def _relax_near(scenario: ScenarioState, need: NeedKey) -> tuple[str, ScenarioState]:
    """A few more minutes on foot; at the limit, the service becomes a wish, not a must."""
    index = next(i for i, item in enumerate(scenario.nearby) if item.need is need)
    item = scenario.nearby[index]
    label = NEED_TEXT[need][0]
    if item.max_walk_minutes < WALK_MAX_MINUTES:
        minutes = min(item.max_walk_minutes + WALK_STEP_MINUTES, WALK_MAX_MINUTES)
        text = f"+{minutes - item.max_walk_minutes} min a pie hasta {label.lower()}"
        changed = item.model_copy(update={"max_walk_minutes": minutes})
    else:
        text = f"{label} cerca como preferencia, no como requisito"
        changed = item.model_copy(update={"required": False})
    nearby = [*scenario.nearby[:index], changed, *scenario.nearby[index + 1 :]]
    return text, scenario.model_copy(update={"nearby": nearby})


def _relax_commute(scenario: ScenarioState, index: int) -> tuple[str, ScenarioState]:
    anchors = list(scenario.anchors)
    anchor = anchors[index]
    anchors[index] = anchor.model_copy(update={"max_minutes": None})
    text = f"Sin límite de tiempo hasta {anchor.label}"
    return text, scenario.model_copy(update={"anchors": anchors})


def passing(scenario: ScenarioState, zones: Sequence[ZoneData]) -> int:
    return sum(all(s is ConstraintStatus.PASS for s in statuses(scenario, z)) for z in zones)


def binding_constraint(fits: Sequence[ZoneFit]) -> str | None:
    """The condition that leaves out the most zones: those where it is not PASS, whatever the
    other conditions say (a first-in-order condition wins a tie)."""
    excluded: dict[str, int] = {}
    for fit in fits:
        for check in fit.constraints:
            excluded.setdefault(check.constraint_id, 0)
            if check.status is not ConstraintStatus.PASS:
                excluded[check.constraint_id] += 1
    if not excluded or max(excluded.values()) == 0:
        return None
    return max(excluded, key=lambda key: excluded[key])  # first in order wins a tie


def reality_check(
    scenario: ScenarioState, zones: Sequence[ZoneData], fits: Sequence[ZoneFit]
) -> RealityCheck:
    passing_now = sum(f.passes_all for f in fits)
    unknown = sum(
        not f.failed and not f.passes_all for f in fits
    )  # no FAIL but some UNKNOWN: never passing
    options: list[Relaxation] = []
    ids = [c.constraint_id for c in fits[0].constraints] if fits else []
    for constraint_id in ids:
        option = relaxed(scenario, constraint_id)
        if option is None:
            continue
        label, relaxed_scenario = option
        count = passing(relaxed_scenario, zones)
        options.append(
            Relaxation(
                constraint_id=constraint_id,
                label=label,
                zones_if_relaxed=count,
                added_zones=count - passing_now,
                relaxed_scenario=relaxed_scenario,
            )
        )
    return RealityCheck(
        zones_evaluated=len(fits),
        zones_passing=passing_now,
        zones_unknown=unknown,
        binding_constraint=binding_constraint(fits),
        relaxations=sorted(options, key=lambda o: -o.added_zones),
    )
