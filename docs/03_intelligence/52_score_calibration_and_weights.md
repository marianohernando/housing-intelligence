# Score Calibration & Weight Governance

## Initial weights
Use expert priors, not arbitrary hidden values.

## Calibration sequence
1. expert baseline;
2. synthetic/golden profiles;
3. human review;
4. sensitivity analysis;
5. pilot users;
6. behavioral LTR.

## Requirements
- weights versioned;
- component contribution capped where needed;
- correlated feature groups prevented from double counting;
- hard constraints outside additive scoring.

## Sensitivity
Every release of scoring must answer:
- what changes top results most?
- does a ±10% weight change destabilize ranking?
- are rankings dominated by one domain?

## Gate
Reject scoring version with unexplained brittle ranking.
