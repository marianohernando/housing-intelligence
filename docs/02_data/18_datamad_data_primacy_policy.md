# Política Madrid-First para DATAMAD

## Objetivo
Asegurar que el proyecto cumple el espíritu y los criterios de DATAMAD 2026 y no utiliza los datos de la Comunidad de Madrid de forma testimonial.

## Principio
Los datos del Catálogo de Datos Abiertos de la Comunidad de Madrid son la materia prima principal del MVP.

Fuentes externas:
- INE;
- Catastro;
- Ayuntamiento;
- CRTM;
- OSM;
- proveedores;
- scraping;
solo complementan, enriquecen o validan.

## Regla funcional
Cada funcionalidad core del MVP debe documentar:
1. qué datasets de Comunidad de Madrid utiliza;
2. qué features derivan de ellos;
3. qué aporta una fuente externa;
4. qué ocurriría si se eliminara la fuente externa.

## Funcionalidades que deben depender de datos regionales
- Residential Fit;
- Housing Gap;
- perfiles demográficos;
- servicios de salud;
- educación;
- atención social;
- vivienda/alquiler;
- parcelas/suelo cuando exista;
- variables ambientales;
- PRO territorial.

## Source contribution matrix
Crear una matriz:

| Feature/Product | CM datasets | External enrichment | CM role |
|---|---|---|---|
| Affordability | alquiler/renta | Catastro/mercado | core |
| Family Fit | población/hogares/educación | OSM | core |
| Senior Fit | población/salud/social | OSM | core |
| Housing Gap | vivienda/hogares/transacciones | otras | core |
| Parcel Intelligence | Portal Suelo + contexto | Catastro | core |

## Regla de demo
En el pitch debe poder mostrarse:
> “Esta recomendación usa X datasets abiertos de la Comunidad de Madrid.”

No es marketing: debe poder trazarse en lineage.

## Open data attribution
Conservar:
- source name;
- source URL;
- fecha de extracción;
- licencia;
- attribution requerida.

## Objetivo para Claude Code
Nunca sustituir silenciosamente una fuente regional por una externa más cómoda si eso reduce el papel real de los datos DATAMAD.
