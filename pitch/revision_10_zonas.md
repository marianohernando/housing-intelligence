# Revisión de 10 zonas: la demo frente a la fuente oficial

Comprobación a mano del 12 nov (fase de prueba y calidad, `~/Desktop/DATAMAD/prompts/FASE_PRUEBAS.md`, línea D, tarea 2). Para cada zona se compara lo que dice la demo en producción con la fuente oficial: colegios, centros de salud, farmacias, población y alquiler. Las discrepancias van numeradas (D1…) para la auditoría de datos de A (T1). Las notas de método (M1…) van para el trabajo de capacidad (T2).

**Resultado en una línea:** en las 10 zonas, la demo cuenta lo mismo que la fuente salvo en un caso. Al recontar la fuente oficial con los mismos filtros, cuadran todas las cifras de 9 de las 10 zonas. La excepción es Madrid capital: le faltan 4 centros de salud, 1 colegio y 3 farmacias, porque la fuente no trae sus coordenadas o las trae mal. El mismo fallo aparece fuera de la muestra, y ahí sí cambia lo que ve una persona: Alcalá de Henares saldría CUBIERTO y no JUSTO en centros de salud, y Navalafuente y Villar del Olmo aparecen sin colegio o sin centro de salud cuando sí los tienen.

## Qué ha hecho A con esto (12 nov, D-216 y D-217)
Respuesta de A en `evidence/gate-01/2026-11-12/audit-places.md` §4. Lo de abajo de este fichero queda como estaba el 12 nov a las 0:40, antes de esos cambios.

| Caso | Estado |
|---|---|
| D1 · centros de atención primaria sin coordenadas | 3 de 8 recuperados con CartoCiudad (CS1135 y CS19950 en Madrid, CS9495 en Gargantilla). Siguen sin lugar los 4 «S/N» (CS1184 y CS6158 en Madrid, CS10286 y CS7529 en Alcalá) y el consultorio de Villar del Olmo (CS11438), cuya dirección lleva a Jaén. Con gap-0.3, Alcalá ya sale CUBIERTO en centros de salud (0,395 frente a 0,3694, `evidence/gate-04/2026-11-12/gap-status-gap03.md`) aunque le falten esos dos |
| D2 · colegios sin coordenadas | Humanitas El Cañaveral, recuperado. El CEIP de Navalafuente sigue en cuarentena: la demo aún dice 0 colegios y 63 min |
| D3 · farmacias | Resuelto: las 4 sin coordenadas, recuperadas; la 763 pasa de Valdemoro a Fuencarral-El Pardo |
| D4 · CEIP Amorós | Resuelto: de Tetuán a Carabanchel |
| D5 · CEIP Nuria Espert | Se queda en Barajas: la dirección no contradice las coordenadas y las secciones del INE lo ponen ahí |
| D6 · base de población de Madrid | Declarado (D-209, D-216 §5); en el 2SFCA los distritos se escalan al censo |
| D7 · farmacias ±1 | Anotado: registro diario frente a estadística anual |
| M1 · San Martín de Valdeiglesias | Con gap-0.3 pasa de FALTA a CUBIERTO en centros de salud (1,594, poco fiable: no tiene vecinos suficientes a 15 km) |
| M2 · consultorios | Ya no cuentan como capacidad: solo para los minutos a pie (D-217 §3) |
| M3 · La Acebeda | 0 a pie, poco fiable (D-217 §7) |

Lo que queda abierto es de la fuente: 4 centros de salud y 1 colegio sin dirección geocodificable. A propone avisar al portal de la CM y, mientras tanto, enseñar SIN DATOS en vez de 0 (deuda `geocoding_quarantine` del board).

