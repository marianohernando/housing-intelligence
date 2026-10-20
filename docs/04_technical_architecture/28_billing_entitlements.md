# Billing & Entitlements

## Principle
Billing provider is separate from product authorization.

## Entitlements
Examples:
- ai_queries_month;
- saved_scenarios;
- listing_analyses;
- pro_projects;
- exports;
- api_calls;
- mcp_tools;
- team_members.

## Backend
Check entitlement server-side.

## Failure
Billing outage must not corrupt tenant data.
Grace-period policy configurable.
