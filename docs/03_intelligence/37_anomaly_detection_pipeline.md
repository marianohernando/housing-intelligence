# Anomaly Detection Pipeline

## Objetivo
Evitar que un dato erróneo contamine scores/modelos.

## Capa 1 — Reglas
- rangos imposibles;
- tipos;
- valores negativos;
- ratios > límites.

## Capa 2 — Estadística
- z-score robusto;
- IQR;
- cambios bruscos;
- distribution drift.

## Capa 3 — Contexto
Comparar con:
- vecinos;
- histórico;
- fuente alternativa.

## Capa 4 — JEV
Triage de anomalías ambiguas:
- probable cambio real;
- probable error;
- requiere revisión.

## Regla
JEV no corrige automáticamente un valor numérico.
Solo clasifica la anomalía y propone routing.
