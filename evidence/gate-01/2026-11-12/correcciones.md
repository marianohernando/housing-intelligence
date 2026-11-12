# Correcciones con fuente oficial (D-218 §10)

Decisión de Mariano (delegada en `datamad-10`, 12 nov): fichero de correcciones versionado, `data/catalog/corrections/places.yaml`, solo con una fuente oficial por registro (URL, fecha de consulta y su texto exacto). Generado con la base local tras `hi-ingest run cm_centros_sanitarios` (parser `places-1.6.0`; el fichero entra como input `corrections` en el linaje y en la suma de comprobación de la carga) y `hi-features compute`.

## Aplicadas (5)

| Registro CM | Antes | Corrección y fuente | Ahora |
|---|---|---|---|
| CH0049 | «Hospital general (Madrid)», sin camas (Fuencarral-El Pardo) | Emparejado a mano con el CNH 280029: el catálogo lo sitúa en la calle de Ayala 38 (28001); la web del hospital (comunidad.madrid/hospital/ramonycajal, consultada el 12 nov) dice «Ctra. de Colmenar Viejo km. 9,100 28034 Madrid», como el registro | «Hospital Universitario Ramon y Cajal» · 886 camas instaladas · `match_method: correccion` |
| CS1184 | En cuarentena: «calle de Arenas del Rey S/N» (Madrid) | Catálogo de Centros de AP 2026 del Ministerio: «ORCASUR · CALLE ARENAS DEL REY, Nº 1 · 28041» | Geocodificado con CartoCiudad (portal 1) · «Centro de salud Orcasur» |
| CS6158 | En cuarentena: «calle de Mirueña S/N» (Madrid) | «CAMPAMENTO · CALLE MIRUEÑA, Nº 5 · 28024» | Geocodificado (portal 5) · «Centro de salud Campamento» |
| CS10286 | En cuarentena: «Valle Inclán S/N c/v G. A. Bécquer» (Alcalá de Henares) | «MIGUEL DE CERVANTES · CALLE GUSTAVO ADOLFO BECQUER, Nº 23 · 28805» | Geocodificado (portal conocido más cercano, 21 por 23) · «Centro de salud Miguel de Cervantes» |
| CS7529 | En cuarentena: «calle Juan de Borgoña s/n» (Alcalá de Henares) | «MARÍA DE GUZMÁN · CALLE JUAN DE BORGOÑA, Nº 1 · 28805» | Geocodificado (portal 1) · «Centro de salud María de Guzmán» |

Cada lugar corregido lleva `attributes.correction` (tipo, motivo, fuente, URL y fecha de consulta). Las coordenadas siguen saliendo de CartoCiudad con las reglas de D-216 (solo portal en el municipio declarado y calle que coincide).

## Efecto en las features (recalculadas)

| Zona | Centros de salud a pie (por 10.000) | Minutos a pie al centro de salud |
|---|---|---|
| Alcalá de Henares | 0,395 → 0,494 (CUBIERTO, ratio 1,07 → 1,33) | 20,2 → 14,9 |
| Latina | 0,346 → 0,383 | 10,5 → 10,2 |
| Usera | 0,340 → 0,392 | 9,0 → 8,2 |

Resumen de estados: `evidence/gate-04/2026-11-12/gap-status-after-corrections.md`.

## Sin corregir (sin fuente oficial utilizable), declarados

| Registro | Por qué |
|---|---|
| CS11438 · consultorio de Villar del Olmo | El registro y el Ministerio coinciden («calle Real 42»), pero CartoCiudad no tiene ese portal en Villar del Olmo (devuelve una calle Real de Jaén). Ninguna fuente oficial publica sus coordenadas |
| 28082174 · CEIP Navalafuente (centros educativos, alta en 2024) | La única dirección oficial es la del registro («calle Eras de Arriba 56»); CartoCiudad solo conoce hasta el portal 16. Sin coordenadas oficiales |
| CS12766 · consultorio de Buitrago (D-216) | Coordenadas en otro municipio y el geocodificador devuelve otra calle; sin fuente oficial de su ubicación |

Para los demás cruces que siguen sin nombre (`evidence/gate-01/2026-11-12/nombres-segunda-pasada.md`) no se ha buscado fuente: no estaban en el encargo.
