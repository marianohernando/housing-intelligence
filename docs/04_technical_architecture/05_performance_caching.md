# Rendimiento y Caché

## Principio
Precalcular lo que no dependa del usuario.

## Precomputar
- features;
- scores base;
- embeddings;
- clusters;
- vector tiles;
- matrices de movilidad comunes.

## Redis
- resultados frecuentes;
- perfiles;
- rankings;
- sesiones;
- API.

## Mapa
Progressive loading:
1. base;
2. H3;
3. edificios;
4. detalle.

## Objetivos orientativos
- consulta cacheada <500 ms;
- ranking básico <1 s;
- streaming en IA;
- mapa fluido en equipos razonables.
