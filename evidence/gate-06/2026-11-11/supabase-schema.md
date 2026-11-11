# OPS-001 paso 0 — esquema en Supabase (2026-11-11)

Proyecto `ilvbivfnqvfqslbbiuts` (West EU, Ireland, Nano), conectado por Session pooler `aws-0-eu-west-1.pooler.supabase.com:5432` con `sslmode=require`. La contraseña está en `.env` (`SUPABASE_DATABASE_URL`); la añadió Mariano y nunca ha pasado por el chat ni por la salida de comandos.

| Paso | Resultado |
|---|---|
| Conexión (`SELECT 1`, salida sin la contraseña) | OK: Postgres 17.11, 0 tablas en `public` |
| `alembic upgrade head` (salida enmascarada) | 0001 → 0002, `alembic current` = `0002 (head)` |
| MCP `list_tables` | 14 tablas en `public`, todas vacías salvo `alembic_version` (1 fila) |
| MCP `list_extensions` | `postgis` 3.3.7 y `vector` 0.8.2 en el schema `extensions` (en local, PostGIS 3.6) |
| MCP `get_advisors` (security), tras la 0002 | ERROR `rls_disabled_in_public` en las 14 tablas: la Data API (PostgREST) las exponía a `anon`/`authenticated` |
| Migración 0003 (D-197, OK de Mariano) | Aplicada en local y en Supabase: `alembic current` = `0003 (head)` |
| MCP `get_advisors` (security), tras la 0003 | Solo queda el aviso INFO `rls_enabled_no_policy` (14), que es el estado buscado |
| `supabase_sync.sh demo` (salida enmascarada, `supabase-sync-demo.txt`) | 9 tablas en 12,9 s. Los conteos coinciden con la base local: geo_admin_unit 4.973, place_master 24.334 (education 3.851, health 4.500, social 1.001, transport 14.982), place_source_alias 24.334, feature_value 2.148. **Tamaño: 100 MB** de 500 |
| Geometrías en remoto (MCP) | SRID 4326 y `ST_IsValid` correcto en todas. Transporte con sección: 14.749 de 14.982 (las 233 que faltan están fuera de la CM, igual que en local) |
| Data API con la clave publishable | `GET /rest/v1/{source_registry,place_master,feature_value,geo_admin_unit}` → `[]` con HTTP 200 aunque hay filas: RLS bloquea a `anon` |

## Arreglos que hizo falta aplicar
- `infra/migrations/env.py`: ConfigParser interpreta el `%`, así que una contraseña codificada en la URL rompía Alembic (`ValueError`). Ahora se escapa a `%%`. Comprobado en modo offline con una URL que lleva `%40`, `%23` y `%25`.
- `Makefile` (`supabase-migrate`): la receta ya no imprime la URL con la contraseña (`@`).

## Pendiente (OPS-001, 17 nov)
- Volver a ejecutar `make supabase-sync PROFILE=demo` cuando CORE-005 y GAP-001 cambien features y lugares. Es idempotente porque trunca y copia.
- Desplegar la API y la web de la demo apuntando a esta base.
