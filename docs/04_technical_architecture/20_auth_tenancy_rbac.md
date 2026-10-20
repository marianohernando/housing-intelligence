# Authentication, Tenancy & RBAC

## Auth
Support:
- anonymous sessions;
- registered consumer;
- PRO organization users;
- API/MCP service credentials.

## Tenant model
All PRO private resources include `tenant_id`.

## Defense
- backend authorization on every resource;
- RLS where useful;
- integration tests for cross-tenant access;
- audit logs.

## Sensitive scopes
Separate permissions for:
- private uploads;
- billing;
- API keys;
- exports;
- membership.

## Session security
- secure cookies/tokens;
- rotation/revocation;
- CSRF strategy where applicable.
