# Despliegue de la demo «Vida Fácil» (OPS-001)

Web (Next.js) y API (FastAPI) en **un solo proyecto de Vercel**, `vida-facil`, leyendo de Supabase (`ilvbivfnqvfqslbbiuts`, eu-west-1).

- URL pública: **https://vidafacil-madrid.vercel.app**, la elegida por Mariano el 11 nov. La web está en `/` y la API en `/api/v1/*`, en el mismo dominio, así que no hay CORS cruzado.
- Alias secundario: `https://vida-facil-eight.vercel.app`. Es el que asignó Vercel al crear el proyecto (otra cuenta ya usa `vida-facil.vercel.app`) y se mantiene para no romper los enlaces ya compartidos. `CORS_ORIGINS` acepta los dos.
- Si se cambia el dominio, hay que actualizar `NEXT_PUBLIC_API_URL`, `CORS_ORIGINS` y `DEMO_URL` en `deploy.sh` y en `smoke_demo.sh`, y volver a desplegar.
- Región de cómputo: `dub1` (Dublín), junto a la base de datos.
- Equipo de Vercel: `mariano-hernando-s-projects`, la cuenta del CLI de Mariano.
- Por qué Vercel y no Render ni Cloud Run: [evidence/gate-06/2026-11-11-deploy/provider-research.md](../../evidence/gate-06/2026-11-11-deploy/provider-research.md).

## Piezas

| Fichero | Para qué |
|---|---|
| [`vercel.json`](../../vercel.json) | Dos servicios (Vercel Services, beta): `web` sale de `apps/web` (Next.js) y `api` es un contenedor construido con `infra/deploy/api/Dockerfile`. También fija la región y las reglas de enrutado. |
| [`.vercelignore`](../../.vercelignore) | Lista de lo que se sube. Solo sale el código: nunca `.env*`, `*.pem`, `*.key`, `*.db`, `*.sqlite`, `node_modules`, `data/` ni `docs/`. |
| [`api/Dockerfile`](api/Dockerfile) | Imagen de la API con solo las dependencias de `hi-api` (`uv sync --package hi-api`). Usuario no root y puerto `$PORT`. |
| [`deploy.sh`](deploy.sh) | `make deploy-demo`. Comprueba que el árbol está limpio y que la rama es la de la demo (`claude/sprint-1-public` o `main`; otra solo con `ALLOW_BRANCH=1`). Avisa de los ficheros sensibles locales que no se suben. Después despliega a producción y pasa el smoke. |
| [`offline/`](offline/) | Paquete offline para la final: `make demo-offline-prepare`, `make demo-offline` y `make demo-offline-stop`. Ver más abajo. |
| [`../../scripts/smoke_demo.sh`](../../scripts/smoke_demo.sh) | `make smoke-demo`: comprueba web, `health`, `ready`, una zona, la geografía y una capa, y que ninguna respuesta pase de 4,5 MB. |
| [`sql/api_readonly_role.sql`](sql/api_readonly_role.sql) | Rol `vf_api_ro`: solo lectura, con una política RLS por cada tabla que lee la API. Es idempotente. |

## Variables de entorno (proyecto Vercel, entorno Production)

Aquí solo van los nombres, nunca los valores. Las variables que no son secretas las fija la línea C con el CLI. Los secretos los mete Mariano.

| Variable | Servicio | Tipo | Valor o forma |
|---|---|---|---|
| `DATABASE_URL` | api | **Secreto** (Sensitive). Lo mete Mariano | `postgresql+psycopg://<usuario>.ilvbivfnqvfqslbbiuts:<contraseña>@aws-0-eu-west-1.pooler.supabase.com:5432/postgres?sslmode=require`. Es el Session pooler: la conexión directa es solo IPv6. El usuario es `vf_api_ro` cuando exista el rol y, mientras tanto, el de `SUPABASE_DATABASE_URL`. El esquema tiene que ser `postgresql+psycopg://`. |
| `CORS_ORIGINS` | api | Config | `["https://vidafacil-madrid.vercel.app","https://vida-facil-eight.vercel.app"]`, una lista JSON |
| `PORT` | api | Config | `8080`. El contenedor escucha ahí y Vercel enruta a `$PORT` |
| `NEXT_PUBLIC_API_URL` | web | Config | `https://vidafacil-madrid.vercel.app`. Se incrusta al compilar: si cambia, hay que volver a desplegar |

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
   - despliega web y API en producción;
   - publica los dos dominios, `vidafacil-madrid` y `vida-facil-eight`;
   - pasa `scripts/smoke_demo.sh`. Si el smoke falla, sale con un código distinto de 0 e imprime el comando de rollback.

   Desde otra rama solo se despliega a propósito, con `ALLOW_BRANCH=1 make deploy-demo`.

