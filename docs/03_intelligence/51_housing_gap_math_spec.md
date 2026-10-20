# Housing Gap — Baseline Mathematical Specification

## Goal
Estimate compatible unmet residential need for segment `s` in area `g`.

## Baseline
`CompatibleDemand(g,s) - EffectiveCompatibleSupply(g,s)`

## Demand
Derived from:
- household population;
- affordability;
- household/type fit;
- tenure;
- mobility/service constraints;
- observed platform intent as separate signal.

## Supply
Distinguish:
- stock;
- available supply;
- expected pipeline;
- turnover;
- suitable supply.

## Do not subtract raw stock
A dwelling that is not available/compatible is not effective supply.

## Outputs
- absolute unmet compatible households;
- ratio vs effective supply;
- normalized Gap Score;
- confidence;
- drivers.

## Platform intent
Never mix platform-user demand with population demand without labeling.
Maintain:
- `structural_demand`
- `observed_platform_intent`

## Calibration
Use historical transactions/absorption/listings when legally available.
