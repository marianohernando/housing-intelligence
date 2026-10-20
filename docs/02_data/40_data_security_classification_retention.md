# Data Classification & Retention

## Classes
### PUBLIC
Open datasets.

### INTERNAL
Derived metrics/model outputs.

### CONFIDENTIAL
Client private datasets/projects.

### SENSITIVE_PERSONAL
Income, debt, precise anchors, accessibility/health-related needs.

## Storage
Sensitive:
- encrypted at rest;
- restricted access;
- no debug logs;
- no analytics payload raw values.

## Retention
Retention is policy-driven by data type.

## Default design
- anonymous raw session: short-lived;
- account scenarios: until deletion/account policy;
- security logs: limited retention;
- derived aggregate analytics: anonymized/pseudonymized;
- client uploads: contract/tenant retention.

Exact production durations require legal review.
