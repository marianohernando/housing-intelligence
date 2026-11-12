# Hospitales: nombre y camas desde el Catálogo Nacional de Hospitales (D-218)

Generado el 12 nov con la base local tras `hi-ingest run ms_catalogo_nacional_hospitales` y `hi-ingest run cm_centros_sanitarios` (parser places-1.3.1, reglas endurecidas tras la revisión: mismas palabras de calle, veto público/privado, unicidad entre todo el código postal; los mismos 79 pares que con 1.3.0).

- Versión del catálogo: `2026-11-12-e5148a11b523` · hospitales de la provincia en el catálogo: 91
- Hospitales del registro de la CM: 85 · cruzados: **79** · por método: {'direccion': 64, 'calle': 13, 'codigo_postal': 2}
- Uno a uno: True ({'reused': 0})
- Público/privado, registro CM frente a catálogo: {'compared': 79, 'disagree': 0}

## Hospitales del registro sin cruzar (conservan «Hospital general (Municipio)», sin camas)

| Registro CM | Tipo | Motivo |
|---|---|---|
| CH0049 | Hospital general | no unique entry among 1 in postal code 28034 |
| CH0068 | Hospital general | no unique entry among 3 in postal code 28006 |
| CH0120 | Hospital general | no unique entry among 1 in postal code 28055 |
| CH0121 | Hospital general | no entry in postal code 28760 |
| CH0122 | Hospital general | no unique entry among 1 in postal code 28223 |
| CH0123 | Hospital general | no unique entry among 1 in postal code 28660 |

## Nombres del catálogo que no se usan (empresa u operador, no el centro)

| Registro CM | Publicado en el catálogo |
|---|---|
| CH0103 | Casta Guadarrama |
| CH0105 | ID Dalud Móstoles Sa |
| CH0113 | Fraternidad Muprespa, Mutua Colaboradora Con La Seguridad Social Nº 275 |
| CH0117 | HM Hospitales 1.989, S.A. |
| CH0118 | Alm Univass S.L. |
| CH0119 | HM Hospitales 1989, S.A. |

## Hospitales del catálogo sin lugar en el registro

Los 9 «Otros centros con internamiento» no son hospitales en el registro de la CM; el Gómez Ulla (Defensa) no figura en él.

| CODCNH | Nombre | Clase |
|---|---|---|
| 281371 | Hospital HM Valles | Otros Centros con Internamiento |
| 280783 | Centro San Juan de Dios Ciempozuelos | Otros Centros con Internamiento |
| 281034 | Clínica Isadora S.A. | Otros Centros con Internamiento |
| 280376 | Hospital Viamed Santa Elena, S.L | Otros Centros con Internamiento |
| 280344 | Hospital de La V.O.T. de San Francisco de Asís | Otros Centros con Internamiento |
| 280323 | Sanatorio Nuestra Señora del Rosario | Hospitales Generales |
| 280724 | Hospital Central de La Defensa Gómez Ulla | Hospitales Generales |
| 280029 | Hospital Universitario Ramon y Cajal | Hospitales Generales |
| 280210 | Hospital de Cantoblanco | Otros Centros con Internamiento |
| 280164 | Hospital Carlos III | Otros Centros con Internamiento |
| 281445 | Servicio Madrileño de Salud | Otros Centros con Internamiento |
| 280148 | Hospital Central de La Cruz Roja, San José y Santa Adela | Otros Centros con Internamiento |

## Los 10 hospitales con más camas instaladas (como sale en `/places`)

| Nombre | Municipio | Camas | Dependencia | Cruce |
|---|---|---|---|---|
| Hospital Universitario 12 de Octubre | 28079 | 1161 | publica | codigo_postal |
| Hospital General Universitario Gregorio Marañón | 28079 | 1140 | publica | direccion |
| Hospital Universitario La Paz | 28079 | 966 | publica | direccion |
| Hospital Universitario Clínico San Carlos | 28079 | 861 | publica | calle |
| Hospital Universitario Fundacion Jimenez Diaz | 28079 | 651 | privada | direccion |
| Hospital Universitario Puerta de Hierro Majadahonda | 28080 | 613 | publica | direccion |
| Hospital Universitario de Getafe | 28065 | 543 | publica | calle |
| Hospital Universitario de La Princesa | 28079 | 524 | publica | direccion |
| Hospital Universitario Príncipe de Asturias | 28005 | 507 | publica | calle |
| Hospital Universitario de Fuenlabrada | 28058 | 413 | publica | direccion |
