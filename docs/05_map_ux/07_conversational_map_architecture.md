# Arquitectura del Mapa Conversacional

## Concepto
Chat y mapa comparten un estado estructurado.

```text
User language
↓
Intent / JEV / LLM
↓
Map Command Plan
↓
Domain Tools
↓
MapState
↓
Renderer
```

## MapState conceptual

```json
{
  "viewport": {},
  "active_layers": [],
  "filters": {},
  "selected_entities": [],
  "comparison": [],
  "scenario": {},
  "time_context": null,
  "visual_mode": "PUBLIC"
}
```

## Map Command Plan
Ejemplo:
```json
{
  "commands": [
    {"tool": "find_best_areas", "args": {}},
    {"map_action": "set_layer", "layer": "residential_fit"},
    {"map_action": "highlight", "entity_ids": []},
    {"map_action": "fly_to", "target": "..."}
  ]
}
```

## Regla de seguridad
El modelo no envía JavaScript al navegador.
Solo comandos validados contra schemas.

## Objetivo futuro
Permitir superficies/mapas renderizables también dentro de interfaces de agentes/chat cuando el cliente lo soporte, sin depender de esa capacidad para el producto principal.
