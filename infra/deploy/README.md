# Despliegue de la demo «Vida Fácil» (OPS-001)

Web (Next.js) y API (FastAPI) en **un solo proyecto de Vercel**, `vida-facil`, leyendo de Supabase (`ilvbivfnqvfqslbbiuts`, eu-west-1).

- URL pública: **https://vidafacil-madrid.vercel.app**, la elegida por Mariano el 11 nov. La web está en `/` y la API en `/api/v1/*`, en el mismo dominio, así que no hay CORS cruzado.
- Alias secundario: `https://vida-facil-eight.vercel.app`. Es el que asignó Vercel al crear el proyecto (otra cuenta ya usa `vida-facil.vercel.app`) y se mantiene para no romper los enlaces ya compartidos. `CORS_ORIGINS` acepta los dos.
- Si se cambia el dominio, hay que actualizar `NEXT_PUBLIC_API_URL`, `CORS_ORIGINS` y `DEMO_URL` en `deploy.sh` y en `smoke_demo.sh`, y volver a desplegar.
- Región de cómputo: `dub1` (Dublín), junto a la base de datos.
- Equipo de Vercel: el de la cuenta del CLI de Mariano. Su slug lleva su apellido, así que no se escribe en el repo (LINEAS.md); `deploy.sh` lo enmascara en su salida.
- Por qué Vercel y no Render ni Cloud Run: [evidence/gate-06/2026-11-11-deploy/provider-research.md](../../evidence/gate-06/2026-11-11-deploy/provider-research.md).

## Piezas

| Fichero | Para qué |
|---|---|
| [`vercel.json`](../../vercel.json) | Dos servicios (Vercel Services, beta): `web` sale de `apps/web` (Next.js) y `api` es un contenedor construido con `infra/deploy/api/Dockerfile`. También fija la región y las reglas de enrutado. |
| [`.vercelignore`](../../.vercelignore) | Lista de lo que se sube. Solo sale el código: nunca `.env*`, `*.pem`, `*.key`, `*.db`, `*.sqlite`, `node_modules`, `data/` ni `docs/`. |
| [`api/Dockerfile`](api/Dockerfile) | Imagen de la API con solo las dependencias de `hi-api` (`uv sync --package hi-api`). Usuario no root y puerto `$PORT`. |
| [`deploy.sh`](deploy.sh) | `make deploy-demo`. Comprueba que el árbol está limpio y que la rama es la de la demo (`claude/sprint-1-public` o `main`; otra solo con `ALLOW_BRANCH=1`). Avisa de los ficheros sensibles locales que no se suben. Después despliega a producción, pasa el smoke y comprueba en `vercel logs` que todas sus peticiones las sirvió el despliegue nuevo. |
| [`offline/`](offline/) | Paquete offline para la final: `make demo-offline-tiles` (mapa base), `make demo-offline-prepare`, `make demo-offline` y `make demo-offline-stop`. Ver más abajo. |
| [`../../scripts/smoke_demo.sh`](../../scripts/smoke_demo.sh) | `make smoke-demo`: comprueba web, `health`, `ready`, una zona, la geografía, una capa (educación), la página 1 de la capa más grande (transporte) y una búsqueda (`POST /api/v1/search` con el caso demo del guion: al menos una zona y menos de 1 MB). También comprueba que ninguna respuesta pase de 4,5 MB. Se identifica con el User-Agent `vida-facil-smoke` (más `/<etiqueta>` si se define `SMOKE_TAG`). |
| [`sql/api_readonly_role.sql`](sql/api_readonly_role.sql) | Rol `vf_api_ro`: solo lectura, con una política RLS por cada tabla que lee la API. Es idempotente. |

## Variables de entorno (proyecto Vercel, entorno Production)

Aquí solo van los nombres, nunca los valores. Las variables que no son secretas las fija la línea C con el CLI. Los secretos los mete Mariano.