## Cómo se ha hecho
- **Demo:** API de producción, https://vidafacil-madrid.vercel.app/api/v1, consultada el 12 nov entre las 0:20 y las 0:40.
  - `GET /gaps/{nivel}/{código}`: estado, valor, referencia y si la zona es pequeña para comparar.
  - `GET /places?category=…&admin_unit_id=…`: los puntos de cada zona.
  - `GET /features/{id}/values?level=…`: población y alquiler.
  - `POST /search`: el alquiler en la tarjeta de zona.

  El número de colegios de la demo sale de su tasa por el denominador oficial (por ejemplo, 1,267 × 412.815 menores / 1.000 = 523). Así se aplica el mismo filtro de titularidad, que `/places` no expone. En centros de salud y farmacias, la tasa y los puntos de `/places` dan lo mismo.
- **Fuente oficial:** los ficheros del portal, descargados el 12 nov. Se recuentan con los mismos filtros que el catálogo:
  - colegios: tipos con primaria, titularidad pública o concertada y situación «ALTA» (`data/catalog/features/colegios_publicos_por_1000_menores.yaml` y `data/catalog/pipelines/cm_centros_educativos.yaml`);
  - centros de salud: «Centro de salud» y «Consultorio de atención primaria», un centro por número de registro (`centros_salud_por_10000_hab.yaml`);
  - farmacias: todas las del registro (`oficinas_farmacia_por_10000_hab.yaml`).

  En los distritos, los colegios se asignan con el campo `DISTRITO` de la fuente y también por coordenadas. Los centros de salud y las farmacias, que no traen distrito, van por coordenadas, sobre los límites de distrito de la API sin simplificar (`/geo/admin-units?level=distrito&parent=ES.28.MUN.28079&simplify_m=0`).
- **Fuentes independientes,** para no comparar la demo solo consigo misma:
  - población: el padrón del INE a 1 de enero de 2025;
  - centros de salud: el total del Servicio Madrileño de Salud;
  - farmacias: la estadística anual de la Comunidad, aparte del registro de puntos.

### Enlaces exactos
| Dato | Ficha | Fichero usado |
|---|---|---|
| Colegios | https://datos.comunidad.madrid/dataset/centros_educativos | https://datos.comunidad.madrid/dataset/c750856d-3166-4dac-8e80-d1b824c968b5/resource/28d60557-1d73-4281-ab08-6cfd3b2f5f83/download/centros_educativos.csv |
| Centros de salud | https://datos.comunidad.madrid/dataset/centros_servicios_establecimientos_sanitarios | https://datos.comunidad.madrid/dataset/d8a0a444-adf5-4c04-8999-0eac3de52cb7/resource/2948b4da-8b39-42b7-b667-779a5284f39d/download/centros_servicios_establecimientos_sanitarios.csv |
| Farmacias (registro con puntos) | https://datos.comunidad.madrid/dataset/oficinas_farmacia | https://datos.comunidad.madrid/dataset/2d682b1d-e2e8-4c6f-b902-7a3f108e2fb9/resource/904a161b-f339-4296-be61-1ae914494c89/download/oficinas_farmacia.csv |
| Farmacias (estadística por municipio, 2025) | https://datos.comunidad.madrid/dataset/farmacias | https://datos.comunidad.madrid/dataset/b5e80c83-8e90-4bb5-8648-9f107174fd56/resource/b1187273-5f62-4938-82a3-69d736c3ab0b/download/recursos-sanitarios.-farmacias.-municipios.csv |
| Población por municipio (censo anual, 1 ene 2025) | https://datos.comunidad.madrid/dataset/poblacion_censada_por_edad_nacionalidad_y_sexo | https://datos.comunidad.madrid/dataset/0a14fbfe-783e-4de3-81b1-ff3792bfd402/resource/bab16922-8df1-49b5-9791-aed4edf8ced1/download/poblacion-censada-por-edad-nacionalidad-y-sexo.-censo-anual.-municipios.csv |
| Población por distrito (padrón del Ayuntamiento, 1 oct 2026) | https://datos.madrid.es/dataset/200076-0-padron | https://datos.madrid.es/dataset/200076-0-padron/resource/200076-2-padron-csv/download/padron.csv |
| Población, comprobación independiente (padrón del INE, 1 ene 2025) | https://www.ine.es/jaxiT3/Tabla.htm?t=2881 | https://servicios.ine.es/wstempus/js/ES/DATOS_TABLA/2881?nult=2 |
| Alquiler €/m² por municipio (2024) | https://datos.comunidad.madrid/dataset/alquiler_metro_cuadrado_mensual_viviendas_arrendadas_valor_catastral_municipios_mas_20000 | https://datos.comunidad.madrid/dataset/244448f3-7df9-4318-8603-92fb550fc865/resource/eb71efce-a7de-46d2-8447-dbf2c8d196b6/download/alquiler-del-metro-cuadrado-mensual-de-viviendas-arrendadas-con-valor-catastral-para-municipios-.csv |
| Alquiler €/m² por código postal de Madrid (2024) | https://datos.comunidad.madrid/dataset/1934259 | https://datos.comunidad.madrid/dataset/7b1e0527-da4c-4c93-8a58-a53879f9c6b8/resource/70c3f1f8-534d-41bc-b4ba-6125cdf10628/download/alquiler-del-metro-cuadrado-medio-mensual-de-viviendas-habituales-arrendadas-por-codigo-postal-p.csv |
| Atención primaria: total oficial | https://www.comunidad.madrid/node/111983 (nota del 10 abr 2026: «265 centros de salud, 163 consultorios locales y 80 puntos de atención continuada») | — |

