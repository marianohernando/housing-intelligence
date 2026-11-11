# DATAMAD-PUBLIC-01 — repo público con historial limpio (2026-11-11)

## Por qué
Los fixtures de equipamientos (`data/fixtures/golden/places_sample/`) se crearon en el commit del 22 oct `5eb4bf7` (ahora `e8c8fc5`) con columnas copiadas tal cual de los registros del portal CM: teléfonos, emails de contacto (algunos personales), NIF y titulares (uno es una persona física). La licencia CC BY cubre los derechos de autor, no la protección de datos (bases §6.6 y §16). Reescribir el historial de un repo que ya existe no basta: GitHub conserva los commits originales en las refs de los PR #2 y #3 ya mergeados. Por eso Mariano decidió hacerlo así:

1. El repo original pasa a llamarse `marianohernando/housing-intelligence-archive`, **privado y archivado**. Conserva los SHAs, los PR y los CI de octubre como prueba de fechas del trabajo previo.
2. Se reescribe una copia con `git-filter-repo 2.47.0` (`--blob-callback`), que solo sustituye los 3 blobs antiguos por su versión redactada de `a2f8dea`:
   - `cm_centros_atencion_social.csv`: `7eb5443` → `6b39053`
   - `cm_centros_educativos.csv`: `49ef33c` → `2abc38e`
   - `cm_centros_sanitarios.csv`: `93054ca` → `e55bfda`
3. Se crea `marianohernando/housing-intelligence` (misma URL), se suben las 5 ramas y el tag, y se hace público cuando pasan las comprobaciones.

## Comprobaciones
| Comprobación | Resultado |
|---|---|
| Commits por rama, antes → después | main 29→29 · sprint-1-public 43→43 · sprint-p1-cm-data 27→27 · open-poi-sources 18→18 · sprint-p0 16→16 |
| Fechas y autor de autor y committer | Idénticos en todas las ramas |
| Contenido de la punta, antes y después | `main` y `sprint-p1-cm-data`: solo difieren los 3 fixtures. `sprint-1-public`, `open-poi-sources` y `sprint-p0`: idénticos |
| Tag `pre-datamad` | Mismo tagger (2026-11-10) y mismo commit con fecha 2026-10-22 12:18 +0200, ahora `cf39459` (antes `08cc526`) |
| Emails en cualquier versión de cualquier fichero (clon nuevo, 43 commits) | Solo `madrid.datamad@urjc.es` (el contacto público del concurso) |
| gitleaks sobre todo el historial (clon nuevo) | Sin hallazgos |
| CI en el repo nuevo | Ver `gh run list -R marianohernando/housing-intelligence` (rama `claude/sprint-1-public`, `103229b`) |

## Efectos colaterales
- 27 commits cambian de SHA. La tabla completa está en `commit-map.txt` (antiguo → nuevo) y las refs en `ref-map.txt`. La evidencia de gates anterior a hoy cita SHAs antiguos, que se traducen con esa tabla.
- `git-filter-repo` quita las firmas GPG que GitHub puso en los merges hechos desde la web (p. ej. `ffbbb5f` → nuevo SHA en `main` y `open-poi-sources`). El contenido es el mismo y solo se pierde el distintivo «Verified».
- Los PR #1–#3 y los CI de octubre solo existen en el repo archivado.
