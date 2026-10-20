# Database Migration / Rollback Tests

## Every migration
- applies to empty DB;
- applies to representative existing DB;
- preserves required data;
- rollback/forward-fix strategy documented;
- indices checked;
- lock/runtime considered.

## Destructive
Require backup and explicit review.

## Demo freeze
No risky schema migration immediately before final demo.
