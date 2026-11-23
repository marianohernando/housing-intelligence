# Catálogo DCAT-AP europeo y Smart Data Models (23 nov, F14)

Rama `claude/f14-dcat-sdm`, desde `claude/sprint-1-public` en `4355527d`. Tres ficheros estáticos de la web, en `apps/web/public/datos/`, que escribe `scripts/export_dcat_sdm.py` desde el catálogo versionado y que se enlazan en `/desarrolladores` («Funciona hoy»). **DCAT-AP europeo 3.0.1, nunca DCAT-AP-ES.**

| Fichero | Tamaño | Qué es | De dónde sale |
|---|---|---|---|
| `datos/catalogo.dcat.jsonld` | 231 KB | `dcat:Catalog` de Vida Fácil (licencia CC BY 4.0) con 62 `dcat:Dataset`: los 59 que usamos (39 del portal CM y 20 complementarios, los que tienen evidencia de Gate 1, como `pitch/datasets_cm.md`), los indicadores de la API (`dct:source` a los 59) y los dos ficheros SDM; y un `dcat:DataService`, la API (`dcat:endpointURL` de producción y su OpenAPI) | `data/catalog/{sources,datasets}`, título y licencia de cada ficha CM de `pitch/portal_cm_snapshot.json`, HVD de `data/catalog/manual/hvd_datasets.yaml` |
| `datos/sdm/datasets.json` | 65 KB | Los 39 conjuntos CM como `Dataset` de `dataModel.DCAT-AP` (esquema 3.0.0) con MELODA en los campos que prevé el modelo: `accessMechanism` (D2) y `standardization` (D4) | `pitch/meloda_cm_snapshot.json` (API del Monitorizador leída el 20 nov; «Fuente: spain.meloda.org», CC BY 4.0) |
| `datos/sdm/farmacias.json` | 1.680 KB | Las 2.957 oficinas de farmacia como `PointOfInterest` (esquema 0.3.1), toda la Comunidad: no hace falta recortar | `GET /api/v1/places?category=pharmacy` de producción, **1 petición** (1 página de 5.000) el 23 nov, guardada en `data/catalog/manual/farmacias_places_api.csv` |

## Decisiones del generador

- **Licencias, sin inventar.** Ficha CM: la del portal (`cc-by` → `…/licence/CC_BY_4_0`; `CRTM-LDA` → `https://www.crtm.es/licencia-de-uso`, con su nombre). Resto: la del registro de fuentes (CC BY 4.0, ODbL → `ODC_BL`, o la URL del aviso legal de AEAT, Ministerio de Sanidad, MIVAU y comunidad.madrid). Los 59 tienen licencia. La única distribución sin `dct:license` es la de la API: mezcla fuentes (también ODbL), así que lleva un `dct:rights` que remite a la licencia de cada conjunto.
- **Frecuencia** (`dct:accrualPeriodicity`) solo donde el `refresh_policy` del registro la dice (anual, semanal, diario…): 33 de 59. `unknown`, `manual` y `none` se dejan sin frecuencia.
- **HVD** solo donde aplica el Reglamento de Ejecución (UE) 2023/138, anexo, punto 2: las 5 fichas de calidad del aire (Directiva 2008/50/CE) → «Aire» `c_63b37dd4`, y el mapa estratégico de ruido (Directiva 2002/49/CE) → «Ruido» `c_e4358335`, con `dcatap:applicableLegislation`. Ni el portal CM ni el del Ayuntamiento las marcan hoy como HVD.
- **Vocabularios de la UE** con su clase (rango de DCAT-AP): `dct:Frequency`, `skos:Concept` con su `skos:prefLabel` en español, `dct:MediaTypeOrExtent`, `dct:Location` (NUTS `ES30`), `eli:LegalResource`. Códigos y etiquetas comprobados hoy en el SPARQL de la Oficina de Publicaciones.
- **SDM.** `license` es el identificador SPDX (`CC-BY-4.0`) y falta en las 10 del CRTM, cuya licencia no tiene uno. `dissemination` y `reputation` no se incluyen: el Monitorizador no las mide. El resto de la puntuación MELODA queda enlazado en `isReferencedBy` (la ficha de la API del Monitorizador). `geolocation` sale de la geometría del catálogo (punto, polígono o línea).
- **Farmacias.** Nombre sintético («Farmacia · calle y número»): el registro nombra a los titulares, que nunca se guardan. Cada entidad lleva `source` (la ficha CM) y el fichero, la licencia y el texto de cita de la fuente. 5 coordenadas geocodificadas lo dicen en `description`.

## Revisión de #124