| Variable | Servicio | Tipo | Valor o forma |
|---|---|---|---|
| `DATABASE_URL` | api | **Secreto** (Sensitive). Lo mete Mariano | `postgresql+psycopg://vf_api_ro.ilvbivfnqvfqslbbiuts:<contraseña>@aws-0-eu-west-1.pooler.supabase.com:6543/postgres?sslmode=require`. Desde el 12 nov a las 13:14 es el Transaction pooler (puerto 6543), con una contraseña nueva para `vf_api_ro`; antes era el Session pooler (5432). La conexión directa es solo IPv6. El esquema tiene que ser `postgresql+psycopg://`. **Cambiar la contraseña deja inservibles los despliegues anteriores** (ver «Volver atrás») |
| `CORS_ORIGINS` | api | Config | `["https://vidafacil-madrid.vercel.app","https://vida-facil-eight.vercel.app"]`, una lista JSON |
| `PORT` | api | Config | `8080`. El contenedor escucha ahí y Vercel enruta a `$PORT` |
| `DB_POOL_SIZE` | api | Config | `1` desde el 12 nov a las 11:00 (antes `2`): conexiones fijas a la base por instancia. El código pone 5 por defecto (`packages/db`, `make_engine`, 4645326). El pooler de Supabase en modo sesión admite tantos clientes como su `pool_size`, compartidos por todas las instancias: 15 en el plan actual del proyecto. No es un límite fijo del pooler (incidente en `evidence/gate-06/2026-11-12-deploy/deploy-13-auditoria-gap03.md`) |
| `DB_MAX_OVERFLOW` | api | Config | `0` desde el 12 nov a las 11:00 (antes `1`): conexiones extra en un pico, que se cierran al devolverse. Por defecto, 10. **Por qué 1 + 0:** Vercel arranca casi una instancia por petición concurrente (unas 12 peticiones de una vista de zona levantaron 11 instancias), así que con 2 + 1 se pasaba de 15 (80 `EMAXCONNSESSION` en 10 min). Con 1 + 0, 10 instancias y 0 errores (`deploy-14-pool.md`). Ese límite de 15 es del modo sesión; con el puerto 6543 se mantiene 1 + 0 porque va bien: 0 errores en 10 min y la búsqueda en caliente en 0,3 s (`deploy-15-6543.md`). Subirlo no mejora la latencia |
| `DB_PREPARED_STATEMENTS` | api | Config | `false` desde el 12 nov: psycopg no prepara las consultas (`prepare_threshold=None`; por defecto `true`). Es el requisito del pooler en modo transacción (puerto 6543), y en el 5432 funciona igual. **Orden (D-219 §5), hecho el 12 nov:** primero esta variable y un redespliegue; después Mariano cambia el puerto de `DATABASE_URL` a 6543 y se vuelve a desplegar con smoke. Al revés, las consultas repetidas fallan con «prepared statement … already exists» o «does not exist». No la vuelvas a `true` mientras se use el 6543 |
| `NEXT_PUBLIC_API_URL` | web | Config | `https://vidafacil-madrid.vercel.app`. Se incrusta al compilar: si cambia, hay que volver a desplegar |
| `NEXT_PUBLIC_FEATURE_SEARCH` | web | Config | `true` desde el 11 nov: enciende el buscador. Se incrusta al compilar. Para apagarlo: `npx vercel@65.12.1 env rm NEXT_PUBLIC_FEATURE_SEARCH production` y volver a desplegar. Si el despliegue anterior se compiló sin ella, también vale un rollback |

Cómo mete Mariano el secreto. En la carpeta enlazada (la que tiene `.vercel/`):

```bash
npx vercel@65.12.1 env add DATABASE_URL --environment production --sensitive
# pega la URL cuando la pida; no queda en el historial de la terminal
```

También se puede meter desde el panel: Project `vida-facil` → Settings → Environment Variables → `DATABASE_URL`, marcando Production y Sensitive. Después hay que volver a desplegar: las variables nuevas solo se aplican en los despliegues que vienen detrás.

## Rol de solo lectura `vf_api_ro`

- **Cómo se crea:** con la migración `0005_api_readonly_role.py` (D-208), que aplica `make supabase-migrate`. [`sql/api_readonly_role.sql`](sql/api_readonly_role.sql) es el mismo rol como script para pegarlo a mano en el SQL Editor de Supabase. Los dos son idempotentes y un test exige que listen las mismas tablas. La contraseña se fija aparte, con `ALTER ROLE vf_api_ro PASSWORD '…'`, y solo va en `DATABASE_URL`. Por el pooler, el usuario es `vf_api_ro.ilvbivfnqvfqslbbiuts`.
- **Qué impide escribir:** los privilegios. Solo tiene `SELECT` en las 7 tablas de la lista y ningún `CREATE` en `public`. `default_transaction_read_only` es una segunda capa, pero el rol podría desactivarla en su sesión.
- **Requisito:** el SQL necesita el esquema `extensions`, donde viven PostGIS y pgvector. Existe en local y en Supabase.
- **Quitar una tabla de la lista no revoca nada.** Si se quita, hay que hacer `REVOKE SELECT` y `DROP POLICY vf_api_ro_read` sobre esa tabla.

### Riesgo: una tabla nueva sale vacía, sin dar error

