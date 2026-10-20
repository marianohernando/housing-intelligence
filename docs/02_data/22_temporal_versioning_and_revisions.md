# Temporal Versioning & Source Revisions

## Objetivo
Poder reconstruir cómo era el dato en una fecha y cómo cambió.

## Por observación
Guardar:
- valid_from;
- valid_to;
- observed_at;
- retrieved_at;
- source_version;
- superseded_by.

## Correcciones
Si una fuente corrige un dato de 2024 en 2026:
- no borrar historia de ingestión;
- marcar la observación anterior como superseded;
- guardar la corrección;
- recalcular features/modelos dependientes.

## Beneficios
- auditoría;
- emerging areas;
- timeline;
- reproducibilidad;
- comparación de modelos.
