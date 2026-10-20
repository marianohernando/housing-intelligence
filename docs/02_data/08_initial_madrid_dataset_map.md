# Primera Cartografía Real de Datos de Madrid
## v0.1 — Fase de descubrimiento

Este documento no es todavía el inventario completo. Es la primera selección validada de fuentes que demuestran que el producto es técnicamente viable.

# 1. Regla de prioridad
- **P0 — Core:** necesaria para que el producto funcione.
- **P1 — Diferenciadora:** aumenta mucho el valor.
- **P2 — Enriquecimiento:** útil, pero puede entrar después.

# 2. Datasets P0 — Core

## P0-01 — Panel de indicadores de distritos y barrios
Fuente: Ayuntamiento de Madrid  
URL: https://datos.madrid.es/dataset/300087-0-indicadores-distritos/information  
Uso: perfil territorial base, Residential Fit, comparación de barrios, feature engineering.

## P0-02 — Alquiler €/m² por código postal
Fuente: Comunidad de Madrid  
URL: https://datos.comunidad.madrid/dataset/1934259  
Uso: affordability, Reality Check, coste residencial, Housing Gap.

## P0-03 — Alquiler €/m² por municipio
URL: https://datos.comunidad.madrid/dataset/alquiler_metro_cuadrado_mensual_viviendas_arrendadas_valor_catastral_municipios_mas_20000  
Uso: extender el producto fuera de Madrid capital.

## P0-04 — Población por edad, nacionalidad y sexo
URL: https://datos.comunidad.madrid/dataset/poblacion_censada_por_edad_nacionalidad_y_sexo  
Uso: estructura demográfica, mayores, familias, demanda potencial.

## P0-05 — Hogares por tamaño
URL: https://datos.comunidad.madrid/dataset/censo_2021_hogares_por_tamanyo  
Uso: demanda por tamaño de vivienda y Housing Gap.

## P0-06 — Viviendas por superficie
URL: https://datos.comunidad.madrid/dataset/censo_anual_vivienda_por_superficie_agregada  
Uso: comparar tamaño de hogares y parque residencial.

## P0-07 — Renta disponible municipal
URL: https://datos.comunidad.madrid/dataset/irpf_indicador_renta  
Uso: affordability territorial y capacidad económica agregada.

## P0-08 — Centros educativos
URL: https://datos.comunidad.madrid/dataset/centros_educativos  
Uso: familias, school access, proximidad.

## P0-09 — Centros sanitarios públicos y privados
URL: https://datos.comunidad.madrid/dataset/centros_servicios_establecimientos_sanitarios  
Frecuencia: diaria.  
Uso: salud, mayores, localización de servicios.

## P0-10 — Registro de centros de atención social
URL: https://datos.comunidad.madrid/dataset/atencion_social_registro_centros  
Frecuencia: mensual.  
Uso: senior fit, dependencia, déficit asistencial.

## P0-11 — Transporte público CRTM
URL: https://datos.crtm.es/  
Formatos: GTFS, SHP, KML, CSV, GeoJSON/API.  
Uso: tiempos de viaje, isócronas, accesibilidad.

## P0-12 — Catastro / INSPIRE
URL: https://www.catastro.hacienda.gob.es/es-es/acceso_infocat.html  
Uso: parcelas, edificios, direcciones y geometría.

# 3. Datasets P1 — Diferenciadores

## P1-01 — Modelo 3D oficial LOD2
URL: https://geoportal.madrid.es/IDEAM_WBGEOPORTAL/dataset.iam?id=ece2d15a-d16f-46e8-aaec-9576771b9997  
Uso: digital twin, edificios 3D, visualización PRO.

## P1-02 — Parcelas del Portal del Suelo
URL: https://datos.comunidad.madrid/dataset/parcelas_portal_suelo  
Frecuencia: diaria.  
Uso: análisis de parcela y recomendación de producto.

## P1-03 — Transacciones inmobiliarias
URL: https://datos.comunidad.madrid/dataset/transacciones_inmobiliarias_municipio  
Uso: actividad y liquidez.

## P1-04 — Transacciones vivienda nueva vs usada
URL: https://datos.comunidad.madrid/dataset/transacciones_vivienda_nueva_usada_municipio  
Uso: estructura de mercado.

## P1-05 — Farmacias
URL: https://datos.comunidad.madrid/dataset/oficinas_farmacia  
Frecuencia: semanal.  
Uso: mayores y servicios esenciales.

## P1-06 — Personas con discapacidad por edad y sexo
URL: https://datos.comunidad.madrid/dataset/personas_discapacidad_por_edad_y_sexo  
Uso: solo agregado para planificar accesibilidad y vivienda adaptada.

## P1-07 — Calidad del aire
URL base: https://datos.comunidad.madrid/dataset/?tags=Calidad+del+aire  
Incluye datos horarios históricos, datos del día y estaciones.  
Uso: calidad de vida y capas dinámicas.

## P1-08 — Arbolado y zonas verdes
Ejemplo: https://datos.madrid.es/dataset/300761-0-arbolado-especies/downloads  
Uso: green access, sombra/calor y calidad urbana.

## P1-09 — Equipamientos y entidades
URL: https://datos.madrid.es/dataset/300331-0-equipamientos-municipales/information  
Uso: POIs, servicios y proximidad.

# 4. Fuentes pendientes de investigar
- ruido;
- isla de calor;
- energía;
- vivienda pública;
- promociones/licencias;
- urbanismo y edificabilidad;
- precios de compraventa;
- hipotecas;
- universidades;
- guarderías;
- deporte;
- empleo territorial;
- accesibilidad de estaciones;
- vivienda vacía;
- VPO;
- ayudas vigentes;
- permisos de construcción.

# 5. Clasificación temporal
## Casi tiempo real
- calidad del aire.

## Alta frecuencia
- parcelas;
- sanidad;
- farmacias.

## Media frecuencia
- centros sociales;
- transporte;
- equipamientos.

## Estructural
- censo;
- hogares;
- parque de vivienda;
- renta.

# 6. Conclusión
Los datos oficiales ya permiten construir de forma real:
- affordability;
- perfiles familiares;
- perfiles senior;
- movilidad;
- mapa 3D;
- servicios;
- Housing Gap inicial;
- Parcel Analyzer;
- capas ambientales.

El siguiente problema no es si existen datos, sino cómo convertirlos en un diccionario estable de 200–400 features.