## Las 10 zonas
Hay 4 de Madrid capital y 6 municipios: urbanos y rurales, grandes y pequeños, con alquiler publicado y sin él, y dos «zonas pequeñas para comparar».

| Zona | Nivel y código | Tipo (`reference_label`) | Población en la demo |
|---|---|---|---|
| Madrid (entera) | municipio 28079 | urbano | 3.477.497 |
| Centro | distrito 2807901 | urbano | 143.174 |
| Ciudad Lineal | distrito 2807915 | urbano | 231.447 |
| Barajas | distrito 2807921 | urbano | 51.221 |
| Móstoles | municipio 28092 | urbano | 214.293 |
| Alcobendas | municipio 28006 | urbano | 123.222 |
| Collado Villalba | municipio 28047 | urbano | 67.956 |
| San Martín de Valdeiglesias | municipio 28133 | rural | 9.302 |
| Rascafría | municipio 28120 | rural, zona pequeña en las 3 filas | 1.698 |
| La Acebeda | municipio 28001 | rural, zona pequeña en las 3 filas | 70 |

## Resultado por zona
✓ = igual que la fuente; ≠ = discrepancia, con su número.

### Colegios con primaria, públicos o concertados (en alta)
| Zona | Demo | Fuente oficial | |
|---|---|---|---|
| Madrid | 523 | 524 | ≠ D2 |
| Centro | 18 | 18 | ✓ |
| Ciudad Lineal | 36 | 36 | ✓ |
| Barajas | 8 | 8 por coordenadas; 7 según el campo `DISTRITO` de la fuente | ≠ D5 |
| Móstoles | 40 | 40 | ✓ |
| Alcobendas | 19 | 19 | ✓ |
| Collado Villalba | 13 | 13 | ✓ |
| San Martín de Valdeiglesias | 2 | 2 | ✓ |
| Rascafría | 1 | 1 | ✓ |
| La Acebeda | 0 | 0 | ✓ |

### Centros de salud y consultorios de atención primaria
| Zona | Demo | Fuente oficial | |
|---|---|---|---|
| Madrid | 129 (126 + 3 consultorios) | 133 (130 + 3) | ≠ D1 |
| Centro | 7 (6 + 1) | 7 | ✓ |
| Ciudad Lineal | 8 | 8 | ✓ |
| Barajas | 2 | 2 | ✓ |
| Móstoles | 10 | 10 | ✓ |
| Alcobendas | 6 | 6 | ✓ |
| Collado Villalba | 4 (3 + 1) | 4 | ✓ |
| San Martín de Valdeiglesias | 1 | 1 | ✓ (el estado, FALTA, ver M1) |
| Rascafría | 2 (1 + 1) | 2 | ✓ |
| La Acebeda | 1 consultorio | 1 | ✓ |

