# OPS-001 paso 0 — esquema en Supabase (2026-11-11)

Proyecto `ilvbivfnqvfqslbbiuts` (West EU, Ireland, Nano), conectado por Session pooler `aws-0-eu-west-1.pooler.supabase.com:5432` con `sslmode=require`. La contraseña está en `.env` (`SUPABASE_DATABASE_URL`); la añadió Mariano y nunca ha pasado por el chat ni por la salida de comandos.

| Paso | Resultado |
|---|---|
| Conexión (`SELECT 1`, salida sin la contraseña) | OK: Postgres 17.11, 0 tablas en `public` |
| `alembic upgrade head` (salida enmascarada) | 0001 → 0002, `alembic current` = `0002 (head)` |
| MCP `list_tables` | 14 tablas en `public`, todas vacías salvo `alembic_version` (1 fila) |
| MCP `list_extensions` | `postgis` 3.3.7 y `vector` 0.8.2 en el schema `extensions` (en local, PostGIS 3.6) |
| MCP `get_advisors` (security) | **ERROR `rls_disabled_in_public` en las 14 tablas**: la Data API (PostgREST) las expone a `anon`/`authenticated`. Hoy no hay datos. Pendiente de la decisión de Mariano antes de `supabase-sync` |

## Arreglos que hizo falta aplicar
- `infra/migrations/env.py`: ConfigParser interpreta el `%`, así que una contraseña codificada en la URL rompía Alembic (`ValueError`). Ahora se escapa a `%%`. Comprobado en modo offline con una URL que lleva `%40`, `%23` y `%25`.
- `Makefile` (`supabase-migrate`): la receta ya no imprime la URL con la contraseña (`@`).

## Pendiente (OPS-001)
- RLS (ver arriba) antes de cargar datos.
- `make supabase-sync PROFILE=demo` después de CORE-005 y GAP-001.
