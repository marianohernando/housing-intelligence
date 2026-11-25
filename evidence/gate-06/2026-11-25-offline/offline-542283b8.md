# Paquete sin conexión para el día final · 542283b8 · 25 nov 2026

Es el plan B por si el 26 falla la red en Vicálvaro: la demo entera corre en el portátil, sin internet.

Comprobado el 25 nov a las 10:47–10:50 UTC (11:47–11:50 en hora peninsular).
- **Paquete:** `make demo-offline-prepare`. Lo lanzó Mariano en su terminal el 24 nov, porque el aviso de seguridad de Next bloquea las builds lanzadas por agentes.
- **Arranque:** `make demo-offline`. API en el puerto 8012, web en el 3012.
- **Parada:** `make demo-offline-stop`. El volumen de datos se conserva.

## Manifiesto del paquete

```text
created_at 2026-11-24T09:57:51Z
git_commit 542283b8
alembic_head 0007 (source 0007)
basemap local, madrid-261111.osm.pbf, label fonts local
source_registry 16
dataset_registry 66
dataset_version 80
metric_registry 57
feature_registry 77
geo_admin_unit 4973
place_master 41686
place_source_alias 42169
feature_value 120586
transit_hub 579
commute_time 191649
```

Es el mismo código que la producción de deploy-46 (`542283b8`, ver `../2026-11-23-deploy/deploy-46-542283b8-mcp-dcat.md`). El mapa base y las tipografías van en local.

## Resultados

| Prueba | Resultado |
|---|---|
| Arranque desde el paquete (`make demo-offline`) | 14 s |
| Smoke de la API (`SMOKE_API_ONLY=1 scripts/smoke_demo.sh`) | **14/14 OK**: health, ready, la zona Madrid (6 filas), 179 municipios, capas, la búsqueda (199 zonas, 131 barrios, 40 alrededores, 138 pueblos), `mcp-init` (protocolo 2025-06-18) y `mcp-tools` (7) |
| `GET /api/v1/datasets?cm_only=true` | `total` 39 y `cm_open_data_count` 39 |
| `GET /api/v1/gaps/distrito/2807905` (Chamartín) | `gap-0.4`. Escuelas infantiles JUSTO, colegios CUBIERTO, centros de salud CUBIERTO, mayores JUSTO, farmacias CUBIERTO, vivienda SIN_DATOS: lo mismo que en producción (`../2026-11-23-mcp-claude-web/prueba-claude-web.md`) |
| Portada | Título y h1: «La zona que te conviene, y lo que le falta» |
| `/como-lo-calculamos`, contado en el navegador | «39 conjuntos de datos del Portal de Datos Abiertos de la Comunidad de Madrid» |
| `/datos/catalogo.dcat.jsonld` y `/desarrolladores` | 200 |
| e2e del pitch, `node infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3012 --block-external` | **chromium desktop-1440: 139/139** (35 s) · **chromium mobile-390: 119/119** (27 s) |
| Peticiones fuera de localhost durante el e2e | **0 bloqueadas**: no se intentó ninguna |

Con `--block-external` falla cualquier petición fuera de localhost, como si no hubiera red. Como no hubo ninguna, la demo no depende de internet para nada del recorrido del pitch.

## Cómo usarlo el 26

1. Con la red del portátil apagada: `make demo-offline`.
2. Abrir `http://localhost:3012/`.
3. Al acabar: `make demo-offline-stop`.