### Farmacias
| Zona | Demo | Registro con puntos | Estadística anual 2025 | |
|---|---|---|---|---|
| Madrid | 1.811 | 1.814 | 1.814 | ≠ D3 |
| Centro | 103 | 103 | — | ✓ |
| Ciudad Lineal | 128 | 128 | — | ✓ |
| Barajas | 27 | 27 | — | ✓ |
| Móstoles | 73 | 73 | 73 | ✓ |
| Alcobendas | 38 | 38 | 37 | ✓ (D7: fechas distintas) |
| Collado Villalba | 21 | 21 | 20 | ✓ (D7) |
| San Martín de Valdeiglesias | 3 | 3 | 3 | ✓ |
| Rascafría | 1 | 1 | 1 | ✓ |
| La Acebeda | 0 | 0 | 0 | ✓ |

### Población
| Zona | Demo | Misma fuente | INE, padrón a 1 ene 2025 | |
|---|---|---|---|---|
| Madrid | 3.477.497 (censo anual CM, 1 ene 2025) | ✓ | 3.506.730 (+0,8 %) | ≠ D6 (con los distritos) |
| Centro | 143.174 (padrón municipal, 1 oct 2026) | ✓ | — | ✓ |
| Ciudad Lineal | 231.447 | ✓ | — | ✓ |
| Barajas | 51.221 | ✓ | — | ✓ |
| Móstoles | 214.293 | ✓ | 214.817 (+0,2 %) | ✓ |
| Alcobendas | 123.222 | ✓ | 123.342 (+0,1 %) | ✓ |
| Collado Villalba | 67.956 | ✓ | 67.274 (−1,0 %) | ✓ |
| San Martín de Valdeiglesias | 9.302 | ✓ | 9.324 (+0,2 %) | ✓ |
| Rascafría | 1.698 | ✓ | 1.704 (+0,4 %) | ✓ |
| La Acebeda | 70 | ✓ | 70 | ✓ |

El censo anual y el padrón son dos estadísticas oficiales distintas y difieren un poco; no es un error. La demo usa siempre el censo anual de la Comunidad para los municipios (`data/catalog/features/poblacion_total.yaml`).

### Alquiler (€/m² al mes, viviendas habituales, 2024)
| Zona | Demo | Fuente oficial | |
|---|---|---|---|
| Madrid | 15,1 | 15,1 | ✓ |
| Centro | 18,4 (aproximación por códigos postales, fiabilidad 0,8) | Códigos con barrios del distrito: 28012 Embajadores 17,8; 28013 Centro 18,4; 28004 Justicia 19,3. Los que comparte con distritos vecinos van de 17,2 a 19,1 | ✓ dentro del rango |
| Ciudad Lineal | 14,0 (la tarjeta: «Alquiler medio ≈ 1.075 €/mes por 77 m² (14,0 €/m²…)») | 28017 Ventas-Ciudad Lineal-La Elipa 13,1; 28027 San Juan Bautista 14,3. Los compartidos van de 13,7 a 14,9 | ✓ dentro del rango |
| Barajas | 13,8 | 28042 Barajas-La Alameda de Osuna 13,7. Los compartidos: 12,8 y 15,0 | ✓ |
| Móstoles | 9,6 | 9,6 | ✓ |
| Alcobendas | 12,7 | 12,7 | ✓ |
| Collado Villalba | 9,9 | 9,9 | ✓ |
| San Martín de Valdeiglesias, Rascafría y La Acebeda | Sin datos | La fuente publica «-»: solo da municipios de más de 20.000 habitantes | ✓ |

El alquiler de los distritos es una media de sus códigos postales, ponderada por dónde están los colegios, centros de salud y centros sociales. Es una aproximación declarada (D-214, `alquiler_m2_mensual.yaml`), y en los tres distritos queda dentro del rango de sus códigos.

