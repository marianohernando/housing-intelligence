# Security Test Plan

## Authz
- anonymous cannot access account data;
- user A cannot access user B;
- tenant A cannot access tenant B;
- viewer cannot mutate;
- API scope restrictions.

## URL analysis
Test:
- localhost;
- private IPs;
- metadata endpoints;
- redirects;
- huge content;
- non-http schemes.

## Uploads
- executable disguised;
- oversized file;
- malformed PDF;
- duplicate;
- tenant leak.

## AI
- prompt injection;
- exfiltration request;
- unauthorized tool;
- hidden instruction in document.

## Gate
Any cross-tenant/privacy critical failure = release blocker.
