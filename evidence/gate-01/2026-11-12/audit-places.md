# Auditoría de equipamientos (T1, fase de prueba) · 12 nov 2026

Línea A. Decisión: D-216. Script: `uv run python scripts/audit_places.py` (base local, tras reingerir los cuatro registros con `places-1.1.0` y recalcular las features). Revisión de 10 zonas de la línea D (`pitch/revision_10_zonas.md` en `claude/coord`, 9d5f1a6): sus discrepancias D1–D7 y M1–M3 se responden en §4.

## Resumen
- **«Centro Polivalente» (1.001) no eran servicios para mayores**, sino clínicas privadas de varias especialidades (RD 1277/2003, C.2.90; 971 «Privado No Benéfico», sin nombre en el registro). Ninguna feature los usaba, pero eran el 65 % de los puntos de la capa de salud. Fuera del registro de lugares (test `test_private_polyclinics_are_not_health_places`). La coincidencia de cifras con los 1.001 servicios para mayores de DATA-009 es casual.
- **Farmacias:** categoría propia `pharmacy` (migración 0006; test `test_pharmacies_are_their_own_category_and_never_health`). La capa `health` queda en 550 lugares: atención primaria, salud mental y hospitales.
- **Coordenadas:** 42 lugares geocodificados con CartoCiudad (38 sin coordenadas y 4 reubicados), siempre a nivel de portal y en el municipio declarado (tests en `tests/unit/pipelines/test_place_coordinates.py`).
- **Cuarentena:** educación 55 → 39; sanidad 11 → 5; mayores 47 → 34; farmacias 4 → 0. Lo que queda no tiene número de portal («S/N», carreteras por kilómetro) o el geocodificador no lo encuentra en su municipio.
- **Duplicados:** ninguno con el mismo identificador. Hay 13 pares del mismo tipo a menos de 10 m; 12 tienen nombre o dirección distintos (centros distintos en el mismo edificio o parcela) y se mantienen. Un caso es sospechoso y queda anotado (§3).

## 1. Recuentos frente a los totales oficiales

