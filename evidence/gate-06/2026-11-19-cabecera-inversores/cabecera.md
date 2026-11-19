# «Inversores» en la cabecera y en «Cómo lo calculamos» (19 nov, D-251)

Rama `claude/f12-header-inversores`. Web con `next dev` en el 3096 (con `NEXT_PUBLIC_FEATURE_SEARCH=true`, como en producción) y la API de la rama en el 8096 con `PARCEL_UPSTREAMS=false` y la base `housing` en solo lectura. La barra «N» de Next que pueda verse es la de desarrollo.

## Capturas (las de la revisión del #104, con el degradado casi opaco, 98 %, sobre el mapa en el móvil)

- `360-cabecera-*.png` y `1440-cabecera-*.png`: la cabecera en el mapa (la portada, sin pie), en «Qué falta», en «Cómo lo calculamos», en `/inversores` y en la ficha de una parcela de demostración (2122202VK4722A). La pestaña activa, con fondo y borde.
- `390-cabecera-mapa.png`: la cabecera sobre el mapa a 390 px.
- `*-mapa-primera-pantalla.png` y `*-inversores-primera-pantalla.png`: la primera pantalla entera.

## Comprobaciones

- `check-cabecera.json`, escrito por `apps/web/scripts/check-cabecera.mjs --shots` (versionado): a 360, 390 y 1440 px, en esas cinco páginas, las cuatro pestañas en una fila y dentro de la pantalla, ningún texto de menos de 16 px ni objetivo de menos de 44 px en la cabecera, sin desborde horizontal, la pestaña activa marcada con `aria-current`, fondo y borde (no solo color), axe 0, y **el contraste de las letras de cada pestaña sobre los píxeles que tienen detrás** (captura con y sin letras; cuenta el peor píxel): como poco **5,48:1, sobre el mapa a 360 y 390 px**. Sin el arreglo del degradado, el mismo script daba 1,69:1 (360) y 1,74:1 (390) sobre el mapa.
- `tamanos-d251.json` (`apps/web/scripts/check-ux-mobile.mjs`): las pantallas del recorrido, mapa incluido, a 390 px sin textos de menos de 16 px ni objetivos de menos de 44 px (los 3 del mapa son sus controles, contados aparte como siempre), y axe 0 a 390, 360 y 1440 px.
- `apps/web/scripts/check-desarrolladores.mjs`: verde a 360, 390 y 1440 px con `main` en los enlaces y el `git clone` sin `--branch`.
- e2e (`infra/deploy/e2e/e2e_prod.mjs`): 145/145 a 1440 px y 121/121 a 390 px. `check-parcela.mjs` (21 pantallas) y `check-inversores.mjs`, verdes con los enlaces nuevos «Cómo lo calculamos».
