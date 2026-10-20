# Final-Product-First Execution Strategy

## Decisión
El proyecto se diseña y se intenta construir como producto final desde el inicio.

No se construye una arquitectura de “hackathon MVP” separada.

## Principio
Construir la versión completa.
Si el tiempo o la estabilidad lo exigen:
recortar funcionalidades de forma controlada.

Nunca:
- rehacer arquitectura para DATAMAD;
- crear mocks que luego haya que tirar;
- programar una versión paralela simplificada si puede evitarse.

## Arquitectura
Toda implementación debe pertenecer al producto final:
- mismo dominio;
- mismos contratos;
- mismos modelos;
- mismos repositorios;
- misma base de datos;
- mismo mapa;
- mismo API/MCP.

## Recorte por capas
Cada capability se clasifica:

### TIER 0 — Core no negociable
Debe funcionar sí o sí.
Ejemplos:
- datos Comunidad de Madrid;
- mapa;
- perfil/ScenarioState;
- Residential Fit;
- affordability;
- movilidad;
- explainability;
- Housing Gap base;
- lineage.

### TIER 1 — Producto fuerte
Objetivo de entrega.
Ejemplos:
- Place Model;
- accesibilidad;
- Reality Check;
- HomeFit;
- PRO;
- MCP;
- parcela/proyecto;
- 3D.

### TIER 2 — Diferenciadores avanzados
Construir si el core está estable.
Ejemplos:
- forecasting;
- timeline;
- Emerging Opportunity;
- dynamic layers;
- scenario engine;
- advanced RAG/GIS;
- multimodal temporal routing.

### TIER 3 — Futuro inmediato
Se puede dejar diseñado/semiconstruido:
- Knowledge Graph;
- full realtime transport;
- full financial engine;
- nationwide rollout;
- extreme automation.

## Regla de desarrollo
Nunca comenzar Tier 2 si Tier 0 tiene deuda crítica.

## Regla de demo
La demo puede ocultar capacidades no suficientemente estables, pero el código sigue perteneciendo al producto final.

## Definition of “cut”
Recortar significa:
- desactivar una capability;
- reducir cobertura;
- limitar un flujo;
- usar fallback estable;
no crear una arquitectura distinta.

## Objetivo
Llegar a DATAMAD con el máximo producto real posible, no con el mínimo producto aceptable.
