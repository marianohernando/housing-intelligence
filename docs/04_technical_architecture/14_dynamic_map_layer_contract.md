# Dynamic Map Layer Contract

## Objetivo
Permitir que MCP/IA construyan análisis visuales temporales sin programar una capa nueva cada vez.

## Capa dinámica
No es JavaScript arbitrario.

Contrato:

```json
{
  "layer_id": "dynamic_uuid",
  "title": "Gap familiar + Cercanías",
  "geometry_type": "h3",
  "metric": "housing_gap_family",
  "filters": [],
  "style": {
    "render": "extrusion",
    "height_metric": "compatible_unmet_demand",
    "color_metric": "gap_score"
  },
  "legend": {},
  "ttl_seconds": 3600
}
```

## Flujo
MCP tool:
`create_analysis_layer`

1. valida consulta;
2. resuelve métricas permitidas;
3. ejecuta service/query;
4. genera dataset/tiles temporales;
5. devuelve `layer_id`;
6. frontend renderiza.

## Seguridad
- whitelist de métricas;
- límites de filas;
- timeout;
- no SQL libre;
- scopes PRO;
- auditoría.

## Futuro
La misma definición puede exportarse para clientes/chat que soporten mapas embebidos.
