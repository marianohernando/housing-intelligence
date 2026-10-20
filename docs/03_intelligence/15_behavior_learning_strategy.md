# Estrategia de Aprendizaje por Comportamiento

## Fase 1 — Analytics
Registrar:
- viewed;
- saved;
- rejected;
- rejection reason;
- scenario modified;
- return visit.

No entrenar automáticamente al principio.

## Fase 2 — Labels
Crear labels derivados:
- positive_preference;
- hard_reject;
- budget_tolerance;
- commute_tolerance.

## Fase 3 — Ranking ML
Con volumen suficiente:
- learning-to-rank;
- cohort-specific models;
- personalization.

## Riesgos
- popularity bias;
- selection bias;
- feedback loops;
- cold start.

## Protección
- mantener baseline de reglas;
- exploration;
- offline evaluation;
- shadow models;
- no sustituir score base sin mejora demostrada.
