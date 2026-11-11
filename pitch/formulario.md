# Formulario de preselección DATAMAD 2026 — listo para copiar

- **Formulario:** https://forms.gle/NyatKHN95aPxvQro8 («DATAMAD 2026 | Presentación de propuestas»). Plazo: antes del 20 nov; objetivo 18 nov y límite real 19 (`docs/09_datamad/25_plan_competicion.md` §5, D-193).
- **Quién lo envía:** Mariano. Este fichero no guarda datos personales porque el repo es público.
- **Campos:** son los del formulario real, leídos el 11 nov.

> Las decisiones del 11 nov están registradas como D-199 a D-207 (`docs/00_index/01_decisions_log.md`). El brief de diseño (`~/Desktop/DATAMAD/prompts/DISENO_VIDA_FACIL.md`, adoptado por D-201) sigue fuera del repo: se cita como documento interno, no como evidencia pública.

## Campos, en orden

| # | Campo del formulario | Obligatorio | Qué poner |
|---|---|---|---|
| 1 | ¿Cómo vas a participar? | Sí | Marca: `Individualmente` (Mariano se presenta solo) |
| 2 | Nombre y apellidos | Sí | Tu nombre completo, listo para copiar en `pitch/formulario.local.md`. Ese fichero es local y git lo ignora: el nombre completo no se guarda en el repo público |
| 3 | Correo electrónico de contacto | Sí | **Lo rellenas tú:** el mismo email del formulario de inscripción inicial |
| 4 | Teléfono de contacto | Sí | **Lo rellenas tú** |
| 5 | Si participáis en equipo, indica los datos del resto de integrantes | Sí | Copia esto: `No aplica: participo individualmente.` |
| 6 | Nombre del proyecto | Sí | Copia esto: `Vida Fácil — Encuentra tu sitio en Madrid` |
| 7 | Describe brevemente vuestra propuesta (máximo 100 palabras) | Sí | Copia la **variante B** mientras el buscador salga como «Muy pronto» en la demo. El **resumen principal**, solo si el buscador ya funciona (ver «Cuándo usar cada versión») |
| 8 | ¿Quieres compartir algún material adicional? | No | Copia el bloque de **enlaces** de abajo |
| 9 | Compromiso de asistencia presencial (26 nov) | Sí | **Lo marcas tú** |
| 10 | Confirmación de inscripción previa | Sí | **Lo marcas tú** |

La ayuda del campo 7 pide «qué queréis construir, qué problema aborda y cómo usaréis los datos abiertos». Los dos textos cubren las tres cosas.

## Campo 7 · Resumen principal (98 palabras)
**Solo si el buscador funciona en la demo desplegada.** Este texto lo da por hecho («le recomienda dónde vivir», «enseña cuántas zonas aparecen»). Hoy (11 nov) no lo está: la web lo enseña como «Muy pronto» (`apps/web/src/lib/capabilities.ts`, `SEARCH_ENABLED`) hasta que exista `POST /api/v1/search` (CORE-003, **pendiente de A**). Mientras siga así, va la variante B.


<!-- resumen:inicio -->
Vida Fácil convierte los datos abiertos de la Comunidad de Madrid en un mapa de lo que falta. A cada persona le recomienda dónde vivir según su alquiler, hogar y trabajo, explica el porqué en lenguaje cotidiano y, si nada encaja, enseña cuántas zonas aparecen al relajar cada condición. A ayuntamientos y empresas les muestra, por municipio y por distrito de Madrid, qué falta, qué está justo y qué está cubierto: escuelas infantiles, colegios, salud, mayores, farmacias y vivienda. Integra 21 datasets del portal regional y cada resultado cita su fuente y su fiabilidad. Código abierto con API.
<!-- resumen:fin -->

Recuento:
```bash
awk '/^<!-- resumen:fin/{f=0} f; /^<!-- resumen:inicio/{f=1}' pitch/formulario.md | wc -w   # 98
```

## Campo 7 · Variante B (94 palabras) · la que vale hoy
Esta versión no promete el buscador como hecho: lo presenta como lo que estamos construyendo. «Frente a municipios parecidos» es el método de D-213: cada zona se compara con los demás municipios de su tipo, urbanos o rurales (`pitch/metodologia.md` §1.4).

