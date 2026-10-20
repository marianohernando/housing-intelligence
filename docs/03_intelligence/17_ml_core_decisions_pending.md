> **ESTADO: SUPERADO.** Las decisiones de este documento fueron cerradas en rondas posteriores. Se conserva como histórico; usar la documentación v0.4.0 y el Decision Log como fuente vigente.

# ML Core — Decisiones Pendientes

## Principio
No usar ML por sofisticación. Cada modelo debe tener:
- objetivo;
- variable target;
- features;
- métrica;
- baseline;
- explicación;
- fallback.

## Orden previsto
1. baseline determinista;
2. place embeddings;
3. ranking ML;
4. price/rent estimation;
5. demand estimation;
6. forecasting;
7. personalization avanzada.

## Restricción
El sistema debe poder operar en modo degradado si un modelo ML falla:
- reglas;
- últimas features válidas;
- último modelo estable.
