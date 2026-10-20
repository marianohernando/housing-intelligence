# Model Evaluation Test Plan

## Required artifact
`model_eval.json`:
- model version;
- dataset version;
- feature set;
- baseline;
- metrics;
- spatial split;
- temporal split;
- segment metrics;
- calibration;
- latency;
- decision.

## Promotion statuses
EXPERIMENT → SHADOW → ACTIVE.

## Rollback
Previous ACTIVE artifact remains deployable.
