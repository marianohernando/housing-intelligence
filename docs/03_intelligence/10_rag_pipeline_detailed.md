# RAG Pipeline Detallado

## Corpus inicial
- ayudas;
- normativa;
- urbanismo;
- documentación de datasets;
- metodología propia;
- FAQs;
- documentación técnica de vivienda;
- licencias.

## Ingestión documental
1. descargar;
2. versionar;
3. extraer texto;
4. detectar estructura;
5. chunk por sección semántica;
6. metadata;
7. embedding;
8. indexación;
9. tests de retrieval.

## Chunk
No cortar arbitrariamente cada N tokens si existen secciones.

Guardar:
- document_id;
- chunk_id;
- heading_path;
- text;
- jurisdiction;
- valid_from;
- valid_to;
- official;
- source_url;
- version.

## Retrieval
1. intent;
2. metadata filter;
3. lexical search;
4. vector search;
5. rerank;
6. context pack.

## Datos normativos
La vigencia es obligatoria.
Un documento expirado puede recuperarse solo si la pregunta es histórica.

## Evaluación
Crear preguntas golden:
- “¿Puedo acceder a X ayuda?”
- “¿Qué requisitos tiene Y?”
- “¿Qué significa esta métrica?”

Medir:
- hit rate;
- source correctness;
- answer groundedness.