## Discrepancias, para A (auditoría de datos, T1)
Ordenadas por lo que cambian en pantalla.

**D1. Centros de salud sin coordenadas: 8 en la región, 4 de ellos en Madrid.** El registro oficial no trae coordenadas en 8 centros de atención primaria. La demo no puede situarlos y los deja fuera:
| Registro | Tipo | Municipio | Dirección (código postal) |
|---|---|---|---|
| CS1135 | Centro de salud | Madrid | Calle del Jazmín (28033) |
| CS1184 | Centro de salud | Madrid | Calle de Arenas del Rey (28041) |
| CS19950 | Centro de salud | Madrid | Calle del Pintor Moreno Carbonero (28028) |
| CS6158 | Centro de salud | Madrid | Calle de Mirueña (28024) |
| CS10286 | Centro de salud | Alcalá de Henares | Calle Ramón María del Valle Inclán (28806) |
| CS7529 | Centro de salud | Alcalá de Henares | Calle Juan de Borgoña (28805) |
| CS11438 | Consultorio | Villar del Olmo | Calle Real (28512) |
| CS9495 | Consultorio | Gargantilla del Lozoya y Pinilla de Buitrago | Calle Carretas (28739) |

Efecto en pantalla:
- **Alcalá de Henares** sale JUSTO en centros de salud: 8 centros, 0,395 por 10.000 habitantes, el 0,85 de su referencia (0,4654). Con sus 2 centros, serían 10 y 0,494, es decir, el 1,06 de la referencia: **CUBIERTO**.
- **Villar del Olmo** sale con 0 centros y el más cercano a 51 min andando, cuando tiene su consultorio. **Gargantilla** sale a 50 min andando.
- **Madrid** pasa de 0,371 a 0,382 por 10.000 habitantes. Sigue FALTA, con una ratio de unos 0,69 en lugar de 0,67.
- Los 4 centros de Madrid tampoco cuentan en sus distritos. Sin coordenadas no se puede saber en cuál están, aunque los códigos postales apuntan a varios.

Posible causa: huecos de la fuente. Arreglo posible: geocodificar por dirección, por ejemplo con CartoCiudad, el geocodificador oficial del IGN. Los puntos geocodificados se marcarían con menos fiabilidad. Lo decide A.

**D2. Colegios sin coordenadas: 2 en la región.**
- CEIP Navalafuente (28082174, Navalafuente): es el colegio del pueblo. La demo dice que Navalafuente no tiene colegio y que el más cercano está a 63 min andando.
- Humanitas Bilingual School El Cañaveral (28082541, concertado, Madrid, Vicálvaro): falta 1 en Madrid y en Vicálvaro.

Misma causa y mismo arreglo que D1.

**D3. Farmacias: 4 sin coordenadas y 1 situada en otro municipio.**
- Sin coordenadas:
  - registro 178 (Calle de Hortaleza 2, Madrid);
  - 1899 (Calle de la Campiña 12, Madrid);
  - 2683 (Arganda del Rey);
  - 2976 (Villaviciosa de Odón).
- Mal situada: la 763, Calle de Afueras a Valverde 36. Su dirección está en Madrid (Fuencarral), pero sus coordenadas caen en Valdemoro, unos 25 km al sur, y la demo la cuenta en Valdemoro.

Efecto: Madrid tiene 3 menos y Valdemoro 1 más. Con 1.811 farmacias no cambia ningún estado. Causa: errores de la fuente.

**D4. Colegio con coordenadas en otro distrito: CEIP Amorós** (28011261). Su dirección es Joaquín Turina 37, 28044, en Carabanchel, y el campo `DISTRITO` de la fuente dice Carabanchel. Sus coordenadas caen en Tetuán, cerca de Plaza de Castilla, y la demo lo cuenta en Tetuán (`/places?category=education&admin_unit_id=ES.28.DIS.2807906`). Causa: coordenadas erróneas en la fuente. Arreglo posible: cuando el distrito de la fuente y el de las coordenadas no coinciden, revisar el punto con la dirección.