| Tipo | Nuestro recuento | Oficial | Fecha | Fuente | Nota |
|---|---|---|---|---|---|
| Centros de salud (SERMAS) | 268 | 265 | 30 jun 2026 | [CM, nota de prensa sobre la Atención Primaria](https://www.comunidad.madrid/node/116506) | El registro de centros sanitarios autoriza edificios; el SERMAS cuenta equipos. D ve unos 10 consultorios inscritos como «centro de salud» (M2). |
| Consultorios locales (SERMAS) | 149 | 163 | 30 jun 2026 | [CM, la misma nota](https://www.comunidad.madrid/node/116506) | Centros de salud + consultorios: 417 SERMAS frente a 428 (−2,6 %). |
| Hospitales (todos) | 85 | 85 (CM, 2023) · 91 (CNH 2025) | 2023 · 31 dic 2024 | [CM «Hospitales y datos asistenciales» · Ministerio de Sanidad, Catálogo Nacional de Hospitales 2025](https://datos.comunidad.madrid/dataset/1912744) | El CNH cuenta uno a uno los hospitales de un complejo y los «otros centros con internamiento»; el registro CM coincide con la estadística CM. |
| Oficinas de farmacia | 2957 | 2.950 (CM, 2025) · 2.948 (CGCOF) | 1 ene 2025 · 31 dic 2025 | [CM `cm_farmacias_municipios` · Consejo General de Farmacéuticos](https://www.farmaceuticos.com/wp-content/uploads/2026/05/2025-Estadisticas-Colegiados-Farmacias_version-corta-11062026.pdf) | El registro es de hoy y la estadística, anual (D7: ±1 en Alcobendas y Collado Villalba). |
| Colegios públicos con primaria | 811 | 769 (tipo «Infantil y Primaria») | curso 2024-25 | [CM, «Datos y cifras de la educación 2025-2026», tabla 11](https://gestiona3.madrid.org/bvirtual/BVCM051753.pdf) | Nuestro recuento suma CEIP (717), CEIPSO (93) y CEP (1); la tabla oficial cuenta los CEIPSO en otro tipo, así que la comparación buena es CEIP: 717 frente a 769, el registro va un curso por delante. |
| Colegios concertados con primaria | 431 | 429 (fila «Primaria y Secundaria») | curso 2024-25 | [CM, «Datos y cifras de la educación 2025-2026», tabla 11](https://gestiona3.madrid.org/bvirtual/BVCM051753.pdf) | Tipologías distintas: la tabla agrupa por enseñanzas impartidas. |
| Escuelas infantiles públicas (0–3) | 488 | 486 (+85 CEIP con aula de 0–3) | curso 2024-25 | [CM, «Datos y cifras de la educación 2025-2026», figura 15](https://gestiona3.madrid.org/bvirtual/BVCM051753.pdf) | Las privadas de 0–3 no se publican como tales. |
| Residencias de mayores | 482 | 478 centros · 55.457 plazas | 31 dic 2024 | [IMSERSO, «Servicios sociales dirigidos a las personas mayores. Informe 2024»](https://imserso.es/documents/20123/10902543/inf_ssppmmesp2024.pdf/1432577e-5e36-5d7c-83d1-24864192dc99) | Coincide. |
| Centros de día de mayores | 314 | 319 · 16.393 plazas | 31 dic 2024 | [IMSERSO, informe 2024](https://imserso.es/documents/20123/10902543/inf_ssppmmesp2024.pdf/1432577e-5e36-5d7c-83d1-24864192dc99) |  |
| Hogares y clubes (centros de mayores) | 218 | 231 | 31 dic 2024 | [IMSERSO, informe 2024](https://imserso.es/documents/20123/10902543/inf_ssppmmesp2024.pdf/1432577e-5e36-5d7c-83d1-24864192dc99) | El Ayuntamiento de Madrid tiene además 93 centros municipales de mayores (Carta de Servicios 2026) que no están en el registro de la CM. |

## 2. Mismo tipo a menos de 10 m (posibles duplicados)

| Registro | Tipo | Id A | Id B | Nombre A | Nombre B | m |
|---|---|---|---|---|---|---|
| cm_centros_atencion_social | CENTROS DE DÍA: OTROS | C2666 | C8261 | GRAN RESIDENCIA, CENTRO DE DIA | CENTRO DE VIDAD VISTA ALEGRE | 0.0 |
| cm_centros_atencion_social | CENTROS DE DÍA: OTROS | C3144 | C9086 | CENTRO DE DIA NUESTRA SEÑORA DE BUTARQUE | CENTRO DE DIA NUESTRA SEÑORA DE BUTARQUE II | 0.0 |
| cm_centros_educativos | CENTRO PRIVADO DE EDUCACIÓN INFANTIL, PRIMARIA Y SECUNDARIA | 28026456 | 28038562 | AMANECER | ALKOR | 8.6 |
| cm_centros_educativos | COLEGIO DE EDUCACIÓN INFANTIL Y PRIMARIA | 28037533 | 28037521 | BLAS DE OTERO | FERNANDO DE LOS RIOS | 0.0 |
| cm_centros_educativos | ESCUELA INFANTIL PRIVADA | 28059826 | 28081534 | ARCO IRIS | ARCO IRIS MORATALAZ | 0.0 |
| cm_centros_educativos | ESCUELA INFANTIL PRIVADA | 28062953 | 28050264 | DINA CONDADO | CASCABEL | 0.0 |
| cm_centros_educativos | ESCUELA INFANTIL PRIVADA | 28062953 | 28062965 | DINA CONDADO | DINA CONDADO-2 | 0.0 |
| cm_centros_educativos | ESCUELA INFANTIL PRIVADA | 28062965 | 28050264 | DINA CONDADO-2 | CASCABEL | 0.0 |
| cm_centros_educativos | ESCUELA INFANTIL PRIVADA | 28070020 | 28080839 | EDUCANDO | EDUCANDO V | 0.0 |
| cm_centros_educativos | ESCUELA INFANTIL PRIVADA | 28082277 | 28068165 | EL GLOBO CELESTE II | EL GLOBO CELESTE | 0.0 |
| cm_centros_sanitarios | Centro de salud | CS21856 | CS1140 | Centro de salud (Madrid) | Centro de salud (Madrid) | 0.0 |
| cm_centros_sanitarios | Consultorio de atención primaria | CS12726 | CS13403 | Consultorio de atención primaria (Piñuécar-Gandullas) | Consultorio de atención primaria (Piñuécar-Gandullas) | 0.0 |
| cm_centros_sanitarios | Hospital general | CH0017 | CH0018 | Hospital general (Madrid) | Hospital general (Madrid) | 0.0 |

Lectura de los duplicados:
- Educación y mayores: nombres distintos en la misma parcela (por ejemplo, «DINA CONDADO» y «DINA CONDADO-2», o los CEIP Blas de Otero y Fernando de los Ríos). Son centros distintos en el registro oficial y se mantienen.
- `CS21856` y `CS1140`: dos centros de salud en la calle de O'Donnell 55 (uno en la «planta quinta»). Pueden ser dos equipos en el mismo edificio o una doble inscripción; sin nombre en el registro no se puede saber. Con ellos salen 268 centros de salud del SERMAS frente a 265 publicados.
- `CH0017` y `CH0018`: dos hospitales privados en Juan Bravo 49 y 39 con las mismas coordenadas (unos 100 m de error en uno de ellos).
- `CS12726` y `CS13403`: los consultorios de Piñuécar (28737) y Gandullas (28738) comparten coordenadas, así que uno está mal (son dos pueblos). Ninguno tiene número de portal: queda anotado y no se corrige.

## 3. Clasificación
| Antes | Después | Por qué |
|---|---|---|
| 1.001 «Centro Polivalente» en `health` | fuera del registro de lugares | Clínicas privadas, no atención primaria ni hospitales; minimización (ya se excluían las consultas privadas) |
| 2.953 farmacias en `health` | 2.957 en `pharmacy` (4 recuperadas) | Servicio propio con su fila en la lista de lo que falta; no es un centro sanitario de la capa de salud |
| Residencias, centros de día y hogares en `social` | sin cambios | Ya separados por subcategoría; `centros_mayores_por_1000_mayores` cuenta hogares y centros de día |

## 4. Revisión de D (10 zonas)
| Caso | Estado | Detalle |
|---|---|---|
| D1 · 8 centros de atención primaria sin coordenadas | 4 recuperados, 4 sin resolver | Recuperados: CS1135 y CS19950 (Madrid), CS9495 (Gargantilla) y CS15364. Sin resolver: CS1184 y CS6158 (Madrid) y CS10286 y CS7529 (Alcalá), todos «S/N». CS11438 (Villar del Olmo, «calle Real 42»): el geocodificador lo lleva a Jaén y se rechaza. Alcalá sigue con 8 centros (0,39 por 10.000) |
| D2 · colegios sin coordenadas | 1 de 2 | Humanitas El Cañaveral recuperado (Vicálvaro, portal 21 por el 20). CEIP Navalafuente: el portal conocido más cercano es el 16 para el 56; queda en cuarentena y la demo sigue diciendo 0 colegios y 63 min |
| D3 · farmacias | resuelto | Las 4 sin coordenadas, recuperadas. La 763 (Afueras a Valverde 36) pasa de Valdemoro a Madrid (Fuencarral-El Pardo) |
| D4 · CEIP Amorós | resuelto | De Tetuán a Carabanchel (Joaquín Turina, portal 27 por el 37; confidence 0,6) |
| D5 · CEIP Nuria Espert | se mantiene en Barajas | Su dirección (María Reiche 34) no contradice las coordenadas y las secciones oficiales lo ponen en Barajas; el registro dice Hortaleza. Anotado. Otros 21 centros de Madrid tienen el mismo desacuerdo de etiqueta, casi todos en límites de distrito |
| D6 · base de población de Madrid | declarado (D-209, D-216) | Municipio con el censo CM y distritos con el padrón (+1,7 %). En el 2SFCA (D-217) los distritos se escalan al censo |
| D7 · farmacias ±1 | anotado | Registro diario frente a estadística anual |
| M1–M3 | golden de la T2 | San Martín de Valdeiglesias, consultorios inscritos como centro de salud, La Acebeda |

## 5. Pendiente y deuda encontrada
- Los 4 centros de salud «S/N» y el CEIP de Navalafuente necesitan coordenadas de la fuente. Propuesta: avisar al portal de la CM; mientras tanto, SIN DATOS en su lugar exacto, nunca 0 en la fila por municipio (hoy cuentan 0 porque el lugar no existe; deuda `geocoding_quarantine` del board).
- **Bug del runner encontrado:** si una ingesta falla después de registrar la versión, la versión queda marcada con el parser nuevo y la siguiente ejecución se la salta («same checksum and parser»). Se resolvió a mano en la base local; hay que arreglarlo en `versions.register_version`.
- El 12 nov el registro de centros sanitarios se descargó de nuevo (actualización diaria): cambian algunos recuentos de un día para otro.
