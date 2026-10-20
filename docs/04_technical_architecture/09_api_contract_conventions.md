# API Contract Conventions

## Base
`/api/v1`

## Response envelope

```json
{
  "data": {},
  "meta": {
    "request_id": "...",
    "generated_at": "...",
    "methodology_version": "...",
    "data_version": "..."
  },
  "warnings": []
}
```

## Errores

```json
{
  "error": {
    "code": "INSUFFICIENT_DATA",
    "message": "No hay cobertura suficiente...",
    "details": {}
  }
}
```

## Códigos funcionales
- `INSUFFICIENT_DATA`
- `INVALID_PROFILE`
- `OUT_OF_COVERAGE`
- `SOURCE_DEGRADED`
- `MODEL_UNAVAILABLE`
- `CONSENT_REQUIRED`
- `RATE_LIMITED`

## Versionado
Breaking changes → nueva versión API.

## Pagination
Cursor-based cuando aplique.

## Units
Siempre explícitas en schemas.
