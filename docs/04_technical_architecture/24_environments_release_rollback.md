# Environments, Release & Rollback

## Environments
- local;
- test/CI;
- staging;
- production/demo.

## Same migrations/contracts
Avoid environment-specific code paths beyond config/capability flags.

## Release
1. CI pass;
2. migration dry-run;
3. staging smoke;
4. deploy;
5. post-deploy smoke;
6. monitor.

## Rollback
- app rollback;
- feature flag disable;
- model rollback;
- data snapshot rollback when safe;
- forward-fix migrations preferred for destructive DB changes.

## Demo freeze
Freeze a known-good release before final presentation.
