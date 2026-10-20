# Hybrid GIS + RAG Query Engine

## Objetivo
Responder preguntas que mezclan:
- documentos;
- geografía;
- cifras;
- modelos.

## Ejemplo
> “¿Qué se podría hacer con esta parcela y qué demanda residencial hay alrededor?”

## Plan
1. resolve parcel;
2. fetch structured parcel facts;
3. GIS context;
4. demand/supply metrics;
5. retrieve relevant technical/urban documentation;
6. models;
7. evidence bundle;
8. LLM synthesis.

## Evidence bundle
```json
{
  "entities": [],
  "gis_facts": [],
  "metrics": [],
  "model_outputs": [],
  "documents": [],
  "sources": [],
  "warnings": []
}
```

## Regla
RAG no reemplaza PostGIS.
PostGIS no reemplaza documentación legal.
El LLM une resultados ya calculados.
