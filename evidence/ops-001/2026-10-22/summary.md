# OPS-001 — Supabase remoto preparado (2026-10-22)

Estado: **preparado y simulado; pendiente de la contraseña de la base de datos** para ejecutarlo contra `ilvbivfnqvfqslbbiuts`.

## Comandos (cuando `SUPABASE_DATABASE_URL` esté en `.env`)
```bash
make supabase-migrate              # alembic upgrade head contra Supabase
make supabase-sync PROFILE=demo    # geografía, equipamientos, features y registros
make supabase-sync PROFILE=full    # además observaciones y vínculos H3
```

## Simulación local
Base vacía `housing_supasim` en el mismo Postgres 17, migrada con `make supabase-migrate` y cargada
por un rol **sin superusuario** (como el `postgres` de Supabase):

| Perfil | Tablas | Tamaño remoto |
|---|---|---|
| demo | 9 | 77 MB |
| full | 12 | 276 MB |

Límite del plan gratuito: 500 MB. Re-ejecutar es idempotente (trunca y copia).

## Decisiones
- Se copia desde la base local validada con `pg_dump --data-only` en vez de re-ejecutar los pipelines en remoto: mismos datos que pasaron los Quality Gates y sin descargar fuentes dos veces.
- Sin `--disable-triggers` (requiere superusuario): las claves foráneas se validan al final de cada COPY.
- Las conexiones de la aplicación fijan `search_path TO public, extensions`, así que no dependen de la configuración por defecto de la base.
