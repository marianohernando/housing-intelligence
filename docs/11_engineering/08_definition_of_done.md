# Definition of Done — v0.4.0

## Any code task
- implementation;
- typed contracts;
- unit tests;
- integration/contract tests where relevant;
- error/degraded path;
- logs/metrics;
- security/privacy review proportional to change;
- docs;
- no secrets;
- lint/typecheck;
- acceptance criteria;
- relevant Quality Gate still green.

## Dataset
- source registry;
- license/terms status;
- Bronze snapshot;
- parser;
- Silver schema;
- data tests;
- geospatial tests if relevant;
- lineage;
- freshness;
- null semantics;
- attribution;
- fallback.

## Feature
- dictionary contract;
- source;
- formula;
- units;
- geo/time;
- confidence;
- tests/invariants;
- version;
- consumers.

## Model
- dataset/feature versions;
- baseline;
- spatial/temporal eval;
- calibration;
- fairness review;
- latency/cost;
- registry;
- rollback.

## UX
- loading;
- empty;
- error;
- degraded;
- mobile;
- keyboard/accessibility;
- analytics privacy.

## PRO
- RBAC;
- tenant isolation;
- audit;
- export permissions.

## Release
Not done until phase/capability evidence exists under `evidence/`.
