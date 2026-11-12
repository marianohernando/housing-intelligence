# Nombres con tilde con fuente oficial (D-221)

Petición de `datamad-10` (12 nov): el Ramón y Cajal (CH0049) salía «Hospital Universitario Ramon y Cajal», como lo publica el Catálogo Nacional de Hospitales. Generado con la base local tras `hi-ingest run cm_centros_sanitarios` (parser `places-1.7.0`, versión `2026-11-12-6f1013c9c79d`, 553 lugares, calidad en verde).

- Antes: `nombres-tildes-antes.md` (`uv run python scripts/audit_name_accents.py`, con la carga anterior).
- Después: `nombres-tildes-auditoria.md` (el mismo comando tras la carga).

## Cómo se buscaron

1. **Automático** (`scripts/audit_name_accents.py`): los 483 lugares de salud con nombre de un catálogo del Ministerio. Una palabra es candidata si los datos oficiales ya cargados (municipios, distritos y barrios; registros de la CM de colegios y centros sociales; paradas del CRTM: 1.021 palabras con tilde o eñe) la escriben con tilde o eñe, o si termina en «-cion»/«-sion». Salen 15 candidatos.
2. **A mano:** los 313 nombres de atención primaria sin ninguna tilde y los de los 85 hospitales del registro. Añade «Pedro Lain Entralgo» y las tres «Quironsalud».
3. **Fuente por registro** (D-212, D-218 §10): nunca de memoria. Primero el BOCM, que en las órdenes de renovación de autorizaciones lista cada centro por su número de registro; si no, la página del centro en comunidad.madrid con la misma dirección; si no, otro texto del BOCM con el mismo domicilio.

## Corregidos (11)

| Registro | Publicado por el catálogo | Ahora | Fuente (consultada el 12 nov) |
|---|---|---|---|
| CH0049 | Hospital Universitario Ramon y Cajal | Hospital Universitario Ramón y Cajal | Página del hospital en comunidad.madrid (la misma de su corrección de directorio) |
| CH0080 | Hospital Universitario Fundacion Alcorcón | Hospital Universitario Fundación Alcorcón | BOCM 27/12/2022, Orden 1903/2022: «CH0080. Hospital Universitario Fundación Alcorcón» |
| CH0028 | Hospital de La Fuenfria | Hospital La Fuenfría | BOCM 08/11/2023, Orden 1574/2023: «CH0028. Hospital La Fuenfría» |
| CH0046 | Hospital Psiquiátrico Doctor Rodriguez Lafora | Hospital Psiquiátrico Doctor Rodríguez Lafora | BOCM 08/11/2023, Orden 1574/2023: «CH0046. …» |
| CH0011 | Hospital Universitario Fundacion Jimenez Diaz | Hospital Universitario Fundación Jiménez Díaz | comunidad.madrid/centros, misma dirección (Reyes Católicos 2, 28040) |
| CH0097 | Hospital Universitario Infanta Sofia | Hospital Universitario Infanta Sofía | comunidad.madrid/centros, misma dirección (paseo de Europa 34, 28702) |
| CH0024 | Hospital Beata Maria Ana | Hospital Beata María Ana | BOCM 06/05/2014, Decreto 53/2014 (Placa de Oro al hospital de las Hermanas Hospitalarias en Madrid) |
| CH0038 | Fundacion Instituto San José | Fundación Instituto San José | BOCM 13/06/2022, adenda al convenio con el SERMAS (mismo domicilio: Pinar de San José 98, 28054) |
| CS8694 | Centro de salud Lavapies | Centro de salud Lavapiés | BOCM 16/02/2026, Orden 123/2026: «CS8694.- Centro de Salud Lavapiés» |
| CS9335 | Centro de salud Pedro Lain Entralgo | Centro de salud Dr. Pedro Laín Entralgo | BOCM 09/12/2025, Orden 1777/2025: «CS9335.- Centro de Salud Dr. Pedro Laín Entralgo» |
| CS12162 | Centro de salud Infante Luis de Borbon | Consultorio Infante Don Luis de Borbón | comunidad.madrid/centros, misma dirección (Secundino Zuazo 6, 28660) |

Las URL completas y el texto exacto de cada fuente están en `data/catalog/corrections/places.yaml`. Cada lugar guarda en `attributes.correction` el tipo (`name`; `directory+name` en CH0049), la fuente y `previous_name`; `attributes.directory.name` sigue con el nombre del catálogo. Camas y cruces sin cambios (los 10 nuevos ya estaban cruzados por dirección completa o calle).

Base local: `select count(*) from place_master where attributes ? 'correction'` → 15 (5 de antes + 10); `… where attributes->'correction' ? 'previous_name'` → 11.

## Sin corregir, declarados

| Registro | Nombre | Por qué |
|---|---|---|
| CH0013 | Hospital HM Nuevo Belen | Hospital privado; ninguna fuente pública oficial lo nombra (solo la web del grupo y prensa) |
| CH0081 | Hospital Universitario HM Monteprincipe | Igual |
| CH0071, CH0084, CH0091 | Hospital Quironsalud San José, Sur y Madrid | «Quirónsalud» es una marca comercial; ninguna fuente oficial encontrada |
| CS12650 | Consultorio local Belvis del Jarama | La CM también escribe «Belvis de Jarama» (comunidad.madrid/centros/consultorio-belvis-jarama): no hay tilde que recuperar |
| CS9655 | Centro de salud Cortes | Barrio de Cortes: sin tilde (falso positivo de «Cortés») |
| CS2225 | Centro de salud Canal de Panamá | Falso positivo de «cañal» |

No se tocan otras diferencias con la CM que no son tildes («Hospital General de Villalba» frente a «Hospital Universitario General de Villalba»), ni el tipo del registro (D-221 §5).
