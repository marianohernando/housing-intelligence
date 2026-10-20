# JEV — Workflows Detallados

## JEV-01 Dataset Classifier

### Input state
- title
- description
- columns
- sample values
- provider

### Questions
- domain
- geo level
- temporal type
- relevance
- privacy risk
- quality concern

### Output
Typed choices + confidence.

---

## JEV-02 Column Semantic Mapper

Input:
- column name;
- dataset context;
- examples.

Output:
- metric family;
- probable unit;
- entity/measure;
- temporal semantics.

Uso:
proponer mapeo, nunca modificar catálogo automáticamente sin validación.

---

## JEV-03 User Preference Interpreter

Input:
> “Quiero algo tranquilo, con parques, no me importa alejarme 40 min.”

Output:
```json
{
  "quiet_importance": "high",
  "green_importance": "high",
  "commute_tolerance": "high"
}
```

---

## JEV-04 Candidate Reranker

Input:
- perfil resumido;
- 20 candidatos;
- scores estructurados.

Output:
- order;
- reason codes;
- confidence.

No tiene acceso a información personal no necesaria.

---

## JEV-05 Data Quality Triage

Input:
- anomalías;
- schema changes;
- distributions.

Output:
- likely benign;
- likely breaking;
- requires review.

---

## Fallback
Confidence baja → Claude/Fable o reglas específicas.
