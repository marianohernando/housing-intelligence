# Phase Quality Gates — NO AVANZAR SIN PASS

## Gate 0 — Repository / Foundation
Must pass:
- lint;
- typecheck;
- unit test scaffold;
- migrations up/down or forward-fix test;
- Docker/local boot;
- secret scan;
- CI green.

Evidence:
`evidence/gate-00/`.

---

## Gate 1 — Source / Bronze ingestion
For every P0 source:
- registry complete;
- license status;
- snapshot checksum;
- parser deterministic;
- schema test;
- freshness metadata;
- retry/failure path.

PASS only if last-valid snapshot survives a broken new ingestion.

---

## Gate 2 — Silver canonical / Geo
- entity resolution golden cases;
- CRS/geometry validation;
- Madrid bounds;
- duplicate controls;
- H3/admin mappings;
- address resolution confidence;
- random manual sample.

Critical geometry error = FAIL.

---

## Gate 3 — Metrics / Feature Store
Every production feature:
- Feature Dictionary entry;
- source lineage;
- unit;
- null semantics;
- deterministic calculation;
- range/invariant tests;
- temporal/geographic resolution;
- confidence.

No undocumented feature can enter model matrix.

---

## Gate 4 — Core math
Affordability / Total Cost / constraints / Residential Fit baseline:
- golden cases;
- monotonicity;
- PASS/FAIL/UNKNOWN;
- budget curve;
- anchor weighting;
- missing domain;
- confidence.
All critical invariants = 100% pass.

---

## Gate 5 — PUBLIC flow
E2E:
map → chat/chips → scenario → recommendation → explanation → edit → save.

Must pass:
- no PII in analytics/logs;
- error recovery;
- anonymous mode;
- account mode;
- accessible keyboard route.

---

## Gate 6 — Map / Digital Twin
- vector tile correctness;
- layers;
- zoom transitions;
- H3/buildings;
- selection;
- performance budget;
- visual regression;
- layer failure isolation.

---

## Gate 7 — Inclusive Living
Golden scenarios:
- visual accessibility;
- reduced mobility;
- sensory/low-noise;
- cognitive/simple-route.

Must prove:
- no diagnosis inference;
- UNKNOWN not PASS;
- explanation uses evidence;
- accessible UI itself passes.

---

## Gate 8 — Place Model / ML
- baseline comparison;
- spatial CV;
- temporal CV if possible;
- registry;
- reproducibility;
- no leakage;
- inference latency;
- rollback.

Complex model must materially beat baseline.

---

## Gate 9 — JEV / RAG / LLM
- JEV golden precision;
- RAG grounding/citations;
- prompt injection;
- tool schema validation;
- no arbitrary SQL;
- provider failure fallback.

---

## Gate 10 — PRO
E2E:
workspace → site/thesis → analysis → gap → recommendation → report.

Security:
- tenant isolation 100%;
- RBAC;
- export permissions;
- private upload handling.

---

## Gate 11 — API / MCP
- OpenAPI contract;
- auth/scopes;
- rate limit;
- idempotency where needed;
- MCP tool schemas;
- evidence metadata;
- abuse limits.

---

## Gate 12 — System / Production readiness
- load;
- security;
- backup restore;
- migration;
- observability;
- cost budget;
- browser/mobile;
- WCAG;
- data degradation.

---

## Gate 13 — DATAMAD release
- all enabled capabilities pass;
- demo 10 consecutive clean runs;
- external-network-off smoke;
- source manifest;
- repo pack;
- no secrets;
- pitch evidence.
