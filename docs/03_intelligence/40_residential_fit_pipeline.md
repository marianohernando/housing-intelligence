# Residential Fit Pipeline

```text
ScenarioState
  ↓
1. Validate profile
  ↓
2. Hard constraints
  ↓
3. Candidate generation
  ↓
4. Base feature scoring
  ↓
5. Confidence adjustment
  ↓
6. Contextual scoring
  ↓
7. ML ranker (si está activo)
  ↓
8. JEV reranking cuando aporte
  ↓
9. Diversity / Pareto selection
  ↓
10. Explainability bundle
```

## Candidate generation
Reducir primero por geografía, presupuesto máximo, tenure, dormitorios mínimos, accesibilidad verificable y commute máximo.

## Subscores
- affordability
- mobility
- housing
- services
- education
- health
- environment
- safety
- accessibility
- lifestyle

## Fail-safe
Si ML/JEV falla, volver al baseline estructurado y explicable.