Con RLS activo (D-197), una tabla que lee la API pero que no tiene `GRANT SELECT` ni política `vf_api_ro_read` se comporta así:
- **Sin `GRANT`:** la petición falla con `permission denied` y la API devuelve 500.
- **Con `GRANT` pero sin política:** la tabla **se ve vacía**. Es el peor caso, porque la API responde 200 con listas vacías o filas «SIN DATOS».

Cómo se detecta:
1. **Antes del merge:** `tests/unit/api/test_readonly_role.py` falla si el SQL de la API (`text(...)` en `apps/api`) consulta una tabla que ninguna migración concede al rol (`API_TABLES`). Para añadir una tabla hay que hacer una migración nueva con su `API_TABLES`, actualizar el script SQL y ejecutar `make supabase-migrate`.
2. **En producción:** `make smoke-demo`.
   - `ready` da 503 `INSUFFICIENT_DATA` si el rol no ve `geo_admin_unit`.
   - `zone` falla si la lista de la zona sale sin filas.
   - `geography` y `layer` fallan si no hay municipios o lugares.
   - Los datos que no cubre el smoke (por ejemplo, el buscador cuando exista) hay que comprobarlos con el rol: `SET ROLE vf_api_ro; SELECT count(*) FROM <tabla>;` en el SQL Editor tiene que dar el mismo número que como `postgres`.

## Volver a desplegar (17 nov)

1. **A** carga los datos en Supabase:

   ```bash
   make supabase-migrate
   make supabase-sync PROFILE=demo
   ```

2. Desde un checkout limpio de `claude/sprint-1-public`, o de `main` después del merge, ejecuta `make deploy-demo`. El checkout se enlaza una sola vez con `npx vercel@65.12.1 link --project vida-facil`.

   El comando:
   - despliega web y API en producción y anota el id del despliegue nuevo (`dpl_…`);
   - publica los dos dominios, `vidafacil-madrid` y `vida-facil-eight`;
   - pasa `scripts/smoke_demo.sh` con una etiqueta única en el User-Agent;
   - busca esas peticiones en `vercel logs requests` (tardan 10–20 s en aparecer) y comprueba que **todas** las sirvió el despliegue nuevo. Imprime cuántas vienen de cada despliegue;
   - si el smoke falla, o si alguna petición vino de otro despliegue, espera 20 s y repite smoke y comprobación, **hasta 3 veces**.

   **Por qué:** durante unos segundos después de cambiar el dominio, el despliegue anterior sigue atendiendo parte del tráfico. El 11 nov dio un 500, porque se había creado antes de existir `DATABASE_URL`. Más tarde ese día, dos veces seguidas, un smoke 7/7 recién desplegado tenía 3 o 4 de sus 7 peticiones servidas por el despliegue anterior. Un smoke en verde, por sí solo, no prueba el despliegue nuevo.

   **Cómo termina:**

   | Código | Qué significa | Qué hacer |
   |---|---|---|
   | 0 | Smoke en verde y todas sus peticiones del despliegue nuevo («verified: …») | Nada |
   | 1 | Falló el despliegue, o el smoke falló las 4 veces | Rollback (imprime el comando) |
   | 2 | No ha desplegado: árbol sucio, rama no permitida, falta `jq` o el enlace con Vercel | Corregir y repetir |
   | 3 | Ha desplegado pero no está verificado: el smoke pasa y alguna petición sigue viniendo de otro despliegue, o los logs no muestran todas | No presentar así. Revisar `npx vercel@65.12.1 logs requests --environment production --since 10m` y repetir `make smoke-demo` |

   El script solo imprime ids de despliegue y recuentos, nunca tokens ni variables.

   Desde otra rama solo se despliega a propósito, con `ALLOW_BRANCH=1 make deploy-demo`.

3. Guarda la salida en `evidence/gate-06/<fecha>-deploy/`, pasándola por `scripts/redact_paths.py`: `set -o pipefail; ALLOW_BRANCH=1 make deploy-demo 2>&1 | uv run python scripts/redact_paths.py > evidence/…`.
   - `deploy.sh` ya cambia por `<panel de Vercel>` y `<despliegue>` las URLs del CLI que llevan el slug del equipo.
   - Antes del commit, revisa que no quede ninguna ruta local ni ninguna URL con ese slug (LINEAS.md).

**Tiempo:** unos 2–3 minutos. La construcción de la imagen de la API y de la web lleva unos 85–110 s, y la comprobación en los logs unos 20 s por ronda. Lo normal es que la primera ronda aún pille el despliegue anterior y la segunda verifique: 157 s el 11 nov.

**Sin Git:** la integración con GitHub está desconectada a propósito. Los push de las líneas no despliegan nada; solo despliega `make deploy-demo`.

