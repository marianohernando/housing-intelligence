# Loading, Empty, Error & Recovery States

## Todo flujo debe definir
- loading;
- no data;
- no results;
- degraded data;
- permission denied;
- provider unavailable;
- timeout;
- partial result;
- retry.

## Principio
“No hay resultados” ≠ “no tenemos datos”.

## Map
Una capa fallida no debe tumbar el mapa completo.

## AI
Si JEV/LLM falla:
- deterministic fallback;
- mensaje claro;
- conservar ScenarioState.
