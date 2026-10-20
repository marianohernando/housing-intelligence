# Claude Code Execution Protocol

## Goal
Use Claude Code as implementation engine without losing architectural control.

## Before task
Claude must read:
1. `CLAUDE.md`
2. relevant domain docs
3. card/task file
4. affected contracts
5. relevant test plan

## Task size
Prefer cards that can be implemented/reviewed independently.

Avoid:
“Construye todo el PRO”.

Prefer:
- create project entity + migration;
- implement project create API;
- implement tenant permission tests;
- implement project drawer UI.

## Mandatory loop
1. Plan.
2. Inspect existing code.
3. Implement.
4. Add/modify tests.
5. Run relevant tests.
6. Run static checks.
7. Summarize changes.
8. State unresolved risks.
9. Update evidence/doc if gate work.

## No silent architecture decisions
If a task requires changing a documented major decision:
create ADR / flag conflict.

## Parallel agents/worktrees
Allowed only when:
- contracts are stable;
- file ownership does not overlap dangerously;
- integration owner exists.

## End-of-card output
Claude must report:
- files changed;
- tests run;
- test results;
- acceptance criteria status;
- gate impact;
- debt/TODO introduced.

## Definition
Code generated quickly is not progress unless integrated + tested.
