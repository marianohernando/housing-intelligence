# Fase 0 (README + PR) — gate 2026-11-11T10:27:48Z — 114023a + cambios en README.md, board/BOARD.md
$ make lint
uv run ruff check .
All checks passed!
uv run ruff format --check .
180 files already formatted

> @hi/web@0.0.1 lint
> eslint .

lint exit=0
$ make typecheck
uv run pyright
0 errors, 0 warnings, 0 informations

> @hi/web@0.0.1 typecheck
> tsc --noEmit

typecheck exit=0
$ make test
uv run pytest tests/unit tests/data -q
........................................................................ [ 46%]
........................................................................ [ 92%]
...........                                                              [100%]
155 passed in 2.56s

> @hi/web@0.0.1 test
> vitest --run


 RUN  v5.0.5 ~/Desktop/DATAMAD/housing-intelligence/apps/web


 Test Files  3 passed (3)
      Tests  11 passed (11)
   Start at  11:27:57
   Duration  82ms (tests 51%, import 24%, transform 15%, worker 11%)

uv run pytest -m db tests/integration -q
............................................                             [100%]
44 passed in 21.29s
test exit=0
exit=0
