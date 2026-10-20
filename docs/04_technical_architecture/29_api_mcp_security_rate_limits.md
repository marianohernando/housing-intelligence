# API/MCP Authentication & Rate Limits

## Credentials
- user OAuth/session;
- tenant API key;
- scoped service token.

## Scope
Each tool declares required scope.

## Rate limits
By:
- IP anonymous;
- user;
- tenant;
- API key;
- expensive tool.

## MCP
No generic `run_sql`.
No arbitrary filesystem/network.
Tools return evidence metadata.

## Abuse
- quotas;
- concurrency limits;
- timeout;
- max area/query size.
