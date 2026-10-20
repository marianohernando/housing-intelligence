# Catastro Ingestion Specification

## Fuentes oficiales preferentes
Dirección General del Catastro INSPIRE:
- Cadastral Parcels (CP);
- Addresses (AD);
- Buildings (BU).

## Acceso
- WFS para consultas;
- ATOM para descargas completas por municipio;
- WMS para visualización;
- productos catastrales cuando aplique.

## Estrategia Madrid
Para cargas masivas:
preferir ATOM/descarga por municipios + versionado local.

Para detalle puntual:
WFS por referencia/área.

## Canonical entities
- parcel_master
- building_master
- address_master

## Derivaciones
Cruzar con:
- H3;
- sección censal;
- barrio/distrito/municipio;
- 3D LOD2;
- servicios;
- mercado;
- urbanismo.

## Regla
No confundir información catastral pública con información de mercado.
