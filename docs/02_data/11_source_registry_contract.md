# Source Registry Contract

## Tabla conceptual: `source_registry`

```sql
source_id              text primary key
name                   text not null
provider               text not null
source_type            text not null
base_url               text
license_name           text
license_url            text
commercial_use         boolean
redistribution_allowed boolean
trust_tier             text
default_confidence     numeric
update_frequency       text
geographic_scope       text
terms_reviewed_at      timestamptz
active                 boolean
notes                  text
created_at             timestamptz
updated_at             timestamptz
```

## `trust_tier`
- `A_OFFICIAL`
- `B_OPEN_STRUCTURED`
- `C_COMMERCIAL_API`
- `D_SCRAPED`

## Regla de conflicto
Por defecto:
A > B > C > D

No aplicar ciegamente: si una fuente oficial está desactualizada y otra tiene mayor actualidad, almacenar ambas y decidir a nivel de métrica mediante una política explícita.

## Campos obligatorios
No entra una fuente a producción sin:
- licencia revisada;
- frecuencia;
- scope geográfico;
- owner/provider;
- trust tier.
