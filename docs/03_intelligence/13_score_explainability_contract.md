# Score Explainability Contract

## Todo score importante debe exponer

```json
{
  "score": 87,
  "scale": "0-100",
  "components": [
    {"id": "affordability", "score": 92, "weight": 0.30},
    {"id": "mobility", "score": 80, "weight": 0.20}
  ],
  "top_positive_reasons": [],
  "top_negative_reasons": [],
  "confidence": 0.89,
  "data_freshness": {},
  "methodology_version": "1.0"
}
```

## Regla
Nunca mostrar un score sin:
- escala;
- definición;
- componentes;
- fecha/frescura;
- confidence cuando corresponda.

## LLM
El LLM puede convertir razones estructuradas en lenguaje natural, pero no alterar pesos ni score.
