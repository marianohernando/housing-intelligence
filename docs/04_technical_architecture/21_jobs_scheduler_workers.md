# Jobs, Scheduler & Workers

## Background jobs
- ingestion;
- feature builds;
- report generation;
- embeddings;
- alert evaluation;
- model training;
- exports;
- heavy parcel analysis.

## Requirements
- idempotency;
- retry policy;
- dead-letter handling;
- job status;
- timeout;
- correlation ID.

## Scheduler
Source refresh cadences stored in config/catalog.

## MVP
Can use simple worker/queue architecture.
Do not run heavy jobs in web request process.
