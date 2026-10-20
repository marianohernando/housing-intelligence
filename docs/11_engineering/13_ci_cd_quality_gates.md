# CI/CD Quality Gates

## Pull Request required
- lint;
- typecheck;
- unit;
- contract;
- changed-data tests;
- changed-feature tests;
- secret scan;
- dependency scan.

## Main
Additionally:
- integration;
- DB/PostGIS;
- API;
- selected E2E;
- build images.

## Nightly
- full data quality;
- model/RAG/JEV eval;
- visual regression;
- load sample;
- drift checks.

## Release
- staging full smoke;
- backup verified;
- migration dry-run;
- rollback ready;
- enabled capability gate results.

## Rule
Do not bypass failed required checks for demo pressure without explicit Decision Log entry.
