# services/features — Feature Store (Gold)

Calcula features deterministas a partir de `metric_observation` y `place_master`.
Cada feature se declara en `data/catalog/features/<feature_id>.yaml`; el YAML elige un método
genérico (`metric_value`, `metric_share`, `metric_weighted_mean`, `places_per_population`,
`place_attribute_per_population`) y sus parámetros. Ningún dataset ni fórmula está en el código.

```bash
uv run hi-features compute            # todas
uv run hi-features compute --feature renta_per_capita
```
