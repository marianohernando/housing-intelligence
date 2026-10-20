# Backup, Restore & Disaster Recovery

## Back up
- PostgreSQL/PostGIS;
- object storage metadata/files;
- model registry;
- source catalog/config;
- secrets through provider process, not plaintext backups.

## Tests
A backup is not valid until restore is tested.

## Initial targets
- daily DB backup;
- pre-migration snapshot;
- documented restore runbook.

## Demo
Keep independent local/demo snapshot.

## Production later
Define RPO/RTO by plan/SLA.
