# Engineering Rules

## General
- Python 3.12+.
- TypeScript estricto.
- Tipado obligatorio en interfaces públicas.
- Configuración por entorno.
- No secrets.
- No magic numbers.

## Python
- Ruff.
- Pyright/Mypy según decisión final.
- Pydantic para contracts.
- SQLAlchemy/SQLModel o capa explícita definida antes de implementación.

## TypeScript
- strict=true.
- ESLint.
- schemas compartidos mediante generación/OpenAPI cuando sea posible.

## DB
- migraciones.
- índices documentados.
- no DDL manual en producción.
- PostGIS types explícitos.

## Logs
- estructurados;
- request IDs;
- no PII sensible.

## Code review checklist
- correcto;
- testeado;
- documentado;
- observable;
- seguro;
- no rompe contrato.
