# Formulario de preselección DATAMAD 2026 — listo para copiar

**Enviado el 12 nov por Mariano, resumen principal (98 palabras).** Lo que sigue queda como registro de lo enviado y de su evidencia.

- **Formulario:** https://forms.gle/NyatKHN95aPxvQro8 («DATAMAD 2026 | Presentación de propuestas»). Plazo: antes del 20 nov; objetivo 18 nov y límite real 19 (`docs/09_datamad/25_plan_competicion.md` §5, D-193).
- **Quién lo envía:** Mariano. Este fichero no guarda datos personales porque el repo es público.
- **Campos:** son los del formulario real, leídos el 11 nov.

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## Campos, en orden

| # | Campo del formulario | Obligatorio | Qué poner |
|---|---|---|---|
| 1 | ¿Cómo vas a participar? | Sí | Marca: `Individualmente` (Mariano se presenta solo) |
| 2 | Nombre y apellidos | Sí | Tu nombre completo, listo para copiar en `pitch/formulario.local.md`. Ese fichero es local y git lo ignora: el nombre completo no se guarda en el repo público |
| 3 | Correo electrónico de contacto | Sí | **Lo rellenas tú:** el mismo email del formulario de inscripción inicial |
| 4 | Teléfono de contacto | Sí | **Lo rellenas tú** |
| 5 | Si participáis en equipo, indica los datos del resto de integrantes | Sí | Copia esto: `No aplica: participo individualmente.` |
| 6 | Nombre del proyecto | Sí | Copia esto: `Vida Fácil — Encuentra tu sitio en Madrid` |
| 7 | Describe brevemente vuestra propuesta (máximo 100 palabras) | Sí | Copia el **resumen principal**: el buscador está encendido en producción desde el 11 nov. La variante B queda de reserva (ver «Cuándo usar cada versión») |
| 8 | ¿Quieres compartir algún material adicional? | No | Copia el bloque de **enlaces** de abajo |
| 9 | Compromiso de asistencia presencial (26 nov) | Sí | **Lo marcas tú** |
| 10 | Confirmación de inscripción previa | Sí | **Lo marcas tú** |

La ayuda del campo 7 pide «qué queréis construir, qué problema aborda y cómo usaréis los datos abiertos». Los dos textos cubren las tres cosas.

