# Capability Flags & Controlled Scope Cuts

## Objetivo
Poder construir grande y recortar sin romper el sistema.

## Capability flags
Ejemplos:
- enable_place_embeddings
- enable_forecasting
- enable_dynamic_mcp_layers
- enable_homefit_url_ingestion
- enable_emerging_opportunity
- enable_scenario_engine
- enable_realtime_transport
- enable_knowledge_graph

## Reglas
- flags no deben cambiar contratos públicos de forma incoherente;
- cada capability tiene fallback;
- tests cubren enabled/disabled cuando sea crítica;
- UI oculta features desactivadas.

## Fallback examples
### Realtime transport off
Usar GTFS estático.

### Forecast off
Mostrar histórico + tendencia.

### Place embeddings off
Usar similarity por features normalizadas.

### Scenario engine off
Mostrar análisis estático de proyecto.

### Advanced accessibility data missing
Usar necesidades que sí tengan cobertura + warning.

## Scope-cut registry
Mantener documento con:
- capability;
- valor;
- coste;
- dependencia;
- riesgo;
- fallback;
- demo relevance;
- cut order.

## Regla
Cortar por coste/riesgo, no por importancia visual únicamente.
