# Centros de salud y consultorios: nombre desde el Catálogo de Centros de Atención Primaria (D-218 §8)

Generado el 12 nov con la base local tras `hi-ingest run ms_catalogo_centros_atencion_primaria` y `hi-ingest run cm_centros_sanitarios` (parser places-1.4.0).

- Versión del catálogo: `2026-11-12-260312fa3bc8` · entradas de la provincia: 419 (1 fila sin código, en cuarentena)
- Centros de salud y consultorios del registro de la CM: 423 · con nombre: **356** · por método: {'direccion': 278, 'calle': 55, 'codigo_postal': 23}
- Uno a uno: True · público/privado (hospitales y atención primaria): {'compared': 435, 'disagree': 0}

## Cruces solo por código postal (0,7): el único centro de ese tipo en el código postal

| Registro CM | Municipio | Dirección en el registro | Nombre | Dirección en el catálogo |
|---|---|---|---|---|
| CS0507 | Algete | de Valdeamor S/N | Centro de salud Algete | CALLE VALDEAMOR, esquina CALLE CARRACHEL, Nº 1 |
| CS11513 | Estremera | de Don José Maestro Martínez S/Nº | Consultorio local Estremera | CALLE DOCTOR JOSÉ MAESTRO MARTÍNEZ, Nº 1 |
| CS11604 | Arganda del Rey | Monte Alegre 11 | Consultorio local La Poveda | CALLE MONTEALEGRE, Nº 11 |
| CS12472 | Berrueco, El | de los Huertos 15 | Consultorio local El Berrueco | CALLEJÓN DE LOS HUERTOS, Nº 15 |
| CS12762 | Canencia | de José Luis Muñiz Toca 5 | Consultorio local Canencia | PLAZA DE LA CONSTITUCIÓN, Nº 1 |
| CS13267 | Alcobendas | de Salvador Allende 22 | Centro de salud Arroyo de la Vega | BULEVAR SALVADOR ALLENDE, Nº 22 |
| CS13706 | Arroyomolinos | de Marbella S/N | Consultorio local Arroyomolinos | CALLE MARBELA, S/N |
| CS21751 | Parla | Planeta Venus 24 | Centro de salud Las Américas | AVENIDA DE LAS AMÉRICAS, Nº 6 |
| CS5244 | Coslada | de los Príncipes de España 30 | Centro de salud Valleaguado | AVENIDA PRÍNCIPE DE ESPAÑA, Nº 30 |
| CS6850 | Boalo, El | de la Peña Hoyuela 17 | Consultorio local El Boalo | CALLE DE LA PEÑA, Nº 17 |
| CS7249 | Villanueva del Pardillo | Río Perales 2 | Consultorio local Villanueva del Pardillo | CALLE RÍO TAJUÑA, Nº 2 |
| CS7255 | Robledo de Chavela | de Miguel de Unamuno 1 | Centro de salud Robledo de Chavela | CARRETERA NAVAS DEL REY, Nº 4 |
| CS7374 | Valdemaqueda | Dos de Mayo 37 | Consultorio local Valdemaqueda | TRAVESÍA 2 DE MAYO, Nº 37 |
| CS7465 | Boadilla del Monte | de Ronda 10 | Centro de salud Condes de Barcelona | CALLE RONDA, Nº 10 |
| CS8447 | Valdelaguna | M-315 (Colmenar de Oreja) S/N | Consultorio local Valdelaguna | CALLE JOSÉ ANTONIO, Nº 12 |
| CS8640 | Madrid | de Cincovillas 1 | Centro de salud Ensanche de Vallecas | CALLE CINCO VILLAS, Nº 1 |
| CS8715 | Rascafría | de la Rivera del Artiñuelo 2 | Centro de salud Rascafría | CALLE RIBERA DE ARTIÑUELO, Nº 2 |
| CS8906 | Ajalvir | Fuente 28-30 | Consultorio local Ajalvir | AVENIDA LAS AGUAS, Nº 2 |
| CS9039 | Fuente el Saz de Jarama | Almendralejos 11 | Consultorio local Fuente el Saz | CALLE ALMEDRALEJOS, Nº 11 |
| CS9304 | Soto del Real | Cristal 2 | Centro de salud Soto del Real | CALLE CRISTAL, Nº 2 -URBANIZACIÓN LA RETAMILLA |
| CS9362 | Fuenlabrada | de Francia 38 | Centro de salud Francia | CALLE FRANCIA, Nº 38 POSTERIOR |
| CS9550 | Cadalso de los Vidrios | Francisco Caballero C/VDOCTOR MENENDEZ | Centro de salud Cadalso de los Vidrios | CALLE DOCTOR MENÉNDEZ, Nº 5 |
| CS9877 | Morata de Tajuña | de la Clínica 4 | Consultorio local Morata de Tajuña | CALLE CALLEÍNICA, Nº 4 |

## Centros del registro sin nombre (conservan «Centro de salud (Municipio)»)