3. Guarda la salida en `evidence/gate-06/<fecha>-deploy/`.

**Tiempo:** unos 100 s con el smoke incluido. Construye la imagen de la API y la web.

**Sin Git:** la integración con GitHub está desconectada a propósito. Los push de las líneas no despliegan nada; solo despliega `make deploy-demo`.

## Volver atrás

- **Instant Rollback en Hobby:** solo permite volver al despliegue de producción inmediatamente anterior ([docs](https://vercel.com/docs/instant-rollback)). Comando: `npx vercel@65.12.1 rollback`, o desde el panel: Production Deployment → Instant Rollback.
- **Después de un rollback:** Vercel desactiva la asignación automática del dominio. El siguiente despliegue no queda publicado hasta que lo promueves con `npx vercel@65.12.1 promote <url-del-despliegue>`.
- **Variables de entorno:** el rollback no las cambia. Si el fallo era una variable, corrígela y vuelve a desplegar.
- **Si el fallo está en los datos y no en el código:** no se arregla con un rollback. A vuelve a ejecutar `make supabase-sync PROFILE=demo` con la versión buena de la base local.

## Límites del plan gratuito (Hobby)

| Recurso | Límite | Riesgo para la demo |
|---|---|---|
| Uso | Solo personal y no comercial ([fair use](https://vercel.com/docs/limits/fair-use-guidelines)) | Una demo de concurso sin pagos ni anuncios encaja |
| Invocaciones | 1.000.000 al mes | Bajo |
| CPU activa | 4 h al mes, **compartidas con los otros proyectos del equipo** | Medio: vigilar en Usage |
| Memoria provisionada | 360 GB-h al mes | Bajo |
| Transferencia | 100 GB al mes (Fast Data Transfer) y 10 GB (Origin Transfer) | Bajo: la respuesta más grande pesa 2,8 MB |
| Respuesta | 4,5 MB como máximo por respuesta no streaming ([límites](https://vercel.com/docs/functions/limitations)) | El smoke lo comprueba |
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

## Día de la final (26 nov): lista

1. **Por la mañana:**
   - `make smoke-demo` tiene que dar 6/6. Si falla, sigue la sección «Si la demo se cae».
   - Comprueba que el paquete offline arranca (`make demo-offline`, abrir `http://localhost:3012/map` y luego `make demo-offline-stop`).
   - Lleva las capturas y el vídeo del recorrido.
2. **En la sala:** conecta el portátil a la red y abre https://vidafacil-madrid.vercel.app/map. Si no hay red o Vercel no responde, usa `make demo-offline` y abre `http://localhost:3012/map`.
3. **Calentamiento, 2–3 minutos antes de presentar:** ejecuta `make smoke-demo`.
   - Sus 6 peticiones pasan por la web y por cada ruta que usa la demo: health, ready, zona, geografía y capa.
   - Así el contenedor de la API ya está arrancado y no te comes los 3–4 s del arranque en frío delante del jurado.
   - Deja después la pestaña de la demo abierta y recárgala una vez.
   - El contenedor se apaga tras 5 min sin tráfico. Si entre el calentamiento y tu turno pasan más de 5 min, repítelo.
4. **Durante la presentación:** si una petición se queda colgada más de 10 s, cambia al paquete offline (`make demo-offline`, unos 7 s) en vez de esperar.

## Si la demo se cae

1. **Diagnóstico (1 minuto):** `make smoke-demo`.
   - `health` falla: la caída es de la plataforma o de la API.
   - `health` funciona pero `ready` falla con `SOURCE_DEGRADED`: la base de datos no responde (Supabase pausada o caída, o la credencial está mal).
   - `ready` falla con `INSUFFICIENT_DATA`: el rol no ve filas (falta una política o un `GRANT`) o los datos no están cargados.
2. **Si el fallo vino con el último despliegue:** Instant Rollback (ver arriba).
3. **Si Supabase está pausada:** reanúdala desde el panel de Supabase con la cuenta dedicada a DATAMAD y vuelve a pasar el smoke.
4. **Sin Internet o con Vercel caído durante la presentación:** `make demo-offline`, el paquete offline de la sección siguiente. Arranca en unos 7 s en el portátil, con los mismos datos. Lleva también capturas y un vídeo corto del recorrido, grabados con la versión desplegada.
5. **Si Vercel cae varios días:** el mismo `infra/deploy/api/Dockerfile` sirve en Render o en Cloud Run. Las opciones B y C están en `provider-research.md` y necesitan cuenta.

## Paquete offline para la final (26 nov)

Es la demo completa en el portátil, sin Internet: la API (la misma imagen que en Vercel) y la web, con un volcado del perfil demo. Corre en una base aislada:
- proyecto de compose `vida-facil-offline`, con su propio volumen;
- Postgres en `127.0.0.1:5441`, API en `:8012` y web en `:3012`.

No toca la base de desarrollo (`housing`, puerto 5440) ni sus puertos 8010 y 3010. A la base de desarrollo solo la lee para hacer el volcado.

### Regenerarlo (23 nov, con Internet, tras el freeze)

En el checkout que se vaya a usar el 26, con la base de desarrollo arrancada y en la misma migración que el checkout:

```bash
make demo-offline-prepare
```

Unos 25 s. El comando hace lo siguiente:
1. Construye las imágenes (Postgres con PostGIS y la API).
2. Recrea vacía la base offline.
3. Comprueba que la migración de la base de origen coincide con la del checkout.
4. Vuelca, en modo solo lectura, las 9 tablas del perfil demo (las mismas que `make supabase-sync PROFILE=demo`).
5. Crea el esquema con Alembic y carga los datos.
6. **Compara los conteos de filas** con la base de origen.
7. Compila la web (Next.js standalone) contra `http://localhost:8012`.

El resultado se guarda en `data/offline/`, que git ignora: `demo-data.sql.gz` (41 MB el 11 nov) y `manifest.txt` (fecha, commit, migración y conteos).

- Si la base de origen va por delante del checkout con una migración que no toca las tablas de la demo (por ejemplo, un rol), se puede forzar con `DEMO_OFFLINE_ALLOW_HEAD_MISMATCH=1`.
- El volcado sale de la base local de desarrollo, que es la que A sincroniza con Supabase. Si se quiere exactamente lo publicado, hay que regenerar justo después de `make supabase-sync PROFILE=demo`.

### Arrancarlo (26 nov, en 1 minuto, sin red)

```bash
make demo-offline        # ~7 s: base, API, web y smoke 5/5
# abre http://localhost:3012/map
make demo-offline-stop   # al terminar; los datos se quedan en el volumen
```

- `start` no construye ni descarga nada (`--no-build`). Comprobado con un navegador headless: 0 peticiones a hosts externos y la consola sin errores.
- No hace falta calentarlo. Los procesos quedan arrancados y el propio `make demo-offline` pasa el smoke al terminar, así que la API ya ha respondido una vez.
- **Requisitos el 26:**
  - Docker Desktop abierto, con las imágenes `vida-facil-offline-db:17` y `vida-facil-api:offline` ya construidas el 23;
  - Node, con `node_modules` instalado;
  - no hace falta `uv` ni Internet.
- **Si un puerto está ocupado:** `make demo-offline-stop`, o cierra lo que use el 3012, el 8012 o el 5441.
- **Ensayo:** hazlo el 24–25 con el wifi apagado. Si la web nueva de B usa teselas, fuentes o imágenes externas, lo verás ahí: tienen que venir incluidas en la build.

## Problemas conocidos

- **Versión del CLI:** usa `npx vercel@65.12.1`. El CLI global 54.x no entiende `services` en `vercel.json`.
- **`vercel link`:** añade `.env*` a `.gitignore`, con lo que vuelve a ignorar `.env.example`. Hay que revertir esa línea. Además escribe un token OIDC en `.env.local`, que está ignorado por git y por `.vercelignore`.
- **Docker Desktop (macOS):** si `docker build` se queda en `resolve image config`, el helper de credenciales `desktop` no responde. Solución: `DOCKER_CONFIG` temporal con `{}` y un enlace a `~/.docker/cli-plugins`.
