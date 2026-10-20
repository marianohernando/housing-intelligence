# Null / Missingness Contract

## Nunca
`NULL` no puede significar cinco cosas distintas.

## Estados canónicos
- `NOT_APPLICABLE`
- `SOURCE_NO_COVERAGE`
- `SOURCE_MISSING`
- `TEMPORARILY_UNAVAILABLE`
- `STALE`
- `PARSE_ERROR`
- `ENTITY_NOT_RESOLVED`
- `ESTIMATION_NOT_ALLOWED`
- `UNKNOWN`

## Genuinely absent
Si una fuente fiable confirma que no existe un servicio:
guardar valor observado 0 + evidence.

Eso es distinto de:
“no sabemos si existe”.

## Uso en scoring
- observado 0 puede penalizar;
- unknown reduce confidence;
- parse_error genera alerta;
- stale puede usar último valor válido con warning según política.
