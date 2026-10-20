# Source Conflict Resolution

## Problema
Dos fuentes pueden dar valores distintos.

## Nunca
No elegir automáticamente “la última” sin semántica.

## Política por métrica
Cada `metric_id` define:
- preferred_source;
- accepted_fallbacks;
- freshness rules;
- resolution rules;
- reconciliation method.

## Ejemplo
Población:
preferir fuente oficial más granular/compatible con el periodo.

POIs:
fuente oficial para existencia/tipo;
OSM puede complementar geometría/atributos.

## DATAMAD
Cuando un dato de Comunidad de Madrid es apto para la funcionalidad:
debe permanecer como fuente core y aparecer en lineage.

## Discrepancia
Guardar:
- values_by_source;
- selected_value;
- selection_reason;
- selection_policy_version.
