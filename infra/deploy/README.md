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
| [`offline/`](offline/) | Paquete offline para la final: `make demo-offline-prepare`, `make demo-offline` y `make demo-offline-stop`. Ver más abajo. |
| [`../../scripts/smoke_demo.sh`](../../scripts/smoke_demo.sh) | `make smoke-demo`: comprueba web, `health`, `ready`, una zona, la geografía, una capa (educación), la página 1 de la capa más grande (transporte) y una búsqueda (`POST /api/v1/search` con el caso demo del guion: al menos una zona y menos de 1 MB). También comprueba que ninguna respuesta pase de 4,5 MB. Se identifica con el User-Agent `vida-facil-smoke` (más `/<etiqueta>` si se define `SMOKE_TAG`). |
| [`sql/api_readonly_role.sql`](sql/api_readonly_role.sql) | Rol `vf_api_ro`: solo lectura, con una política RLS por cada tabla que lee la API. Es idempotente. |

## Variables de entorno (proyecto Vercel, entorno Production)

Aquí solo van los nombres, nunca los valores. Las variables que no son secretas las fija la línea C con el CLI. Los secretos los mete Mariano.

| Variable | Servicio | Tipo | Valor o forma |
|---|---|---|---|
| `DATABASE_URL` | api | **Secreto** (Sensitive). Lo mete Mariano | `postgresql+psycopg://<usuario>.ilvbivfnqvfqslbbiuts:<contraseña>@aws-0-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=require`. Es el Session pooler: la conexión directa es solo IPv6. El usuario es `vf_api_ro` cuando exista el rol y, mientras tanto, el de `SUPABASE_DATABASE_URL`. El esquema tiene que ser `postgresql+psycopg://`. |
| `CORS_ORIGINS` | api | Config | `["https://vidafacil-madrid.vercel.app","https://vida-facil-eight.vercel.app"]`, una lista JSON |
| `PORT` | api | Config | `8080`. El contenedor escucha ahí y Vercel enruta a `$PORT` |
| `DB_POOL_SIZE` | api | Config | `2` desde el 12 nov: conexiones fijas a la base por instancia. El código pone 5 por defecto (`packages/db`, `make_engine`, 4645326). El pooler de Supabase en modo sesión admite tantos clientes como su `pool_size`, compartidos por todas las instancias: 15 en el plan actual del proyecto. No es un límite fijo del pooler (incidente en `evidence/gate-06/2026-11-12-deploy/deploy-13-auditoria-gap03.md`) |
| `DB_MAX_OVERFLOW` | api | Config | `1` desde el 12 nov: conexiones extra en un pico, que se cierran al devolverse. Por defecto, 10. Con 2 + 1, cada instancia usa como mucho 3, y caben 5 instancias en los 15 clientes que admite hoy el pooler |
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
- **Variables de entorno:** el rollback no las cambia. Si el fallo era una variable, corrígela y vuelve a desplegar.
- **Si el fallo está en los datos y no en el código:** no se arregla con un rollback. A vuelve a ejecutar `make supabase-sync PROFILE=demo` con la versión buena de la base local.
- **Si el fallo es el límite de conexiones de la base, tampoco.** En los logs sale `EMAXCONNSESSION max clients reached in session mode`.
  - El pooler en modo sesión admite tantos clientes como su `pool_size`: 15 en el plan actual de Supabase. No es un límite fijo del pooler. Las instancias vivas del despliegue que falla siguen ocupándolos, y las del despliegue anterior no consiguen ninguno.
  - El 12 nov el rollback dejó el smoke en 2/8. Volver a promover el despliegue nuevo lo arregló en el acto (`deploy-13-auditoria-gap03.md`).
  - El arreglo de fondo es menos conexiones por instancia o el pooler en modo transacción (puerto 6543).

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
   - El sync vacía con `TRUNCATE` las 9 tablas del perfil demo y las vuelve a copiar una a una. Mientras dura, la demo enseña zonas SIN DATOS y capas vacías. El 11 nov se vio `feature_value` con 0 filas a mitad de un sync.
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
   - Hay 500 sueltos, sobre todo en la vista de zona, y en `npx vercel@65.12.1 logs --environment production --since 15m` sale `EMAXCONNSESSION`: está lleno el pooler de Supabase. No hagas rollback (ver «Volver atrás»). Espera a que bajen las instancias: unos 5 min sin tráfico, una estimación hecha con el apagado por inactividad del container runtime, no una garantía. O reduce las conexiones por instancia (`DB_POOL_SIZE`, `DB_MAX_OVERFLOW`); eso exige redesplegar, porque las variables solo se aplican en los despliegues nuevos.
2. **Si el fallo vino con el último despliegue:** Instant Rollback (ver arriba).
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

### Regenerarlo (23 nov, con Internet, tras el freeze)

