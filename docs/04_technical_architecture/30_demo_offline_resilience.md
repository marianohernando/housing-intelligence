# Demo / Offline Resilience

## Demo must survive
- source API down;
- LLM provider temporary failure;
- network degradation;
- routing provider issue.

## Snapshot mode
- local validated data;
- prebuilt vector tiles where useful;
- cached RAG docs;
- deterministic score fallback;
- optional precomputed demo routes.

## LLM fallback
If provider fails:
show structured deterministic analysis and explain capability is degraded.

## Test
Run demo with external network disabled before submission.
