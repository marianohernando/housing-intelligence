# Evolución del Residential Fit

## Fase 0 — Baseline experto
- hard constraints;
- pesos;
- normalización;
- rules;
- explicación completa.

## Fase 1 — Pesos dinámicos
La IA/JEV interpreta preferencias y genera configuración estructurada.

## Fase 2 — Learning-to-Rank
Cuando exista suficiente feedback:
- LightGBM/LambdaRank o equivalente;
- baseline experto como feature/guardrail;
- golden profiles;
- offline evaluation.

## Fase 3 — Personalización
Ranking adaptado a comportamiento real del usuario y cohortes.

## Regla
El ML no elimina el baseline.
Si el modelo falla o no tiene confianza:
volver a sistema interpretable.

## Objetivo
Más precisión sin perder explicabilidad.
