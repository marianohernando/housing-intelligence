# Configuración y Secretos

## Config
Variables:
- DATABASE_URL
- DB_POOL_SIZE, DB_MAX_OVERFLOW y DB_PREPARED_STATEMENTS: pool de cada proceso y prepared statements de psycopg; `false` con el pooler de Supabase en modo transacción (D-219)
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