<!-- variante-b:inicio -->
Vida Fácil convierte los datos abiertos de la Comunidad de Madrid en un mapa de lo que falta. A ayuntamientos y empresas les muestra, por municipio y por distrito de Madrid, qué falta, qué está justo y qué está cubierto frente a municipios parecidos: escuelas infantiles, colegios, salud, mayores, farmacias y vivienda. Para las personas construimos un buscador que recomienda dónde vivir según su alquiler, su hogar y su trabajo, con alternativas cuando nada encaja. Integra 21 datasets del portal regional y cada resultado cita su fuente y su fiabilidad. Código abierto con API.
<!-- variante-b:fin -->

```bash
awk '/^<!-- variante-b:fin/{f=0} f; /^<!-- variante-b:inicio/{f=1}' pitch/formulario.md | wc -w   # 94
```

### Cuándo usar cada versión
- **Resumen principal:** solo si el 18 nov se cumplen las dos condiciones:
  - `POST /api/v1/search` devuelve zonas y Reality Check con datos reales para el perfil dorado;
  - la demo desplegada tiene el buscador encendido (`NEXT_PUBLIC_FEATURE_SEARCH=true`) y ya no enseña «Muy pronto».
- **Variante B:** en cualquier otro caso. Es la que vale hoy. La lista de lo que falta es el diferenciador (D-194), así que va primero, y el buscador sale como algo que «construimos», no como hecho.
- **Si una fila de la lista no llega** (por ejemplo, vivienda), quítala del texto y vuelve a contar las palabras.
- **Si cambia el número de datasets**, usa el de `pitch/datasets_cm.md` regenerado (ver checklist).

## Campo 8 · Enlaces (copiar)

```text
Demo: https://vidafacil-madrid.vercel.app
Código abierto (Apache-2.0): https://github.com/marianohernando/housing-intelligence
Datasets que integra, con licencia y control de calidad: https://github.com/marianohernando/housing-intelligence/blob/claude/sprint-1-public/pitch/datasets_cm.md
```

