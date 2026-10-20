# Configuración y Secretos

## Config
Variables:
- DATABASE_URL
- REDIS_URL
- OBJECT_STORAGE_*
- JEV_*
- LLM_*
- MAP_*
- ROUTING_*

## Regla
`.env.example` contiene nombres, nunca valores reales.

## Secretos
En producción usar secret manager del proveedor.

## Feature flags
Para:
- modelos experimentales;
- capas nuevas;
- JEV workflow;
- PRO modules.
