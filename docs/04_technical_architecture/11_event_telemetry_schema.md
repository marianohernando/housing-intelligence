# Event Telemetry Schema

## Objetivo
Aprender del producto sin crear un almacén innecesario de datos personales.

## Evento base

```json
{
  "event_id": "uuid",
  "event_name": "area_rejected",
  "occurred_at": "...",
  "anonymous_or_user_id": "...",
  "session_id": "...",
  "properties": {},
  "consent_state": {}
}
```

## Eventos PUBLIC
- profile_started
- profile_completed
- recommendation_generated
- area_viewed
- area_saved
- area_rejected
- rejection_reason_selected
- scenario_changed
- reality_check_used
- support_viewed

## Eventos PRO
- area_analyzed
- parcel_analyzed
- report_generated
- layer_enabled
- query_executed
- export_created

## Privacidad
Evitar duplicar:
- ingresos exactos;
- discapacidad;
- deuda;
en eventos si ya están en storage protegido.
Usar segmentos o referencias seguras cuando sea posible.
