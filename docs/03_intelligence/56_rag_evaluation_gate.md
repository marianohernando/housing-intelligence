# RAG Evaluation Gate

## Golden questions
Cover:
- housing aid;
- methodology;
- urbanism docs;
- dataset definitions;
- regulation/document facts.

## Metrics
- retrieval recall@k;
- citation relevance;
- grounded answer rate;
- abstention quality;
- stale-doc handling.

## Initial release targets
- critical claims with citation: >= 95%;
- unsupported critical factual claims: 0 in golden set;
- no-hit queries must abstain rather than invent.

## Prompt injection
Documents are untrusted content.
Retrieved text cannot override system/tool policies.
