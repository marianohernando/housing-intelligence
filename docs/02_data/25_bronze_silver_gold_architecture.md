# Bronze / Silver / Gold Data Architecture

## Bronze — fuente original
Guardar el artefacto tal como se obtiene:
- archivo original;
- response body;
- checksum;
- headers relevantes;
- retrieved_at;
- source_version;
- licencia/terms snapshot reference.

Nunca modificar Bronze.

## Silver — canonical data
Datos:
- tipados;
- limpios;
- deduplicados;
- georreferenciados;
- normalizados;
- enlazados a entidades canónicas;
- con unidades coherentes.

## Gold — intelligence-ready
- métricas;
- features;
- aggregates;
- H3;
- ventanas temporales;
- scores base;
- embeddings.

## Regla
Debe poder regenerarse Gold desde Bronze + código/versiones.

## Ventaja
Si cambia una fórmula:
no necesitamos volver a scrapear/descargar la fuente si Bronze sigue válido.