- **URL de la demo: verificada el 11 nov.** Smoke 6/6, repetido 3 veces, con datos reales de Supabase (`evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md` (rama `claude/s1-deploy`, PR #6)). El 18 nov se abre una vez más en el móvil antes de enviar (checklist, paso 5).
- **Enlace a `datasets_cm.md`:** funciona en cuanto A fusione este PR en `claude/sprint-1-public`. Si para el 18 nov Mariano ha fusionado en `main`, cambia `claude/sprint-1-public` por `main` en la URL.
- **Repo:** público desde el 11 nov (D-198); comprobado con `gh repo view` → `"visibility":"PUBLIC"`.

## Cada afirmación del resumen y su evidencia

| Afirmación | Evidencia hoy (11 nov) | Estado |
|---|---|---|
| Datos abiertos de la Comunidad de Madrid · «Integra 21 datasets del portal regional» | `pitch/datasets_cm.md` (generado desde `data/catalog/`) · `evidence/gate-01/2026-11-10/real-run-quality.txt` (21 PASS) · `evidence/gate-01/2026-11-10/summary.md` | Hecho: los 21 están ingeridos y validados, y 20 ya alimentan la lista o los minutos a pie (GAP-001 F3b, `board/BOARD.md`). Solo falta el alquiler por código postal, que llega con el buscador (CORE-006, **pendiente de A**): es el único que en `datasets_cm.md` lleva «**pendiente de A**». Por eso dice «integra» y no «usa». Si el 18 nov los 21 alimentan la demo, se puede volver a «usa» (ver checklist) |
| «Un mapa de lo que falta» · «qué falta, qué está justo y qué está cubierto» | `GET /api/v1/gaps/{level}/{code}` y `GET /api/v1/gaps?level=&row=` (el mapa, GAP-001 F4) · `data/fixtures/contracts/zone_gap_list.madrid.fixture.json` | Hecho, con las 6 filas en los 179 municipios y los 21 distritos |
| «frente a municipios parecidos» (solo variante B) | D-213 (`gap-0.2`): referencia = los demás municipios del mismo tipo, rural o urbano · `evidence/gate-04/2026-11-11/phase-gap001-f5-review.txt` | Hecho en la API (GAP-001 F5, `d02574f`, `f626e1f`). La demo pública lo enseña cuando C despliegue: hoy aún da `gap-0.1` (**pendiente de C**) |
| «escuelas infantiles, colegios, salud, mayores, farmacias y vivienda» | `gap_row` de los 6 YAML en `data/catalog/features/` · `evidence/gate-04/2026-11-11/phase-gap001-f2.txt`, `-f3a.txt` y `-f3b.txt` · en la demo pública, `GET /api/v1/gaps/distrito/2807905` devuelve las 6 filas (comprobado el 11 nov) | Hecho (GAP-001 F2–F3b). La vivienda sale SIN DATOS en los distritos de Madrid: la CM no la publica a ese nivel |
| «por distrito de Madrid» | D-200 · D-209 (población por distrito del padrón del Ayuntamiento) · DATA-012 hecha (`be40c2f`, `board/BOARD.md`) · ejemplo real: Chamartín, `GET /api/v1/gaps/distrito/2807905` (comprobado en la demo pública el 11 nov) · `evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md` (rama `claude/s1-deploy`, PR #6), «Manual check: Chamartín» | Hecho para las 6 filas (vivienda: SIN DATOS por distrito) |
| «recomienda dónde vivir según su alquiler, hogar y trabajo» | Contrato `ScenarioState` (`packages/contracts/src/hi_contracts/public/scenario.py`, commit `7541527`): presupuesto, hogar y lugar de trabajo | Contrato hecho. Cálculo **pendiente de A** (CORE-006, CORE-003 y `POST /api/v1/search`, 15–16 nov). La pantalla de B existe, pero apagada: sale «Muy pronto» hasta que haya `/search` (`apps/web/src/lib/capabilities.ts`). **Solo en el resumen principal** |
| «si nada encaja, enseña cuántas zonas aparecen al relajar cada condición» (Reality Check) | Contrato `SearchResult` (`packages/contracts/src/hi_contracts/public/search.py`, `7541527`) | Contrato hecho. Cálculo **pendiente de A** (CORE-003). **Solo en el resumen principal** |
| «explica el porqué en lenguaje cotidiano» | Campo `explanation` de la lista. Ejemplo real: «0,37 centros de atención primaria por cada 10.000 habitantes; en los demás municipios urbanos de la Comunidad de Madrid, 0,56 (en toda la Comunidad, 0,59)» (`data/fixtures/contracts/zone_gap_list.madrid.fixture.json`, `gap-0.2`) | Hecho en la lista; en el buscador, **pendiente de A** |
| «cada resultado cita su fuente y su fiabilidad» | Cada fila de la lista lleva `datasets` (nombre, portal, versión, licencia) y `confidence` (mismo fixture) | Hecho en la lista; en el buscador, **pendiente de A** |
| «Código abierto con API» | `LICENSE` (Apache-2.0, D-191) · repo público (D-198) · rutas en `docs/04_technical_architecture/31_public_api_routes.md` | Hecho |
| Demo con enlace público | https://vidafacil-madrid.vercel.app (URL elegida por Mariano) · `infra/deploy/README.md` · `evidence/gate-06/2026-11-11-deploy/deploy-4-supabase-smoke.md` (rama `claude/s1-deploy`, PR #6) | Hecho: smoke 6/6 repetido 3 veces con datos reales (11 nov). Coste 0 €/mes. La web nueva (MAP-004 y PUB-001, fusionada en `bd5b006`) la está desplegando C (**pendiente de C**); el 18 nov se comprueba que la URL ya la enseña |

No se prometen los extras del 19 al 22 nov: zonas verdes, seguridad, «sin escaleras», precio de compra ni MCP (D-206).

## Checklist del 18 nov (antes de enviar)
1. En `hi-coord`, hacer `git fetch origin && git rebase origin/claude/sprint-1-public`.
2. Ejecutar `uv run python pitch/build_datasets_cm.py --refresh-portal` y revisar el diff de `pitch/datasets_cm.md`:
   - el total de datasets CM con Gate en PASS es el número que va en el resumen;
   - si alguno de esos datasets sigue con «pendiente de A», no alimenta nada visible: o A lo conecta o se cuenta solo lo que alimenta la demo.
3. Recorrer la tabla de evidencias: cada «pendiente de A/B/C» pasa a «hecho» con su ruta o su commit, o se quita del resumen lo que no llegó.
4. Elegir la versión del resumen (principal o B) y volver a contar las palabras con el comando de arriba. Tienen que ser ≤ 100.
5. Abrir la URL de la demo en el móvil y en un navegador sin sesión: carga, se ve el caso precargado y la consola no da errores.
6. Pegar la URL de la demo en el campo 8 y comprobar que los 3 enlaces abren.
7. Enviar el formulario (lo hace Mariano) y avisar a A para que anote en el board «Formulario enviado».
