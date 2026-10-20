# Taxonomía y Ontología

## Entidades
- Area;
- GeoCell;
- Building;
- Parcel;
- Household;
- HousingUnit;
- TransportStop;
- School;
- HealthFacility;
- SocialFacility;
- Park;
- AidProgram;
- HousingDemand;
- HousingSupply;
- Metric;
- Dataset;
- Model;
- Score.

## Relaciones
- Area CONTAINS Building;
- Building LOCATED_IN GeoCell;
- GeoCell SERVED_BY TransportStop;
- HousingProfile MATCHES Area;
- Parcel SUPPORTS Use;
- Area HAS_DEMAND HousingType.

## Objetivo
Que cualquier columna nueva termine mapeada a un concepto estable.