## Campo 7 · Resumen principal (98 palabras) · la que vale hoy
Este texto da el buscador por hecho («le recomienda dónde vivir», «enseña cuántas zonas aparecen»). Ya lo es:
- el cálculo funciona en la API con datos reales (`POST /api/v1/search`, D-214 y D-215);
- producción lo tiene encendido desde el 11 nov (`NEXT_PUBLIC_FEATURE_SEARCH=true`). Lo verificó C con smoke 7/7, axe AA sin fallos y la consola limpia (`evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11).


<!-- resumen:inicio -->
Vida Fácil convierte los datos abiertos de la Comunidad de Madrid en un mapa de lo que falta. A cada persona le recomienda dónde vivir según su alquiler, hogar y trabajo, explica el porqué en lenguaje cotidiano y, si nada encaja, enseña cuántas zonas aparecen al relajar cada condición. A ayuntamientos y empresas les muestra, por municipio y por distrito de Madrid, qué falta, qué está justo y qué está cubierto: escuelas infantiles, colegios, salud, mayores, farmacias y vivienda. Usa 26 datasets del portal regional y cada resultado cita su fuente y su fiabilidad. Código abierto con API.
<!-- resumen:fin -->

Recuento:
```bash
awk '/^<!-- resumen:fin/{f=0} f; /^<!-- resumen:inicio/{f=1}' pitch/formulario.md | wc -w   # 98
```

## Campo 7 · Variante B (94 palabras) · de reserva
Esta versión no promete el buscador como hecho: lo presenta como lo que estamos construyendo. Solo vale si el 18 nov la demo vuelve a enseñar «Muy pronto». «Frente a municipios parecidos» es el método de D-213, refinado por D-217: cada zona se compara con los demás municipios de su tipo, urbanos o rurales, y un pueblo muy pequeño, junto con sus vecinos parecidos (`pitch/metodologia.md` §1.4).

<!-- variante-b:inicio -->
Vida Fácil convierte los datos abiertos de la Comunidad de Madrid en un mapa de lo que falta. A ayuntamientos y empresas les muestra, por municipio y por distrito de Madrid, qué falta, qué está justo y qué está cubierto frente a municipios parecidos: escuelas infantiles, colegios, salud, mayores, farmacias y vivienda. Para las personas construimos un buscador que recomienda dónde vivir según su alquiler, su hogar y su trabajo, con alternativas cuando nada encaja. Usa 26 datasets del portal regional y cada resultado cita su fuente y su fiabilidad. Código abierto con API.
<!-- variante-b:fin -->

```bash
awk '/^<!-- variante-b:fin/{f=0} f; /^<!-- variante-b:inicio/{f=1}' pitch/formulario.md | wc -w   # 94
```

### Cuándo usar cada versión
- **Resumen principal:** si el 18 nov se siguen cumpliendo las dos condiciones. Las dos se cumplen (comprobado el 11 y el 12 nov):
  - `POST /api/v1/search` devuelve zonas y alternativas con datos reales para el caso de ejemplo. En producción, caso de la Castellana: 33 de 199 zonas, Fuencarral-El Pardo 1.ª al 100 % (`fit-0.3`, con el trabajo en minutos de transporte público) y «+5 min a pie hasta colegio con primaria: saldrían 50 zonas, 17 más» (12 nov, tras el despliegue de `28a0f2f`; el 11 nov, 32 y 49 en `evidence/gate-06/2026-11-11-deploy/prod-buscador-check.json`, PR #11);
  - la demo desplegada tiene el buscador encendido y ya no enseña «Muy pronto».
- **Variante B:** solo si el 18 nov la demo vuelve a enseñar «Muy pronto», por ejemplo porque C haya vuelto a una versión sin buscador. Ahí la lista de lo que falta es el diferenciador (D-194), así que va primero, y el buscador sale como algo que «construimos», no como hecho.
- **Si una fila de la lista no llega** (por ejemplo, vivienda), quítala del texto y vuelve a contar las palabras.
- **Si cambia el número de datasets**, usa el de `pitch/datasets_cm.md` regenerado (ver checklist).

## Campo 8 · Enlaces (copiar)

```text
Demo: https://vidafacil-madrid.vercel.app
Código abierto (Apache-2.0): https://github.com/marianohernando/housing-intelligence
Datasets que integra, con licencia y control de calidad: https://github.com/marianohernando/housing-intelligence/blob/claude/sprint-1-public/pitch/datasets_cm.md
```

- **URL de la demo: verificada el 11 nov con el buscador encendido.** Smoke 7/7 con datos reales de Supabase (`evidence/gate-06/2026-11-11-deploy/deploy-12-buscador.md`, PR #11). El 18 nov se abre una vez más en el móvil antes de enviar (checklist, paso 5).
- **Enlace a `datasets_cm.md`:** funciona en cuanto A fusione este PR en `claude/sprint-1-public`. Si para el 18 nov Mariano ha fusionado en `main`, cambia `claude/sprint-1-public` por `main` en la URL.
- **Repo:** público desde el 11 nov (D-198); comprobado con `gh repo view` → `"visibility":"PUBLIC"`.

## Cada afirmación del resumen y su evidencia

| Afirmación | Evidencia hoy (11 nov) | Estado |
|---|---|---|
| Datos abiertos de la Comunidad de Madrid · «Usa 26 datasets del portal regional» | `pitch/datasets_cm.md` (generado desde `data/catalog/`, regenerado el 12 nov: 26 con Gate 1 en PASS) · `evidence/gate-01/2026-11-10/real-run-quality.txt` (los 21 del 10 nov) · `evidence/gate-01/2026-11-12/cm_dotacion_camas/` y `cm_hospitales_datos_asistenciales/` (2 del 12 nov, D-217 §4) · `evidence/gate-01/2026-11-12/crtm_topologia_*/` (las 3 topologías del CRTM, 12 nov, D-223) · en producción, `GET /api/v1/datasets?cm_only=true` da `cm_open_data_count: 26` y la web lo enseña en «Cómo lo calculamos» y en el pie (12 nov) | Hecho: los 26 están ingeridos y validados. 24 alimentan la lista o el buscador; el alquiler por código postal se ve en la tarjeta de cada distrito de Madrid (Ciudad Lineal: «Alquiler medio ≈ 1.070 €/mes por 77 m²», producción, 12 nov). Los 2 de camas solo dan el total de la región (20.776 camas instaladas en 2023): su uso en pantalla está **pendiente de A** (`grep -c 'pendiente de A' pitch/datasets_cm.md` da 4: esos 2 y 2 fuentes del catálogo aún sin ingerir). Las 3 topologías alimentan «sin escaleras», en producción desde el 12 nov. Si el 18 nov siguen así, «usa 26» sigue siendo cierto, pero si preguntan se dice qué se ve en pantalla |
| «Un mapa de lo que falta» · «qué falta, qué está justo y qué está cubierto» | `GET /api/v1/gaps/{level}/{code}` y `GET /api/v1/gaps?level=&row=` (el mapa, GAP-001 F4) · `data/fixtures/contracts/zone_gap_list.madrid.fixture.json` (`gap-0.3`) · recuento por estado: `evidence/gate-04/2026-11-12/gap-status-gap03.md` | Hecho, con las 6 filas en los 179 municipios y los 21 distritos. Desde el 12 nov, las 5 de servicios miden lo que se tiene a 15 min andando, repartido entre quienes lo comparten (D-217, `gap-0.3`, en producción) |
| «frente a municipios parecidos» (solo variante B) | D-213: referencia = los demás municipios del mismo tipo, rural o urbano · D-217: un pueblo demasiado pequeño se compara junto con sus vecinos del mismo tipo a 15 km o menos (`comparison_group`) · `evidence/gate-04/2026-11-12/phase-t2-review-gate.txt` · en producción, `GET /api/v1/gaps/distrito/2807913` da `gap-0.3` (comprobado el 12 nov) | Hecho en la API y en producción (GAP-001 F5; DATA-AUDIT T2, D-217) |
| «escuelas infantiles, colegios, salud, mayores, farmacias y vivienda» | `gap_row` de los 6 YAML en `data/catalog/features/` · `evidence/gate-04/2026-11-11/phase-gap001-f2.txt`, `-f3a.txt` y `-f3b.txt` · en la demo pública, `GET /api/v1/gaps/distrito/2807905` devuelve las 6 filas (comprobado el 11 nov) | Hecho (GAP-001 F2–F3b). La vivienda sale SIN DATOS en los distritos de Madrid: la CM no la publica a ese nivel |
| «por distrito de Madrid» | D-200 · D-209 (población por distrito del padrón del Ayuntamiento) · DATA-012 hecha (`be40c2f`, `board/BOARD.md`) · ejemplo real: Chamartín, `GET /api/v1/gaps/distrito/2807905` (comprobado en la demo pública el 11 nov) · `evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md`, «Manual check: Chamartín» | Hecho para las 6 filas (vivienda: SIN DATOS por distrito) |
| «recomienda dónde vivir según su alquiler, hogar y trabajo» | `POST /api/v1/search` (CORE-003, `915be3c`; CORE-006, `92eab6b`) · D-214 (alquiler × m² del hogar) · D-215 (condiciones y % de encaje) · `evidence/gate-04/2026-11-11/phase-core003-f2.txt` (6 escenarios dorados en datos reales) | Hecho en la API y en producción (PUB-001 F4, PR #10; encendido en el PR #11). El trabajo cuenta en minutos de transporte público llegando a las 9:00 (CORE-009, D-220, `fit-0.2`): hecho en la API y en producción desde el 12 nov (despliegue de `28a0f2f`, `evidence/gate-06/2026-11-12-deploy/deploy-17-pub001.md`). **Solo en el resumen principal** |
| «si nada encaja, enseña cuántas zonas aparecen al relajar cada condición» (Reality Check) | D-215 (punto 8) · en producción, «¿Y si cambias algo?» del caso de la Castellana: «+5 min a pie hasta colegio con primaria: saldrían 50 zonas, 17 más» (`POST /api/v1/search` con el fixture, 12 nov; el 11 nov eran 49, `prod-buscador-check.json`, PR #11). Subir el presupuesto ya no suma zonas y la web no enseña esa opción | Hecho en la API y en producción. El bloque sale siempre, plegado a la opción que más zonas suma, y se despliega solo cuando salen pocas zonas o ninguna. **Solo en el resumen principal** |
| «explica el porqué en lenguaje cotidiano» | Campo `explanation` de la lista. Ejemplo real: «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)» (Puente de Vallecas, `GET /api/v1/gaps/distrito/2807913`, `gap-0.3`, producción, 12 nov) | Hecho en la lista y en la API del buscador (`facts`, D-215: «Colegio con primaria a 5 min andando») |
| «cada resultado cita su fuente y su fiabilidad» | Cada fila de la lista lleva `datasets` (nombre, portal, versión, licencia) y `confidence` (`zone_gap_list.madrid.fixture.json` y la misma respuesta de Puente de Vallecas) | Hecho en la lista y en la API del buscador (`datasets` y `confidence` por zona y por hecho, D-215) |
| «Código abierto con API» | `LICENSE` (Apache-2.0, D-191) · repo público (D-198) · rutas en `docs/04_technical_architecture/31_public_api_routes.md` | Hecho |
| Demo con enlace público | https://vidafacil-madrid.vercel.app (URL elegida por Mariano) · `infra/deploy/README.md` · `evidence/gate-06/2026-11-11-deploy/deploy-9-web-nueva.md` (web nueva) · `deploy-12-buscador.md` (buscador, PR #11) · gap-0.3 en producción: despliegue `28e53fa`, smoke 8/8 con `/search` (PR #15 de C, abierto: `deploy-13-auditoria-gap03.md`) y `GET /api/v1/gaps/distrito/2807913` con `method.version: gap-0.3` (12 nov) | Hecho: la web nueva con el buscador, smoke 7/7 con datos reales (11 nov); gap-0.3 desplegado el 12 nov. Coste 0 €/mes. El 18 nov se vuelve a abrir antes de enviar |

El resumen no promete los extras: zonas verdes, «sin escaleras», precio de compra ni MCP (D-206). Las zonas verdes y «sin escaleras» ya están en la API (D-222, D-223), pero el 18 nov puede que la web aún no los enseñe y no caben en 100 palabras. La seguridad no puntúa (D-224) y no se menciona.

## Checklist del 18 nov (antes de enviar)
1. En `hi-coord`, hacer `git fetch origin && git rebase origin/claude/sprint-1-public`.
2. Ejecutar `uv run python pitch/build_datasets_cm.py --refresh-portal` y revisar el diff de `pitch/datasets_cm.md`:
   - el total de datasets CM con Gate en PASS es el número que va en el resumen;
   - si alguno de esos datasets sigue con «pendiente de A», no alimenta nada en la lista ni en el buscador. Se cuenta igual si la web lo lista en «Cómo lo calculamos» (hoy, los 2 de camas del 12 nov, como total de la región); si no, se cuenta solo lo que alimenta la demo.
3. Recorrer la tabla de evidencias: cada «pendiente de A/B/C» pasa a «hecho» con su ruta o su commit, o se quita del resumen lo que no llegó.
4. Comprobar que la demo sigue con el buscador (sin «Muy pronto») y copiar el resumen principal; si no, la variante B. Volver a contar las palabras con el comando de arriba: tienen que ser ≤ 100.
5. Abrir la URL de la demo en el móvil y en un navegador sin sesión: carga, se ve el caso precargado y la consola no da errores.
6. Pegar la URL de la demo en el campo 8 y comprobar que los 3 enlaces abren.
7. Enviar el formulario (lo hace Mariano) y avisar a A para que anote en el board «Formulario enviado».