- **R-03:** el `dct:description` del catálogo dice «La licencia de este catálogo cubre sus metadatos; cada distribución lleva la licencia de su fuente.» La licencia CC BY 4.0 del catálogo se mantiene.
- **R-02:** cada uno de los 6 datasets HVD lleva un `rdfs:comment` con el criterio, que sale del `reason` de `hvd_datasets.yaml`: «Marcado como HVD por Vida Fácil: datos de la Directiva 2008/50/CE, … (Reglamento de Ejecución (UE) 2023/138, anexo); el publicador no lo declara.»
- **R-01:** el mapeo de «cc-by» a CC BY 4.0 no cambia. Las 29 fichas CM con «cc-by», su entidad SDM y la fuente de `farmacias.json` dicen que el portal no da versión y que la 4.0 es la del registro de fuentes del portal (`data/catalog/sources/comunidad_madrid_ckan.yaml`).
- **R-04:** `claude/sprint-1-public` (#120, #121 y #122) ya estaba fusionada; `make lint` en verde con los ficheros regenerados.

Tras estos cambios se repitieron las dos validaciones en línea, con el mismo resultado: 0 violaciones propias en el ITB y 39/39 y 2.957/2.957 en `pysmartdatamodels`.

## Validación sin red (tests)

`tests/unit/catalog/test_dcat_sdm_export.py`, 14 tests: `--check` sin diferencias; JSON-LD con los espacios de nombres y las propiedades obligatorias de DCAT-AP 3.0.1 por clase; vocabularios de la UE con su clase; HVD solo en las 6 del registro; copias de los esquemas SDM con el sha256 del original (`data/schemas/sdm/sources.json`); **39/39 `Dataset` y 2.957/2.957 `PointOfInterest` válidos** con `jsonschema` 4.26 (`Draft202012Validator`) y un `Registry` de `referencing` 0.37 que resuelve las URL oficiales a las copias; el validador rechaza un nivel inexistente y una entidad sin `name`. En la web, `openData.test.ts` comprueba que los tres enlaces son ficheros JSON de `public/`.

## Validación en línea

**DCAT-AP 3.0.1, validador SHACL del ITB de la Comisión** (API REST, 23 nov): **0 violaciones en nuestro fichero** en todos los perfiles 3.0.1. Detalle en `itb-dcat-ap-resumen.json`.

| Perfil | Resultado |
|---|---|
| `base0` (obligatorios) y `range0`, `range` (rangos) | conforme, 0 resultados |
| `base` | 5 violaciones `foaf:name`, todas en nodos del conocimiento de fondo del validador: un catálogo mínimo de 2 nodos da las mismas 5 (`itb-dcatap.3_0_1_base-catalogo-minimo.jsonld`) |
| `codelists` | 0 violaciones; 109 avisos: el publicador no es un organismo de la UE (65) y NUTS no está en las listas que sugiere para `dct:spatial` (44) |
| `rec` y `full` | 0 violaciones propias (las 16 de `full` están en el conocimiento de fondo: los 5 nodos de arriba, dos veces, y 6 esquemas ADMS); 468 avisos de propiedades recomendadas que no tenemos (descripción de cada distribución, `availability`, palabras clave, cobertura temporal, contacto de las fichas CM) |
| HVD 3.0.0 `full` | El perfil trata todo el fichero como HVD. En las 6 fichas HVD quedan 12: 6 de la regla de API (un HVD debe servirse por un `dcat:DataService`; los publicadores no declaran ninguno y no lo inventamos) y 6 de rango sobre `dcat:accessURL` |

**Smart Data Models, `pysmartdatamodels` 0.8.2.0** (`validate_payload`, esquemas oficiales de GitHub, descargados una vez por modelo): **39/39 `Dataset` y 2.957/2.957 `PointOfInterest` válidos** (`pysmartdatamodels.json`).

## Gate

- `make lint typecheck`: verde (`make-lint-typecheck.txt`), con el nuevo `export_dcat_sdm.py --check` también en `make lint` y en CI.
- `make test-unit`: 1.365 tests de Python y 649 de la web, verdes (`make-test-unit.txt`), tras fusionar `claude/sprint-1-public` (#121, #122).
- `npm run build` de `apps/web`: verde (`npm-run-build.txt`). Tras cada `npm ci`, la primera ejecución se detiene en el aviso de seguridad de la versión de Next.js (16.4.2) y la siguiente termina; la versión no se toca en esta rama.

## Pendiente tras desplegar

- `curl -I` de los tres ficheros en producción: el `Content-Type` del `.jsonld` (si no fuera `application/ld+json`, valdría `.json`).
