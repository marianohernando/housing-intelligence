# Security Threat Model

## Assets
- personal finances;
- precise anchors;
- accessibility needs;
- tenant private data;
- API keys;
- source credentials.

## Threats
- IDOR/cross-tenant access;
- SQL injection;
- prompt injection;
- SSRF from listing URL;
- malicious uploads;
- secrets leakage;
- XSS;
- CSRF;
- rate abuse;
- data exfiltration through AI tools;
- insecure exports/share links.

## Controls
- typed queries/ORM/prepared SQL;
- URL allow/deny + network egress controls;
- file scanning;
- content security;
- authz;
- rate limits;
- audit logs;
- secret scanning;
- dependency scanning.

## AI
Tool permissions are authoritative; model text is never authorization.