## Volver atrás

- **Instant Rollback en Hobby:** solo permite volver al despliegue de producción inmediatamente anterior ([docs](https://vercel.com/docs/instant-rollback)). Comando: `npx vercel@65.12.1 rollback`, o desde el panel: Production Deployment → Instant Rollback.
- **Después de un rollback:** Vercel desactiva la asignación automática del dominio. El siguiente despliegue no queda publicado hasta que lo promueves con `npx vercel@65.12.1 promote <url-del-despliegue>`.
- **Variables de entorno:** cada despliegue se queda con las que había al construirlo. Un rollback no corrige una variable: corrígela y vuelve a desplegar.
- **Ningún despliegue anterior a `dpl_AtNd6uYPahHmYPyHMp3SwRepcck8` (12 nov, 13:55) sirve para volver atrás.** Si hay que volver atrás, despliega desde Git la versión buena del código con `make deploy-demo`, que toma la contraseña y los datos actuales. Hay dos motivos:
  - **Los anteriores a `dpl_5efz…` (13:14) llevan la contraseña vieja de `vf_api_ro`,** que Mariano cambió con el paso al puerto 6543. Durante el cambio de dominio, uno de ellos respondió `/search` con 500 y «password authentication failed for user "vf_api_ro"» (`deploy-15-6543.md`).
  - **`dpl_5efz…` no entiende los datos actuales de Supabase.** El sync de la prioridad de zonas verdes (DATA-018) tumbó su `/search` con «ValueError: None is not a valid NeedKey» (`deploy-16-fit03.md`).
  - En general, un despliegue solo sirve para volver atrás si su código entiende los datos que hay en Supabase.
- **Orden al cambiar a la vez código y datos:** primero se despliega el código que entiende los datos nuevos, y después se sincroniza.
- **Si el fallo está en los datos y no en el código:** no se arregla con un rollback. A vuelve a ejecutar `make supabase-sync PROFILE=demo` con la versión buena de la base local.
- **Si el fallo es el límite de conexiones de la base, tampoco.** En los logs sale `EMAXCONNSESSION max clients reached in session mode`.
  - El pooler en modo sesión admite tantos clientes como su `pool_size`: 15 en el plan actual de Supabase. No es un límite fijo del pooler. Las instancias vivas del despliegue que falla siguen ocupándolos, y las del despliegue anterior no consiguen ninguno.
  - El 12 nov el rollback dejó el smoke en 2/8. Volver a promover el despliegue nuevo lo arregló en el acto (`deploy-13-auditoria-gap03.md`).
  - El arreglo de fondo era el pooler en modo transacción (puerto 6543), en uso desde el 12 nov a las 13:14. `EMAXCONNSESSION` solo puede volver si `DATABASE_URL` vuelve al 5432.

## Límites del plan gratuito (Hobby)

| Recurso | Límite | Riesgo para la demo |
|---|---|---|
| Uso | Solo personal y no comercial ([fair use](https://vercel.com/docs/limits/fair-use-guidelines)) | Una demo de concurso sin pagos ni anuncios encaja |
| Invocaciones | 1.000.000 al mes | Bajo |
| CPU activa | 4 h al mes, **compartidas con los otros proyectos del equipo** | Medio: vigilar en Usage |
| Memoria provisionada | 360 GB-h al mes | Bajo |
| Transferencia | 100 GB al mes (Fast Data Transfer) y 10 GB (Origin Transfer) | Bajo: la respuesta más grande es una página de `/places`, de unos 1,4 MB |
| Respuesta | 4,5 MB como máximo por respuesta no streaming ([límites](https://vercel.com/docs/functions/limitations)) | Bajo: `/places` va paginado desde 879101a, con 5.000 lugares por página (unos 1,4 MB). El smoke mide la página 1 de transporte (`largest`). Antes de paginar, la capa entera pesaba 4,2 MB, el 94 % del límite |
| Duración | 300 s por petición | Ninguno |
| Memoria por instancia | 2 GB, 1 vCPU | Ninguno |
| Región | Una sola (`dub1`) | — |
| Subida por CLI | 100 MB de código | `.vercelignore` deja unos 4 MB |
| Arranque en frío | El contenedor se apaga tras 5 min sin tráfico ([container runtime](https://vercel.com/docs/functions/runtimes/container)). La primera petición tarda unos 3–4 s; las siguientes, 0,1–0,25 s | Calentar la demo antes de presentar (ver «Día de la final») |
| Supabase free | La base pasa a solo lectura por encima de 500 MB (la demo ocupa 100 MB). Los proyectos inactivos se pausan | Abrir la demo durante la semana anterior |

## Vigilancia diaria

[`.github/workflows/smoke-demo.yml`](../../.github/workflows/smoke-demo.yml) ejecuta `scripts/smoke_demo.sh` contra la URL pública todos los días a las 07:30 (hora de Madrid). También se puede lanzar a mano:

- desde la pestaña Actions → smoke-demo → Run workflow, con `base_url` opcional;
- o con `gh workflow run smoke-demo.yml`.

Si falla, GitHub manda un email a la cuenta que cambió por última vez la línea `cron`.

**Solo se activa cuando el fichero está en `main`:** GitHub ejecuta los `schedule` y los `workflow_dispatch` desde la rama por defecto. Cubre del 17 al 26 nov si `claude/sprint-1-public` se fusiona en `main` antes del 17.

### Recorridos del pitch en un navegador (`make e2e-prod`)
[`e2e/e2e_prod.mjs`](e2e/e2e_prod.mjs) hace en un navegador real los recorridos del guion (`pitch/guion.md`):
1. **J1:** portada → «Ver un ejemplo» → la 1.ª zona → «¿Y si cambias algo?», aplicar y deshacer.
2. **J2:** «Qué falta» → «Madrid (toda la ciudad)».
3. **J3:** el mapa por fila («¿Qué quieres ver?»), las 6 filas.
4. **J4:** la lista de zonas.

**Qué comprueba:**
- Cada cifra de la pantalla, contra la respuesta de la API que recibió la propia página: zonas que encajan, leyenda, % y hechos de la tarjeta, opciones de «¿Y si cambias algo?», estado de cada fila y recuentos de la lista. No hay cifras fijas, así que sigue valiendo tras un sync.
- Que todas las peticiones a `/search` lleven `max_minutes: null`.
- Que no haya errores de consola ni desbordamiento horizontal.

**Cómo se ejecuta:**
- `make e2e-prod`: Chromium a 1440 y 390 px, unos 30 s. Sale con 0 solo si pasa todo.
- Más navegadores, tamaños y capturas: `make e2e-prod E2E_ARGS="--browsers chromium,webkit,firefox --devices desktop-1440,desktop-1920,mobile-390,projector-125 --shots --out <carpeta>"`. Los navegadores se instalan una vez con `npx playwright install chromium webkit firefox`.
- El workflow diario ejecuta además un job `e2e` con Chromium. El informe se guarda 14 días como artefacto `e2e-report`.

**Comprobaciones omitidas, no superadas:** en móvil, la leyenda oculta los recuentos a propósito, así que esas comprobaciones salen como `skipped`.

## Día de la final (26 nov): lista

1. **Por la mañana:**
   - `make smoke-demo` tiene que dar 8/8. Si falla, sigue la sección «Si la demo se cae».
   - Comprueba que el paquete offline arranca (`make demo-offline`, abrir `http://localhost:3012/map` y luego `make demo-offline-stop`).
   - Lleva las capturas y el vídeo del recorrido.
2. **En la hora previa a presentar, nunca `make supabase-sync`**, lo lance quien lo lance.
   - El sync vacía con `TRUNCATE` las 11 tablas del perfil demo y las vuelve a copiar una a una. Mientras dura, la demo enseña zonas SIN DATOS y capas vacías. El 11 nov se vio `feature_value` con 0 filas a mitad de un sync.
   - Si ese día hay que cargar datos, que sea por la mañana y seguido de `make smoke-demo` con 8/8.
   - Si en esa hora fallan los datos, no se arreglan con un sync: usa el paquete offline.
3. **En la sala:** conecta el portátil a la red y abre https://vidafacil-madrid.vercel.app/map. Si no hay red o Vercel no responde, usa `make demo-offline` y abre `http://localhost:3012/map`.
4. **Calentamiento, 2–3 minutos antes de presentar:** ejecuta `make smoke-demo`, que ya incluye `/search`.
   - Sus 8 peticiones pasan por la web y por cada ruta que usa la demo: health, ready, zona, geografía, dos capas y una búsqueda con el caso del guion.
   - Así el contenedor de la API ya está arrancado y la búsqueda tiene su caché lista, y no te comes delante del jurado los unos 6 s de un `/search` en frío (medido el 12 nov: 3,5 s de arranque más 2,5 s de la primera búsqueda).
   - Deja después la pestaña de la demo abierta y recárgala una vez.
   - El contenedor se apaga tras 5 min sin tráfico. Si entre el calentamiento y tu turno pasan más de 5 min, repítelo.
5. **Durante la presentación:** si una petición se queda colgada más de 10 s, cambia al paquete offline (`make demo-offline`, unos 7 s) en vez de esperar.

## Si la demo se cae

1. **Diagnóstico (1 minuto):** `make smoke-demo`.
   - `health` falla: la caída es de la plataforma o de la API.
   - `health` funciona pero `ready` falla con `SOURCE_DEGRADED`: la base de datos no responde (Supabase pausada o caída, o la credencial está mal).
   - `ready` falla con `INSUFFICIENT_DATA`: el rol no ve filas (falta una política o un `GRANT`) o los datos no están cargados.
   - `ready` falla y en `npx vercel@65.12.1 logs --environment production --since 15m` sale «password authentication failed»: la contraseña de `DATABASE_URL` no es la de `vf_api_ro`. Pasa si alguien hizo rollback a un despliegue anterior al 12 nov a las 13:14 (ver «Volver atrás»), o si la contraseña cambió en Supabase y no en Vercel. Mariano la corrige en Vercel y se vuelve a desplegar.
   - Hay 500 sueltos, sobre todo en la vista de zona, y en esos logs sale `EMAXCONNSESSION`: está lleno el pooler de Supabase en modo sesión, así que `DATABASE_URL` ha vuelto al puerto 5432. No hagas rollback (ver «Volver atrás»). Espera a que bajen las instancias: unos 5 min sin tráfico, una estimación hecha con el apagado por inactividad del container runtime, no una garantía. O reduce las conexiones por instancia (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`); eso exige redesplegar, porque las variables solo se aplican en los despliegues nuevos.
2. **Si el fallo vino con el último despliegue:** Instant Rollback (ver arriba), salvo que el anterior sea anterior a `dpl_AtNd6uYPahHmYPyHMp3SwRepcck8`. En ese caso, vuelve a desplegar la versión buena del código con `make deploy-demo`.
3. **Si Supabase está pausada:** reanúdala desde el panel de Supabase con la cuenta dedicada a DATAMAD y vuelve a pasar el smoke.
4. **Sin Internet o con Vercel caído durante la presentación:** `make demo-offline`, el paquete offline de la sección siguiente. Arranca en unos 7 s en el portátil, con los mismos datos. Lleva también capturas y un vídeo corto del recorrido, grabados con la versión desplegada.
5. **Si Vercel cae varios días:** el mismo `infra/deploy/api/Dockerfile` sirve en Render o en Cloud Run. Las opciones B y C están en `provider-research.md` y necesitan cuenta.

## Paquete offline para la final (26 nov)

Es la demo completa en el portátil, sin Internet: la API (la misma imagen que en Vercel) y la web, con un volcado del perfil demo. Corre en una base aislada:
- proyecto de compose `vida-facil-offline`, con su propio volumen;
- Postgres en `127.0.0.1:5441`, API en `:8012` y web en `:3012`.

Qué no toca nunca:
- **La base de desarrollo** (`housing`, puerto 5440) ni sus puertos 8010 y 3010. A esa base solo la lee para hacer el volcado.
- **El proyecto de compose de desarrollo.** El script fija `-p vida-facil-offline`, así que un `COMPOSE_PROJECT_NAME` del entorno, por ejemplo exportado desde `.env` por `make`, no puede hacer que sus comandos actúen sobre `housing-intelligence`.
- **`apps/web/.next`.** La web se compila en una copia privada (`data/offline/web-build`). Así no pisa el `next dev` de A o de B, y no hereda ninguna `NEXT_PUBLIC_*` del entorno ni de un `.env`.

### Mapa base sin red (`make demo-offline-tiles`, una vez, con Internet)

Genera las teselas del mapa base de la Comunidad de Madrid para que, sin red, el mapa salga con calles, parques y edificios en 3D. Va antes de `make demo-offline-prepare`, que compila la web apuntando a ellas. Tarda alrededor de 1 minuto.
1. **Descarga el extracto de OpenStreetMap de Geofabrik** (licencia ODbL) a `data/offline/tiles-src/`.
   - **Extracto fijado:** `madrid-261111.osm.pbf`, con datos del 11 nov y 86 MB. El nombre y el md5 están fijados en `demo_offline.sh` (`PBF_PINNED`, `PBF_PINNED_MD5`).
   - **Por qué el md5 va en el script:** al no tomarlo del mismo servidor que el fichero, detecta un fichero manipulado, no solo uno corrupto. Si ya está descargado y la suma cuadra, no lo vuelve a bajar.
   - **Otro extracto:** `PBF_FILE=madrid-AAMMDD.osm.pbf PBF_MD5=<md5> make demo-offline-tiles`, y después fija los dos en el script. Si Geofabrik deja de tener el fijado, el script lo dice.
   - **Requisito:** `jq`, para adaptar la configuración de tilemaker. El script avisa si falta.
2. **Genera las teselas con tilemaker 3.2.0:**
   - Usa la imagen oficial del repositorio (`ghcr.io/systemed/tilemaker`), fijada por digest en `demo_offline.sh` y sin red dentro del contenedor.
   - El esquema es OpenMapTiles, el mismo que el estilo de la web. De la configuración de tilemaker se quitan las capas que salen de shapefiles (mar, glaciares, zonas urbanas de Natural Earth), porque Madrid no tiene ninguna.
   - Salen de z0 a z14 sin comprimir, para que la web las sirva como ficheros estáticos.
3. **[`offline/tiles_meta.py`](offline/tiles_meta.py) escribe `tiles.json`, un TileJSON con la atribución «© OpenStreetMap contributors (ODbL) · © OpenMapTiles».**
   - **Límites:** los calcula con las teselas de z14, porque los de tilemaker salen mal.
   - **Antes de rellenar, comprueba lo que escribió tilemaker:** al menos 4.000 teselas con contenido, y alguna en cada zoom desde el 7, donde empiezan las calles del estilo. De z0 a z2 la Comunidad no tiene nada que dibujar. Si no llega, para, para que un tilemaker que falló a medias no quede tapado por teselas vacías.
   - **Huecos:** rellena con teselas vacías los que hay dentro de esos límites. Si no, MapLibre los pediría, y cada 404 sería un error de consola.
   - **Fuera de la Comunidad,** en las esquinas de ese rectángulo y más allá, el mapa sale en blanco: solo el color de fondo, sin calles. Todas las zonas de la demo están dentro.
4. **Resultado** en `data/offline/tiles/`, que git ignora: 4.750 teselas de tilemaker (4.490 con contenido) y 3.365 vacías de relleno, 89 MB.
   - `manifest.txt` guarda el fichero, su md5, la imagen y los límites.
   - El 12 nov: 0 hosts cortados y 0 errores de consola sin red (`offline-teselas.md`).

Sin `data/offline/tiles/`, `prepare` avisa y compila la web con OpenFreeMap, que necesita red. El `manifest.txt` del paquete dice cuál de los dos lleva (`basemap`).

### Regenerarlo (23 nov, con Internet, tras el freeze)

En el checkout que se vaya a usar el 26, con la base de desarrollo arrancada y en la misma migración que el checkout. Si aún no existe `data/offline/tiles/`, primero `make demo-offline-tiles`:

```bash
make demo-offline-prepare
```

Unos 25–45 s. **No se pierde nada hasta que el paquete nuevo está validado.** El comando hace lo siguiente:
1. Construye las imágenes: Postgres con PostGIS, y la API.
2. Comprueba que la base de origen responde. Si no, da un mensaje claro con la URL enmascarada y para.
3. Comprueba que la migración de la base de origen es la misma que la del checkout.
4. Vuelca, en modo solo lectura, las 11 tablas del perfil demo (con `transit_hub` y `commute_time` desde CORE-009, D-220) (las mismas que `make supabase-sync PROFILE=demo`) a `demo-data.sql.gz.tmp`.
5. Crea el esquema con Alembic en una base **staging**, carga el volcado y **compara los conteos de filas** con la base de origen.
6. Compila la web (Next.js standalone) contra `http://localhost:8012`, en la copia privada, con el buscador encendido (`NEXT_PUBLIC_FEATURE_SEARCH=true`, como en producción; desde el 12 nov). Si hay mapa base local, la compila con `NEXT_PUBLIC_MAP_TILES_URL=/tiles/tiles.json` y copia las teselas a su `public/tiles`. Con las teselas, tarda unos 4–5 minutos.
7. Solo si todo lo anterior sale bien: la base staging pasa a ser la base de la demo y los ficheros `.tmp` sustituyen a los anteriores.

Si algo falla, el paquete anterior sigue intacto y `make demo-offline` funciona con él.

El resultado se guarda en `data/offline/`, que git ignora:
- `demo-data.sql.gz`: 44 MB el 12 nov a las 13:35, con fit-0.2;
- `manifest.txt`: fecha, commit, migración y conteos;
- `web/`: el servidor web listo para arrancar.

- Si la base de origen va por delante del checkout con una migración que no toca las tablas de la demo (por ejemplo, un rol), se puede forzar con `DEMO_OFFLINE_ALLOW_HEAD_MISMATCH=1`.
- El volcado sale de la base local de desarrollo, que es la que A sincroniza con Supabase. Si se quiere exactamente lo publicado, hay que regenerar justo después de `make supabase-sync PROFILE=demo`.
  - Si no, las cifras pueden no coincidir con producción. El 12 nov, la base local ya tenía la auditoría de D-216 y Supabase todavía no. El caso de ejemplo daba 33 zonas en el paquete y 32 en producción.
  - Para saber si la diferencia importa, compara los conteos de `manifest.txt` con Supabase y las respuestas de la API (`/search` con el caso del guion, `/gaps`, `/datasets`) del paquete con las de producción. El 12 nov a las 13:35 la base local tenía 9.686 filas de parques de más en `feature_value` (DATA-018). La API no las leía y las respuestas eran iguales (`offline-fit02.md`).
  - El guion siempre lee las cifras de la pantalla. Aun así, el 23 hay que regenerar después del último sync.

### Arrancarlo (26 nov, en 1 minuto, sin red)

```bash
make demo-offline        # ~8 s: base, API, web y smoke 7/7 (sin la web, con /search)
# abre http://localhost:3012/map
make demo-offline-stop   # al terminar; los datos se quedan en el volumen
```

- `start` no construye ni descarga nada (`--no-build`).
- **Sin red, el mapa sale con calles** si el paquete se preparó con el mapa base local (`make demo-offline-tiles`): la web sirve las teselas desde `http://localhost:3012/tiles`.
  - **Sin ese mapa base:** la web pide el fondo a `tiles.openfreemap.org` y, sin Internet, no llega. Siguen funcionando las zonas coloreadas, el buscador, «¿Y si cambias algo?», «Qué falta» y la lista.
  - **El aviso en ese caso:** la web enseña arriba «Mapa sin fondo de calles.», y la consola registra los fallos de esas teselas. Si fallara el mapa entero, el aviso sería «No se ha podido cargar el mapa. Puedes seguir con la lista de zonas.».
- **`start` comprueba el volumen**, no solo el volcado. Si la base no coincide con `manifest.txt` (por ejemplo, porque se borró el volumen de Docker), la restaura desde `demo-data.sql.gz` en unos 11 s. Para eso necesita `uv`, que ya está instalado.
- **`stop` solo mata su propio servidor web.** Antes comprueba que el pid de `web.pid` sigue siendo el de Next.js. Si algo falla a medias, el script lo dice: «Clean up with: make demo-offline-stop».
- No hace falta calentarlo. Los procesos quedan arrancados y el propio `make demo-offline` pasa el smoke al terminar, así que la API ya ha respondido una vez.
- **Requisitos el 26:**
  - Docker Desktop abierto, con las imágenes `vida-facil-offline-db:17` y `vida-facil-api:offline` ya construidas el 23;
  - Node;
  - no hace falta Internet.
- **Si un puerto está ocupado:** `make demo-offline-stop`, o cierra lo que use el 3012, el 8012 o el 5441.
- **Ensayo:** hazlo el 24–25 con el wifi apagado. Si la web nueva de B usa teselas, fuentes o imágenes externas, lo verás ahí: tienen que venir incluidas en la build.
  - Con el paquete arrancado, los recorridos del pitch se comprueban solos: `node infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3012 --block-external`.
  - `--block-external` corta toda petición que no vaya a localhost, como si no hubiera red. El informe lista los hosts cortados.
  - **El 12 nov, con el mapa base local:** 66/66 y 40/40, sin ningún host cortado y sin errores de consola (`offline-teselas.md`).
  - **Antes, con OpenFreeMap:** el único host cortado era `tiles.openfreemap.org`, y solo fallaba la comprobación de «consola sin errores».

## Problemas conocidos

- **Versión del CLI:** usa `npx vercel@65.12.1`. El CLI global 54.x no entiende `services` en `vercel.json`.
- **`vercel link`:** añade `.env*` a `.gitignore`, con lo que vuelve a ignorar `.env.example`. Hay que revertir esa línea. Además escribe un token OIDC en `.env.local`, que está ignorado por git y por `.vercelignore`.
- **Docker Desktop (macOS):** si `docker build` se queda en `resolve image config`, el helper de credenciales `desktop` no responde. Solución: `DOCKER_CONFIG` temporal con `{}` y un enlace a `~/.docker/cli-plugins`.
- **Build de la web con fuentes de Google (resuelto):** el 11 nov, el primer build en Vercel falló con `Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'`, y pasó al segundo intento.
  - B sirve ahora Plus Jakarta Sans e Inter desde el repo con `next/font/local` (`apps/web/src/app/fonts.ts`), así que ni el build ni el paquete offline dependen de Google Fonts.
  - Si un build falla por cualquier otra causa: `deploy.sh` sale con 1 y producción no cambia.
