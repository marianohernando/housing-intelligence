# Modelo Geoespacial

## Sistemas simultáneos
### Administrativo
- Comunidad;
- provincia;
- municipio;
- distrito;
- barrio;
- código postal;
- sección censal;
- parcela;
- edificio.

### Analítico
H3 como malla común.

## GeoCell
Unidad interna:
- h3_id;
- geometry;
- municipality;
- district;
- neighborhood;
- census_sections;
- buildings;
- metrics;
- features.

## PostGIS
Usado para:
- proximidad;
- buffers;
- intersecciones;
- containment;
- spatial joins;
- vector tiles.

## Motivo
Todos los datasets deben poder compararse espacialmente.