| Registro CM | Tipo | Motivo |
|---|---|---|
| CS0177 | Centro de salud | no entry in postal code 28230 |
| CS0287 | Centro de salud | no entry in postal code 28053 |
| CS0293 | Centro de salud | no entry in postal code 28053 |
| CS0403 | Centro de salud | no unique entry among 6 in postal code 28038 |
| CS0597 | Centro de salud | no unique entry among 3 in postal code 28044 |
| CS0662 | Centro de salud | no entry in postal code 28053 |
| CS0821 | Centro de salud | no unique entry among 2 in postal code 28025 |
| CS1013 | Centro de salud | no unique entry among 6 in postal code 28018 |
| CS10284 | Centro de salud | no unique entry among 6 in postal code 28850 |
| CS10477 | Consultorio de atención primaria | no unique entry among 2 in postal code 28818 |
| CS1140 | Centro de salud | ambiguous: 2 places claim 1328001985 |
| CS1178 | Centro de salud | no unique entry among 1 in postal code 28701 |
| CS12471 | Consultorio de atención primaria | no unique entry among 4 in postal code 28729 |
| CS12644 | Consultorio de atención primaria | no unique entry among 1 in postal code 28752 |
| CS12649 | Consultorio de atención primaria | no entry in postal code 28120 |
| CS12726 | Consultorio de atención primaria | no unique entry among 5 in postal code 28737 |
| CS12763 | Consultorio de atención primaria | no unique entry among 2 in postal code 28190 |
| CS13045 | Consultorio de atención primaria | no unique entry among 1 in postal code 28979 |
| CS13222 | Consultorio de atención primaria | no unique entry among 5 in postal code 28737 |
| CS13295 | Consultorio de atención primaria | no unique entry among 5 in postal code 28749 |
| CS13396 | Consultorio de atención primaria | no unique entry among 5 in postal code 28739 |
| CS13403 | Consultorio de atención primaria | no entry in postal code 28738 |
| CS13707 | Centro de salud | ambiguous: 2 places claim 1328018171 |
| CS13991 | Centro de salud | no entry in postal code 28053 |
| CS17064 | Centro de salud | no unique entry among 3 in postal code 28015 |
| CS1832 | Centro de salud | no unique entry among 3 in postal code 28044 |
| CS18571 | Consultorio de atención primaria | no unique entry among 5 in postal code 28749 |
| CS20540 | Consultorio de atención primaria | no unique entry among 3 in postal code 28400 |
| CS21829 | Centro de salud | no unique entry among 1 in postal code 28006 |
| CS21856 | Centro de salud | ambiguous: 2 places claim 1328001985 |
| CS22170 | Consultorio de atención primaria | ambiguous: 2 places claim 1328008948 |
| CS22316 | Consultorio de atención primaria | no unique entry among 2 in postal code 28816 |
| CS22326 | Centro de salud | no unique entry among 1 in postal code 28938 |
| CS22404 | Centro de salud | no unique entry among 4 in postal code 28021 |
| CS22480 | Centro de salud | no unique entry among 4 in postal code 28002 |
| CS2260 | Centro de salud | no unique entry among 2 in postal code 28031 |
| CS4381 | Centro de salud | no unique entry among 4 in postal code 28032 |
| CS5245 | Centro de salud | no entry in postal code 28820 |
| CS6082 | Centro de salud | no unique entry among 3 in postal code 28044 |
| CS6876 | Centro de salud | no entry in postal code 28340 |
| CS6878 | Centro de salud | no unique entry among 3 in postal code 28034 |
| CS7256 | Consultorio de atención primaria | no unique entry among 1 in postal code 28691 |
| CS7343 | Centro de salud | no unique entry among 1 in postal code 28981 |
| CS7366 | Consultorio de atención primaria | no unique entry among 3 in postal code 28296 |
| CS7368 | Centro de salud | no unique entry among 1 in postal code 28004 |
| CS7380 | Centro de salud | no entry in postal code 28700 |
| CS7528 | Centro de salud | no unique entry among 1 in postal code 28806 |
| CS8138 | Consultorio de atención primaria | no unique entry among 2 in postal code 28039 |
| CS8139 | Centro de salud | no unique entry among 4 in postal code 28100 |
| CS8428 | Centro de salud | no entry in postal code 28222 |
| CS8736 | Centro de salud | no entry in postal code 28700 |
| CS8737 | Centro de salud | no unique entry among 2 in postal code 28770 |
| CS8886 | Consultorio de atención primaria | no unique entry among 3 in postal code 28189 |
| CS9007 | Centro de salud | no unique entry among 2 in postal code 28760 |
| CS9013 | Centro de salud | no unique entry among 1 in postal code 28933 |
| CS9043 | Consultorio de atención primaria | ambiguous: 2 places claim 1328008948 |
| CS9144 | Centro de salud | no unique entry among 1 in postal code 28914 |
| CS9145 | Centro de salud | no unique entry among 1 in postal code 28914 |
| CS9166 | Consultorio de atención primaria | no entry in postal code 28728 |
| CS9208 | Consultorio de atención primaria | no unique entry among 2 in postal code 28130 |
| CS9240 | Centro de salud | no unique entry among 1 in postal code 28914 |
| CS9336 | Centro de salud | no unique entry among 3 in postal code 28942 |
| CS9361 | Centro de salud | ambiguous: 2 places claim 1328018171 |
| CS9558 | Centro de salud | no unique entry among 2 in postal code 28922 |
| CS9655 | Centro de salud | no unique entry among 1 in postal code 28014 |
| CS9656 | Centro de salud | no entry in postal code 28941 |
| CS9855 | Consultorio de atención primaria | no unique entry among 2 in postal code 28812 |
