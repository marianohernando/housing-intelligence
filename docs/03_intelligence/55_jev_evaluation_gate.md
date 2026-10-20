# JEV Evaluation Gate

## Each JEV workflow has
- typed labels;
- golden set;
- high/medium/low confidence policy;
- confusion matrix;
- fallback.

## Initial target
For auto-accepted HIGH-confidence decisions:
- precision target >= 98% on reviewed golden set.

MEDIUM:
- validation/rerank/fallback.

LOW:
- escalate or abstain.

## Critical domains
No JEV auto-action may:
- change hard sensitive constraints;
- alter exact numeric facts;
- merge entities ambiguously without evidence.
