# Infrastructure, DevOps & Security — v0.4.0

## Initial stack
Docker Compose/local:
- web;
- api;
- workers;
- postgres/postgis/pgvector;
- redis;
- routing;
- object storage compatible service where needed.

## Environments
local → CI/test → staging → production/demo.

## CI/CD
See engineering Quality Gates.

## Security
- secret manager/env;
- RBAC;
- tenant isolation;
- RLS selectively;
- rate limits;
- audit logs;
- encryption;
- file/URL defenses;
- dependency/secret scan.

## Operations
- backups;
- restore test;
- migrations;
- rollback;
- observability;
- SLOs;
- cost monitoring.

## Rule
Multi-tenant/security is not “fase posterior”; architecture supports it from the beginning even if initial deployment is single-user.
