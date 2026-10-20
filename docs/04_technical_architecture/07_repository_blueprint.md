# Repository Blueprint

## Monorepo propuesto

```text
housing-intelligence/
├── CLAUDE.md
├── README.md
├── apps/
│   ├── web/
│   └── api/
├── packages/
│   ├── domain/
│   ├── contracts/
│   ├── map-config/
│   └── ui/
├── services/
│   ├── ingestion/
│   ├── features/
│   ├── ml/
│   ├── routing/
│   └── mcp/
├── data/
│   ├── catalog/
│   ├── schemas/
│   └── fixtures/
├── infra/
│   ├── docker/
│   └── migrations/
├── notebooks/
│   └── research/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── e2e/
│   ├── data/
│   └── evals/
└── docs/
```

## Apps

### `apps/web`
Next.js/React.

### `apps/api`
FastAPI.

## Packages

### `domain`
Tipos y lógica pura.

### `contracts`
Pydantic/JSON schemas compartidos.

### `map-config`
Capas, estilos y mappings.

## Services
Procesos que pueden ejecutarse como workers sin convertirse todavía en microservicios de red.

## Regla
La estructura puede adaptarse, pero los dominios no deben mezclarse por comodidad.