En el checkout que se vaya a usar el 26, con la base de desarrollo arrancada y en la misma migración que el checkout:

```bash
make demo-offline-prepare
```

Unos 25–45 s. **No se pierde nada hasta que el paquete nuevo está validado.** El comando hace lo siguiente:
1. Construye las imágenes: Postgres con PostGIS, y la API.
2. Comprueba que la base de origen responde. Si no, da un mensaje claro con la URL enmascarada y para.
3. Comprueba que la migración de la base de origen es la misma que la del checkout.
4. Vuelca, en modo solo lectura, las 9 tablas del perfil demo (las mismas que `make supabase-sync PROFILE=demo`) a `demo-data.sql.gz.tmp`.
5. Crea el esquema con Alembic en una base **staging**, carga el volcado y **compara los conteos de filas** con la base de origen.
6. Compila la web (Next.js standalone) contra `http://localhost:8012`, en la copia privada, con el buscador encendido (`NEXT_PUBLIC_FEATURE_SEARCH=true`, como en producción; desde el 12 nov).
7. Solo si todo lo anterior sale bien: la base staging pasa a ser la base de la demo y los ficheros `.tmp` sustituyen a los anteriores.

Si algo falla, el paquete anterior sigue intacto y `make demo-offline` funciona con él.

El resultado se guarda en `data/offline/`, que git ignora:
- `demo-data.sql.gz`: 43 MB el 12 nov;
- `manifest.txt`: fecha, commit, migración y conteos;
- `web/`: el servidor web listo para arrancar.

- Si la base de origen va por delante del checkout con una migración que no toca las tablas de la demo (por ejemplo, un rol), se puede forzar con `DEMO_OFFLINE_ALLOW_HEAD_MISMATCH=1`.
- El volcado sale de la base local de desarrollo, que es la que A sincroniza con Supabase. Si se quiere exactamente lo publicado, hay que regenerar justo después de `make supabase-sync PROFILE=demo`.
  - Si no, las cifras pueden no coincidir con producción. El 12 nov, la base local ya tenía la auditoría de D-216 y Supabase todavía no. El caso de ejemplo daba 33 zonas en el paquete y 32 en producción.
  - El guion siempre lee las cifras de la pantalla. Aun así, el 23 hay que regenerar después del último sync.

### Arrancarlo (26 nov, en 1 minuto, sin red)

```bash
make demo-offline        # ~8 s: base, API, web y smoke 7/7 (sin la web, con /search)
# abre http://localhost:3012/map
make demo-offline-stop   # al terminar; los datos se quedan en el volumen
```

- `start` no construye ni descarga nada (`--no-build`).
- **Sin red, el mapa sale sin fondo.** La web nueva pide el mapa base a `tiles.openfreemap.org` (`apps/web/src/lib/map/style.ts`), y sin Internet ese fondo no llega.
  - Sí funcionan las zonas coloreadas, el buscador, «¿Y si cambias algo?», «Qué falta» y la lista.
  - La web enseña arriba el aviso «No se ha podido cargar el mapa. Puedes seguir con la lista de zonas.», y la consola registra los fallos de esas teselas.
  - Comprobado el 12 nov con `--block-external` (ver «Ensayo»).
  - Para tener fondo sin red, B tendría que hacer configurable el TileJSON y el paquete tendría que servir un extracto local de Madrid. Está propuesto, no hecho.
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
  - El 12 nov el único host cortado fue `tiles.openfreemap.org`, y todas las comprobaciones de datos pasaron. Solo falló la de «consola sin errores», por esas teselas.

## Problemas conocidos

- **Versión del CLI:** usa `npx vercel@65.12.1`. El CLI global 54.x no entiende `services` en `vercel.json`.
- **`vercel link`:** añade `.env*` a `.gitignore`, con lo que vuelve a ignorar `.env.example`. Hay que revertir esa línea. Además escribe un token OIDC en `.env.local`, que está ignorado por git y por `.vercelignore`.
- **Docker Desktop (macOS):** si `docker build` se queda en `resolve image config`, el helper de credenciales `desktop` no responde. Solución: `DOCKER_CONFIG` temporal con `{}` y un enlace a `~/.docker/cli-plugins`.
- **Build de la web con fuentes de Google:** la web descarga Plus Jakarta Sans e Inter de Google Fonts al compilar (`next/font/google`).
  - El 11 nov, el primer build en Vercel falló con `Module not found: Can't resolve '@vercel/turbopack-next/internal/font/google/font'` («next/font/google queries have exactly one entry»). El mismo commit compiló en local, y en Vercel al segundo intento.
  - Si pasa: `deploy.sh` sale con 1 y producción no cambia. Repite `make deploy-demo`.
  - Para quitar esa dependencia de la red, B puede servir las fuentes desde el repo con `next/font/local`. Es un cambio en `apps/web`, de B.
