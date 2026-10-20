# AI Orchestration

## Objetivo
Elegir la herramienta correcta para cada tipo de problema.

## Router conceptual

```text
User Request
  ↓
Intent Classification
  ↓
┌──────────────────────────────────────┐
│ Exact calculation → Domain function │
│ Structured decision → JEV           │
│ Document retrieval → RAG            │
│ Geo query → GIS service             │
│ Prediction → ML model               │
│ Complex synthesis → Claude/Fable    │
└──────────────────────────────────────┘
  ↓
Evidence bundle
  ↓
LLM explanation
```

## Principio
El LLM recibe resultados, no toneladas de datos crudos.

## Evidence Bundle

Formato conceptual:

```json
{
  "facts": [],
  "scores": [],
  "model_outputs": [],
  "documents": [],
  "sources": [],
  "confidence": {},
  "limitations": []
}
```

## Respuesta
El LLM debe:
- responder;
- explicar trade-offs;
- citar fuentes internas;
- mencionar incertidumbre cuando sea material.

No debe:
- alterar cifras;
- inventar fuentes;
- ocultar limitaciones.
