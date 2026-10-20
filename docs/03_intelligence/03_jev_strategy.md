# Estrategia JEV

## Qué es para nosotros
Capa de decisión rápida, tipada, probabilística y con confidence.

## Uso en trabajo previo
- clasificar datasets;
- clasificar columnas;
- detectar categoría;
- estimar utilidad;
- alertar de riesgo de calidad;
- routing.

## Uso en runtime
- extraer preferencias;
- clasificar intención;
- reranking;
- decisiones rápidas;
- quality gates.

## NO usar JEV para
- sumar;
- SQL;
- población;
- hipotecas;
- distancias;
- cálculos exactos;
- inventar precio.

## Confidence routing
- alta: aceptar;
- media: validar;
- baja: escalar a Claude Fable.
