# Fixtures de contratos de la API (FIXTURES, no salida del producto)

Ejemplos de los contratos PUBLIC (`packages/contracts/src/hi_contracts/public/`) para que la web tipe y pruebe sus pantallas contra zonas e indicadores reales antes de que existan las rutas del motor. **Solo se usan en tests y desarrollo; nunca se muestran en la demo.**

Se regeneran con `uv run python scripts/build_contract_fixtures.py`, que lee la base local en modo solo lectura. `tests/unit/contracts/test_public_contracts.py` valida cada fichero contra su contrato.

| Fichero | Contrato | Qué es real | Qué no |
|---|---|---|---|
| `scenario_state.familia_castellana.fixture.json` | `ScenarioState` (cuerpo de `POST /api/v1/search`) | El caso de la demo: pareja con 2 hijos que trabaja en la Castellana (perfil dorado `golden_family`) | — |
| `zone_gap_list.madrid.fixture.json`, `zone_gap_list.mostoles.fixture.json` | `ZoneGapList` (`data` de `GET /api/v1/gaps/{level}/{code}`) | Todo: es exactamente lo que devuelve hoy la ruta (`hi_api.services.gaps.zone_gap_list`), con la referencia regional del Feature Store (total de la Comunidad / población) | Solo 2 filas (colegio y centro de salud) hasta que GAP-001 añada el resto. Los cortes FALTA < 0,8 y CUBIERTO ≥ 1,0 (`gap-0.1`) son provisionales hasta el ADR de GAP-001 |
| `search_result.familia_presupuesto.fixture.json` | `SearchResult` (`data` de `POST /api/v1/search`) | Zonas, alquiler €/m² publicado, estado PASS/FAIL/UNKNOWN del presupuesto (1.200 €/mes para 90 m²) y recuentos del Reality Check | **El score y el orden son ilustrativos** (60 % margen de presupuesto + 40 % colegios frente a la región) hasta CORE-003 (`methodology_version = search-fixture-illustrative`). El colegio cercano va como preferencia porque la distancia a pie aún no está calculada |

Las respuestas de la API van dentro del sobre común (`data`, `meta`, `warnings`); sus JSON Schema están en `data/schemas/api/`.
