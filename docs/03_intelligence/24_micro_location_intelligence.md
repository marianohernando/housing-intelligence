# Micro-Location Intelligence

## Principio
Un barrio no es homogéneo.

Dos calles del mismo barrio pueden diferir radicalmente en:
- acceso al Metro;
- líneas de autobús;
- ruido;
- pendiente;
- comercio;
- colegios;
- zonas verdes;
- tiempo al trabajo;
- seguridad vial;
- exposición a tráfico;
- tipología de vivienda.

Por eso el sistema no debe responder:
> “Chamberí es 84/100.”

Debe poder responder:
> “Esta microzona del oeste de Chamberí encaja mejor que la zona próxima a Castellana por ruido, precio y trayecto.”

## Capas de resolución

### Narrativa
Municipio / distrito / barrio.

### Analytics
H3 + sección censal.

### Detail
Calle / parcela / edificio cuando exista cobertura.

## Context windows
Cada microzona tendrá features en diferentes radios/tiempos:
- immediate;
- 5 min;
- 10 min;
- 15 min;
- 30 min mobility catchment.

## Neighborhood context
El modelo debe conocer también celdas vecinas:
- first ring;
- second ring;
- transit-connected context.

## Regla
Nunca asignar automáticamente a todos los edificios de un barrio una media de barrio como si fuera observación exacta.
