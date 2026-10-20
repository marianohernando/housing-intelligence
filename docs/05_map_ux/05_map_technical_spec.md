# Especificación Técnica del Mapa

## Stack
- MapLibre GL JS;
- deck.gl;
- optional Three.js;
- vector tiles;
- 3D Tiles/I3S si aplica.

## Capas por zoom

### Zoom regional
- H3 aggregates;
- municipal boundaries;
- high-level scores.

### Zoom urbano
- neighborhoods;
- POI clusters;
- transit;
- H3 r9/r10.

### Zoom edificio
- LOD2 buildings;
- parcels;
- exact nearby services.

## Layer registry
Cada capa debe tener:
- layer_id;
- source;
- min_zoom;
- max_zoom;
- public/pro;
- style;
- legend;
- interaction;
- data contract.

## Performance
- no cargar geometría completa de Madrid en cliente;
- tile-based;
- progressive;
- memoize layer props;
- worker para operaciones pesadas.

## Selección
Click → canonical entity ID → fetch detail.
No depender del texto visible del feature.