**D5. Colegio en el límite de Barajas y Hortaleza: CEIP Nuria Espert** (28079424, María Reiche 34, 28055, Valdebebas). La fuente dice Hortaleza y sus coordenadas caen en Barajas según los límites de distrito de la demo, que salen de las secciones censales. Puede ser el límite real de Valdebebas o una geometría distinta de la que usa la Comunidad. Efecto: Barajas tiene 8 colegios en la demo y 7 según el campo de la fuente; Hortaleza, 1 menos. Hay que comprobarlo con la cartografía de distritos del Ayuntamiento.

**D6. Madrid y sus distritos usan poblaciones distintas.**
- Madrid entera usa el censo anual de la Comunidad a 1 ene 2025: 3.477.497.
- Los distritos usan el padrón municipal a 1 oct 2026, que suma 3.535.868, un 1,7 % más.
- El padrón del INE a 1 ene 2025 da 3.506.730.

No cambia ningún estado de la muestra, pero las tasas de los distritos y la de Madrid no son del todo comparables. Conviene declararlo en «Cómo lo calculamos» o usar la misma fecha.

**D7. Farmacias: el registro y la estadística anual difieren en 1.** Pasa en Alcobendas (38 frente a 37) y en Collado Villalba (21 frente a 20). En la región hay 2.957 puntos en el registro, 2.953 en la demo y 2.950 en la estadística de 2025. Son dos fuentes de fechas distintas, así que no es un error; solo lo anoto.

## Notas de método, para A (capacidad, T2)
**M1. Un pueblo con un centro de salud grande sale FALTA.** San Martín de Valdeiglesias tiene 1 centro de salud para 9.302 habitantes: 1,075 por 10.000. Los demás municipios rurales están en 7,27, porque cada aldea tiene su consultorio y un consultorio en un pueblo de 200 habitantes dispara la tasa. Con una ratio de 0,15 y la zona fiable, sale **FALTA**, y no es lo que vería un vecino. Es el límite que ya declara la fila («un consultorio rural pesa igual que un centro de salud grande»). Contar capacidad o población asignada por zona básica de salud (T2) debería corregirlo. Es un buen caso de prueba para el método nuevo.

**M2. Totales de atención primaria en la región.**
- La demo: 270 centros de salud y 151 consultorios, 421 en total.
- El registro: 276 y 153, 429 en total. Incluye 7 centros que no son del Servicio Madrileño de Salud (Cruz Roja, Instituto de Salud Carlos III y otros públicos).
- El Servicio Madrileño de Salud: 265 y 163, 428 en total (nota del 10 abr 2026).

El total cuadra, pero la clasificación difiere: el registro llama «centro de salud» a unos 10 que el Servicio Madrileño de Salud cuenta como consultorios. A la fila no le afecta, porque suma los dos tipos. Si T2 los separa por capacidad, conviene saberlo.

**M3. Zonas pequeñas.** Rascafría y La Acebeda salen «zona pequeña para comparar» en las 3 filas, como se espera (D-213). La Acebeda, con 70 habitantes, sale CUBIERTO en centros de salud (142,9 por 10.000) con un solo consultorio. Es correcto, pero llama la atención: es el problema de escala que FASE_PRUEBAS pide revisar.

## Qué no se ha comprobado
- **El 3D y las etiquetas de cada zona:** B enseña en T3 todos los centros de cada zona.
- **Hospitales, escuelas infantiles, mayores y vivienda:** quedan para la auditoría de A (T1).
- **Que cada colegio esté donde dice la fuente:** solo se han revisado los casos en que el distrito de la fuente y el de las coordenadas no coinciden (D4 y D5).

## Cómo repetirlo
Hay que descargar los ficheros de la tabla de enlaces y recontarlos con los filtros de «Cómo se ha hecho». En la demo se consultan las mismas rutas con los códigos de la tabla de zonas. Los recuentos de este informe salen de un script de un solo uso que no se versiona; las cifras y los registros citados bastan para comprobarlas una a una.
