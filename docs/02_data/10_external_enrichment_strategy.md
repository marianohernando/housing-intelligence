# Estrategia de Enriquecimiento Externo
## v0.1

## Objetivo
No depender únicamente de datasets de la Comunidad de Madrid. El sistema combinará fuentes oficiales, Catastro, fuentes abiertas de POIs, transporte, datasets municipales y scraping selectivo cuando sea legal, estable y aporte valor.

## Jerarquía de confianza

### Tier A — Fuente oficial primaria
Ejemplos:
- Comunidad de Madrid;
- Ayuntamiento;
- INE;
- Catastro;
- CRTM;
- ministerios.

Uso:
Fuente preferida para hechos, métricas oficiales y datos que afecten a scoring.

### Tier B — Fuente abierta estructurada
Ejemplos:
- OpenStreetMap;
- GTFS;
- directorios públicos;
- datasets de terceros con licencia clara.

Uso:
Enriquecimiento geográfico y POIs.

### Tier C — APIs comerciales
Ejemplos:
- Foursquare Places;
- Google Places;
- otros proveedores.

Uso:
Enriquecimiento puntual, validación y campos que no existan en fuentes A/B.

### Tier D — Web scraping
Uso solo cuando:
- no exista API/dataset razonable;
- términos permitan el uso;
- los datos sean necesarios;
- tengamos parser/versionado/fallback.

Nunca convertir scraping frágil en dependencia crítica del producto.

---

# 1. Negocios y POIs

## Madrid capital
El Ayuntamiento publica un censo de locales, actividades y terrazas con ficheros masivos y actualización frecuente. Debe ser la fuente prioritaria para actividad económica local.

## Comunidad / resto de municipios
Combinar:
- OpenStreetMap;
- fuentes municipales;
- Foursquare u otro proveedor si se justifica;
- scraping selectivo.

## Categorías
Normalizar a una taxonomía propia:
- supermercado;
- farmacia;
- restauración;
- comercio;
- deporte;
- ocio;
- salud;
- educación;
- servicios personales;
- coworking;
- cultura;
- administración;
- movilidad.

---

# 2. Educación y salud

No scrapear primero.

Fuentes oficiales ya ofrecen:
- centros educativos;
- titularidad;
- etapas;
- localización;
- centros sanitarios;
- establecimientos;
- centros sociales.

Scraping solo para enriquecer:
- horarios;
- web;
- servicios no presentes;
- información adicional verificable.

---

# 3. Catastro

Utilizar servicios INSPIRE para:
- parcelas;
- edificios;
- direcciones;
- geometría.

Catastro es fuente estructural de geometría, no fuente de preferencias del usuario.

---

# 4. OpenStreetMap

Uso principal:
- POIs;
- caminabilidad;
- vías;
- servicios;
- edificios donde aporte;
- transporte auxiliar;
- red peatonal/ciclista.

Guardar atribución y cumplir ODbL.

Overpass se puede usar para exploración y cargas pequeñas, pero para producción es preferible usar extractos/replicación o una fuente intermedia controlada.

---

# 5. Google Places

No debe ser nuestra base maestra de POIs.

Motivos:
- coste;
- restricciones de almacenamiento/caché;
- dependencia comercial;
- condiciones específicas EEE.

Puede usarse para:
- validación;
- enriquecimiento bajo demanda;
- detalles concretos si la licencia lo permite.

---

# 6. Foursquare Places

Puede ser alternativa para enriquecer POIs a escala regional/nacional.

Evaluar:
- coste;
- licencia;
- cobertura;
- frescura;
- persistencia permitida.

---

# 7. Scraping

## Permitido conceptualmente
Scrapers específicos y versionados de:
- webs públicas;
- fuentes sin API;
- directorios cuando sus términos lo permitan.

## Reglas
Cada scraper debe tener:
- source_id;
- terms_reviewed;
- parser_version;
- last_success;
- schema;
- freshness;
- fallback;
- quality score.

## No hacer
- depender de scraping de Google Maps;
- saltarse controles técnicos;
- recopilar datos personales innecesarios;
- mezclar datos sin procedencia.

---

# 8. Entity Resolution

El mismo lugar puede aparecer en cinco fuentes.

Ejemplo:
- colegio oficial;
- OSM;
- Foursquare;
- Ayuntamiento;
- web propia.

Necesitamos un `place_master`.

Campos:
- canonical_place_id;
- name;
- category;
- geometry;
- official_id;
- osm_id;
- external_ids;
- confidence;
- source_priority;
- last_verified.

Deduplicación por:
1. identificador oficial;
2. coordenadas;
3. nombre normalizado;
4. dirección;
5. categoría;
6. fuzzy matching.

---

# 9. Source Confidence

Cada dato tendrá una puntuación de confianza.

Ejemplo:
- fuente oficial reciente: 1.00;
- OSM actualizado: 0.90;
- proveedor comercial: 0.90;
- web oficial scrapeada: 0.85;
- directorio secundario: 0.65.

La confianza de fuente NO sustituye la confianza estadística del modelo.

Son métricas separadas.

---

# 10. Resultado

El sistema final no debe preguntar:
> ¿cuántos negocios hay?

Debe poder responder:
> ¿qué tan accesibles y útiles son los servicios relevantes para este perfil?

Ese cambio convierte POIs en inteligencia residencial.
