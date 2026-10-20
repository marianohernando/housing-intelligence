# Geospatial Resolution Policy

## Objetivo
Evitar falsas precisiones.

## Resoluciones principales
- CCAA
- provincia
- municipio
- distrito
- barrio
- sección censal
- H3
- parcela
- edificio

## Regla
Una métrica nunca debe mostrarse a una resolución más fina que la fuente salvo que:
- exista un método de desagregación documentado;
- se indique que es estimada;
- se acompañe de confidence.

## H3
Usar H3 como unidad analítica común.

### Resolución inicial orientativa
- H3 r7/r8: vista regional.
- H3 r9: análisis urbano.
- H3 r10: detalle fino donde haya datos suficientes.

No fijar una resolución única para todo.

## Spatial join
Cada feature debe documentar:
- cómo se asigna a H3;
- si usa centroid, overlap, population-weighting o network access.
