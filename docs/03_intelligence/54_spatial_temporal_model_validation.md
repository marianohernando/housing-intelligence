# Spatial & Temporal Model Validation

## Problem
Random train/test split can leak neighboring Madrid areas.

## Required evaluation
- spatial holdout;
- temporal holdout;
- municipality/district robustness;
- rare-segment evaluation.

## Price/model baseline
Compare against:
- global median;
- area median;
- simple linear/tree baseline.

## Promotion
A complex model must beat a simpler baseline materially and remain stable across geography/time.

## Rule
No model promoted based solely on random CV.
