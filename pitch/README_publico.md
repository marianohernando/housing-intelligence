<!--
Borrador de la línea D para el README.md de la raíz (lo integra la línea A, que es su dueña).
- Los enlaces son relativos a la raíz del repo, como quedarán en README.md; desde pitch/ no funcionan.
- Las notas entre comentarios como este no se ven en GitHub: dicen de dónde sale cada cifra y qué está pendiente.
- Antes de integrarlo: fusionar el PR #11 (trae la captura C1), quitar las marcas «pendiente» y revisar las cifras con `uv run python pitch/build_datasets_cm.py`.
-->

# Vida Fácil · Encuentra tu sitio en Madrid

Quien busca casa en Madrid mira el precio en una web, los colegios en otra y el transporte en otra, y nadie le dice qué zona va con su vida. Un ayuntamiento que quiere saber dónde falta una escuela infantil o un centro de salud tiene los datos sueltos. **Vida Fácil cruza los datos abiertos de la Comunidad de Madrid para enseñarte qué zonas encajan contigo y qué le falta a cada una.**

**Pruébalo:** [vidafacil-madrid.vercel.app](https://vidafacil-madrid.vercel.app)

<!-- URL verificada el 11 nov con el buscador encendido: smoke 7/7 con datos reales de Supabase, axe AA sin fallos y la consola limpia (evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md, PR #11 de la línea C). Despliegue: infra/deploy/README.md. -->

![Vida Fácil: mapa de la Comunidad de Madrid con la búsqueda de una pareja con 2 hijos, las zonas coloreadas según cuánto encajan y la tarjeta de la zona que más encaja](evidence/gate-06/2026-11-11-deploy/prod-buscador-c1_busqueda_desktop.png)

<!-- Captura C1 de pitch/slides.md: producción, 11 nov, 1440 px, caso de la Castellana con la tarjeta de Ciudad Lineal. La hizo C y está en la rama claude/s1-deploy (PR #11): la imagen se ve cuando se fusione. -->

---

## Qué datos usamos

**21 conjuntos de datos del [Portal de Datos Abiertos de la Comunidad de Madrid](https://datos.comunidad.madrid), todos con su control de calidad superado:**
- población, hogares, vivienda, renta y alquiler;
- colegios, centros de salud, servicios para mayores y farmacias;
- las 6 redes de transporte público del Consorcio Regional de Transportes, que también publica ese portal.

→ **[Lista completa, con el enlace a cada ficha, su licencia, para qué la usamos y su informe de calidad](pitch/datasets_cm.md)**

**Los cubrimos todos:** los 179 municipios de la región, y Madrid capital dividida en sus 21 distritos para que no sea un solo bloque.

Como apoyo, sin contarlos como datos de la Comunidad, usamos el padrón y el panel de distritos del Ayuntamiento de Madrid (población y hogares por distrito) y el mapa de calles de OpenStreetMap (distancias a pie).

<!--
Fuentes:
- 21 conjuntos y control de calidad: pitch/datasets_cm.md (generado desde data/catalog/ y evidence/gate-01/) y evidence/gate-01/2026-11-10/real-run-quality.txt (21 PASS).
- Los 6 GTFS del CRTM cuentan como datos CM porque el portal los publica: D-196.
- 179 municipios: evidence/gate-01/2026-10-20/cm_secciones_censales/row_counts.json.
- 21 distritos: D-200 y D-209 (población por distrito del padrón municipal del Ayuntamiento). DATA-012 hecha (be40c2f); GET /api/v1/gaps/distrito/2807905 (Chamartín) responde con datos reales.
- Red peatonal: evidence/gate-01/2026-11-11/osm_red_peatonal/.
-->

## Cómo funciona

1. **Cuéntanos cómo es tu hogar:** quién vive contigo, cuánto puedes pagar de alquiler, dónde trabajas y qué te importa (transporte, salud, colegios…).
2. **Mira las zonas que encajan contigo,** con su % de encaje y, debajo, hechos que puedes comprobar, como «colegio con primaria a 5 min andando». Cada uno dice cuánto nos fiamos del dato.
3. **¿Salen pocas?** Te enseñamos cuántas zonas aparecen si cambias una sola cosa, por ejemplo 150 € más al mes o el colegio a 5 minutos más.
4. **Entra en una zona y mira qué le falta:** escuela infantil, colegio, centro de salud, mayores, farmacia y vivienda, comparados con los demás municipios de su tipo, urbanos o rurales. Cada fila dice de qué datos sale y a cuántos minutos andando está lo más cercano.

Cómo se calcula cada cosa, con sus límites: pestaña **«Cómo lo calculamos»** de la demo.

<!--
- Pasos 1–3: POST /api/v1/search con datos reales (CORE-003 y CORE-006; D-214 y D-215; evidence/gate-04/2026-11-11/phase-core003-f2.txt). En producción desde el 11 nov (buscador de B, PR #10; encendido por C, PR #11; evidence/gate-06/2026-11-11-deploy/prod-buscador-check.json). El coste es orientativo y tira a la baja (D-214); el trabajo cuenta por distancia en línea recta hasta CORE-009. La compra se puede elegir, pero sale «Sin datos» hasta DATA-021 (D-214, punto 5): por eso el paso 1 solo nombra el alquiler.
- CONDICIÓN, cumplida el 11 nov: la demo desplegada tiene el buscador encendido (sin «Muy pronto»: apps/web/src/lib/capabilities.ts). Reserva, solo si la demo vuelve a «Muy pronto»: la sección queda así:
  1. **Elige una zona en el mapa:** cualquiera de los 179 municipios o de los 21 distritos de Madrid.
  2. **Mira qué tienes cerca:** sus colegios, centros de salud y estaciones en 3D, y cuántos minutos se tarda andando hasta cada servicio.
  3. **Mira qué le falta:** (el paso 4 de arriba).
  Y la entrada dice «para enseñarte qué tiene cerca cada zona y qué le falta».
- «colegio con primaria a 5 min andando» es un hecho real del caso de la Castellana (Ciudad Lineal, D-215). «150 € más» y «5 minutos más» son las relajaciones de D-215 (punto 8: presupuesto +10 % redondeado a 50 €; servicio cerca +5 min) en ese mismo caso.
- Paso 4: GET /api/v1/gaps/{level}/{code} (D-194), con las 6 filas en los 179 municipios y los 21 distritos (GAP-001 F1–F3b; en los distritos, vivienda sale SIN DATOS). Comparación con los municipios del mismo tipo: D-213 (gap-0.2, GAP-001 F5), en producción desde el 11 nov (GET /api/v1/gaps/municipio/28079 da gap-0.2). Minutos a pie en extra_indicators (GAP-001 F1).
- Compra: orientativa (D-203).
-->

## Arráncalo en tu ordenador

Necesitas Docker, [uv](https://docs.astral.sh/uv/) (Python 3.12) y Node 24.

```bash
cp .env.example .env                 # pon una contraseña en POSTGRES_PASSWORD
make dev                             # base de datos + migraciones + catálogo
make ingest-all                      # descarga y valida los datos abiertos, y calcula los indicadores
uv run uvicorn hi_api.main:app --port 8010           # API en http://localhost:8010
npm ci && NEXT_PUBLIC_API_URL=http://localhost:8010 npm run web:dev   # web en http://localhost:3010
```

`make help` lista todos los comandos. `make lint typecheck test` pasa las comprobaciones de calidad.

<!--
- make dev, make ingest-all, make help y make lint typecheck test: Makefile.
- uvicorn: infra/deploy/README.md (PR #4).
- web:dev en el puerto 3010: package.json y apps/web/package.json; NEXT_PUBLIC_API_URL: LINEAS.md.
- Pendiente de A: comprobar el recorrido completo en una máquina limpia antes de integrarlo.
-->

## Licencias

- **Código:** [Apache 2.0](LICENSE).
- **Documentación y catálogo de datos:** [CC BY 4.0](docs/LICENSE).
- **Datos de terceros:** cada uno conserva su licencia, recogida en [`data/catalog/sources/`](data/catalog/sources/):
  - Comunidad de Madrid, CC BY 4.0;
  - Consorcio Regional de Transportes de Madrid, licencia de datos abiertos del CRTM («Powered by CRTM»);
  - Ayuntamiento de Madrid, CC BY 4.0;
  - OpenStreetMap, ODbL.

<!-- D-191. Licencias por fuente: data/catalog/sources/*.yaml (license_name y attribution_text). Ayuntamiento de Madrid: CC BY 4.0, uso comercial y no comercial (https://datos.madrid.es/pages/condiciones-de-uso, leída el 11 nov); en uso desde DATA-012 (ayto_padron_municipal y ayto_panel_indicadores_distritos_barrios, pitch/datasets_cm.md §3). -->

## Qué había antes del concurso

Las bases de DATAMAD 2026 permiten partir de trabajo previo si se identifica (§6, «Proyectos preexistentes»). El nuestro está marcado con el tag [`pre-datamad`](https://github.com/marianohernando/housing-intelligence/tree/pre-datamad): commit `cf39459`, del 22 oct de 2026. Incluía la geografía común de la región, los primeros 10 conjuntos de datos y un mapa base.

Todo lo posterior se ha hecho durante el concurso (desde el 7 nov):
- el transporte público y otros 5 conjuntos de datos;
- la lista de lo que falta por zona;
- el buscador;
- las distancias a pie;
- la web y el despliegue.

Al publicar el repositorio, el 11 nov, reescribimos el historial solo para quitar datos de contacto de unos ficheros de prueba. Las fechas de los commits no cambian, y el repositorio original se conserva privado como prueba de fechas ([detalle](evidence/gate-00/2026-11-11/public-repo.md)).

<!--
- §6: docs/09_datamad/24_bases_oficiales_2026.md · D-174.
- Tag cf39459 = pre-datamad^{commit} (el tag anotado es e6bead3) · D-198.
- 10 conjuntos antes del concurso: evidence/gate-01/2026-10-22/summary.md (Gate 01 PASS, 10 datasets).
- Durante el concurso: board/BOARD.md (DATA-007, DATA-016, GAP-001, CORE-003, CORE-005, OPS-001). Las distancias a pie están hechas (CORE-005, D-210 y D-211) y la demo está desplegada con el buscador encendido (PR #6 y PR #11; CORE-003, D-215). Si el 18 nov la demo vuelve a «Muy pronto», el buscador se quita de la lista.
-->

## Equipo

Equipo de una persona: **Mariano** · [github.com/marianohernando](https://github.com/marianohernando)

<!-- Decisión de Mariano (11 nov): en el repo público solo «Mariano»; el nombre completo va solo en el PDF del deck y en el formulario. -->

Hecho con ayuda de asistentes de programación con IA, que las bases permiten (§7). Las decisiones, los datos y los resultados son responsabilidad del equipo.

<!-- §7: docs/09_datamad/24_bases_oficiales_2026.md. Mariano decide mantener esta línea (11 nov). Los commits ya lo reflejan (Co-Authored-By). -->

---

## Para quien quiera mirar por dentro

- **Estado del proyecto, día a día:** [`board/BOARD.md`](board/BOARD.md).
- **Controles de calidad de cada fase, con su evidencia:** [`evidence/`](evidence/). Por ejemplo, la ingesta de los 21 conjuntos de la Comunidad está en [`evidence/gate-01/2026-11-10/summary.md`](evidence/gate-01/2026-11-10/summary.md).
- **API pública y sus contratos:** [`docs/04_technical_architecture/31_public_api_routes.md`](docs/04_technical_architecture/31_public_api_routes.md), con los JSON Schema en [`data/schemas/api/`](data/schemas/api/).
- **Catálogo de fuentes, datasets e indicadores,** legible por máquina: [`data/catalog/`](data/catalog/).
- **Decisiones del proyecto:** [`docs/00_index/01_decisions_log.md`](docs/00_index/01_decisions_log.md).
- **Estructura del código:**
  - `apps/`: API en FastAPI y web en Next.js;
  - `packages/`: contratos, dominio y base de datos;
  - `services/`: ingesta e indicadores;
  - `infra/`: Docker, migraciones y despliegue;
  - `docs/`: documentación completa.
- **Plataforma:** Vida Fácil está construida sobre *Housing Intelligence*, el nombre técnico del repositorio (D-199).
