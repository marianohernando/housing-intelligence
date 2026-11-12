# Nombres de centros de salud, consultorios y hospitales: segunda pasada (HOSP-001 Fase 3, D-218 §9)

Generado el 12 nov con la base local tras `hi-ingest run ms_catalogo_nacional_hospitales`, `hi-ingest run ms_catalogo_centros_atencion_primaria` (parser `directory-1.1.0`, que guarda el municipio de cada entrada) y `hi-ingest run cm_centros_sanitarios` (parser `places-1.5.3`). Motivo: notas de C desde producción (un hospital de Fuencarral-El Pardo sin nombre ni camas, un «Hospital especializado · 50 camas» sin nombre en Chamartín y 44 «Centro de salud (Municipio)» genéricos).

El portal de la CM publicó hoy una versión nueva del registro de centros sanitarios (`ec0b4644…`, 3 centros menos en total). En centros de salud, consultorios, centros de salud mental y hospitales no cambia nada (tipo, dependencia, dirección y coordenadas, comparado registro a registro), así que las features no se recalculan.

## Resultado

| Tipo del registro | Con nombre antes | Con nombre ahora | Genéricos antes | Genéricos ahora |
|---|---|---|---|---|
| Centro de salud | 228 | 255 | 44 | 17 |
| Consultorio de atención primaria | 128 | 144 | 23 | 7 |
| Hospital general | 54 | 54 | 6 | 6 |
| Hospital especializado | 7 | 7 | 0 | 0 |
| Hospital de media y larga estancia | 8 | 8 | 0 | 0 |
| Hospital de salud mental y tratamiento de toxicomanías | 10 | 10 | 0 | 0 |

- Atención primaria: 399 de 423 cruzados, por método: {'direccion': 289, 'calle': 57, 'direccion_municipio': 25, 'codigo_postal': 27, 'municipio': 1}.
- Hospitales: 79 de 85 (sin cambios), por método: {'direccion': 64, 'calle': 13, 'direccion_municipio': 0, 'codigo_postal': 2, 'municipio': 0}.
- Ningún cruce anterior cambia de pareja (0). Se pierden 3: CS13070, CS21751, CS6706 (ver abajo). 5 cruces anteriores suben a una regla más fuerte con la misma pareja.

## Reglas nuevas (parser places-1.5.3)

1. **`direccion_municipio` (0,85):** mismo municipio, calle y número, en otro código postal. Las dos fuentes discrepan en el código postal en los bordes de los distritos (Cabo Machichaco 62: 28053 en el registro, 28018 en el catálogo). Único entre todas las entradas del municipio.
2. **`municipio` (0,6):** la única entrada del mismo tipo en el municipio. Sirve a los pueblos que comparten código postal con otros (28737, 28749, 28755).
3. **Veto de municipio:** por debajo de la dirección completa, un lugar y una entrada de municipios distintos nunca se cruzan (Madarcos y Robregordo comparten 28755 y los dos tienen «calle de las Eras»). La dirección completa (código postal, calle y número) basta aunque el catálogo archive el centro en el municipio de su área de salud: Aravaca (Madrid) figura en Pozuelo de Alarcón.
4. **El tipo tiene que coincidir por debajo de la dirección completa:** un consultorio en la misma calle que un centro de salud del catálogo no es ese centro.
5. **Grafías:** abreviaturas («Mª», «Ntra. Sra.»), singular y plural («América» y «Américas»), «bulevar», «callejón» y «carrera» como tipo de vía, el número pegado a «Nº» («Nº12»), esquinas («Zeus esq. Joaquín Blume» está en las dos calles) y la sustitución del catálogo de atención primaria, que escribe «CALLE» por cada «CL» y «AVENIDA» por cada «AV», también dentro de las palabras: «SAN CALLEAUDIO» (San Claudio), «VALLE INCALLEÁN», «ISLA DE JAVENIDAA», «AVENIDAILÉS», «CALLEFUENTESPINA». La calle del registro se compara también con esa misma sustitución; nunca se corrige el nombre publicado.

## Cruces nuevos

| Registro CM | Municipio | Dirección en el registro | Nombre | Dirección en el catálogo | Regla |
|---|---|---|---|---|---|
| CS0287 | Madrid | CALLE del Cabo Machichaco 62 (28053) | Centro de salud José María Llanos | CALLE CABO MACHICHACO, Nº 62 | `direccion_municipio` |
| CS0403 | Madrid | CALLE de San Claudio 154 (28038) | Centro de salud Rafael Alberti | CALLE SAN CALLEAUDIO, Nº 154 | `direccion` |
| CS0662 | Madrid | CALLE de Martínez de la Riva 57 (28053) | Centro de salud Martínez de la Riva | CALLE MARTÍNEZ DE LA RIVA, Nº 55-57 | `direccion_municipio` |
| CS0821 | Madrid | AVDA de Nuestra Señora de Fátima 93 (28025) | Centro de salud Ntra. Sra.de Fátima | AVENIDA DE NTRA SRA DE FÁTIMA, Nº 93 | `direccion_municipio` |
| CS1013 | Madrid | CALLE de Villalobos 16 (28018) | Centro de salud Campo de la Paloma | CALLE VILLALOBOS, Nº 16 | `direccion_municipio` |
| CS10284 | Torrejón de Ardoz | CALLE Joaquín Blume ESQUINA A (28850) | Centro de salud Los Fresnos | CALLE ZEUS, esq JOAQUÍN BLUME S/N | `calle` |
| CS10477 | Anchuelo | CALLE del Coso S/Nº (28818) | Consultorio local Anchuelo | AVENIDA DE LA PLAZA, Nº 2 | `codigo_postal` |
| CS12471 | Valdemanco | CALLE de las Eras 16 (28729) | Consultorio local Valdemanco | CALLE LAS HERAS, Nº 16 | `codigo_postal` |
| CS12644 | Lozoyuela-Navas-Sieteiglesias | PLAZA de la Constitución (Navas) 1 (28752) | Consultorio local Las Navas de Buitrago | PLAZA DE LA CONSTITUCIÓN, Nº 1 | `direccion_municipio` |
| CS12649 | Algete | AVDA del Guadalix 37 (28120) | Consultorio local Santo Domingo (Urbanización) | AVENIDA DE GUADALIX, Nº 27 | `municipio` |
| CS12763 | Montejo de la Sierra | CALLE Real 5 (28190) | Consultorio local Montejo de la Sierra | PLAZA MAYOR, Nº 1 | `codigo_postal` |
| CS13045 | Batres | CALLE los Secaderos 3 (28979) | Consultorio local Batres | CALLE SECADEROS, Nº 3 | `direccion_municipio` |
| CS13222 | Gascones | CALLE Huerto Pozancos 1 (28737) | Consultorio local Gascones | CALLE DESPENSA, Nº 7 | `codigo_postal` |
| CS13295 | Rascafría | CALLE Real 29 (28749) | Consultorio local Oteruelo | PLAZA DE LA PAZ, Nº 5 | `codigo_postal` |
| CS13403 | Piñuécar-Gandullas | PLAZA de la Sierra 1 (28738) | Consultorio local Gandullas | PLAZA DE LA SIERRA, Nº 1 | `direccion_municipio` |
| CS13707 | Leganés | CALLE María Ángeles López Gómez 2 (28915) | Centro de salud María Ángeles López | CALLE Mª ÁNGELES LÓPEZ GÓMEZ, Nº 2 | `direccion` |
| CS13991 | Madrid | CALLE de la Sierra de Alquife 8 (28053) | Centro de salud Vicente Soldevilla | CALLE SIERRA DE ALQUIFE, Nº 8 | `direccion_municipio` |
| CS18571 | Pinilla del Valle | PLAZA de la Constitución 21 (28749) | Consultorio local Pinilla del Valle | PLAZA DEL GOBERNADOR, Nº 1 | `codigo_postal` |
| CS22170 | Madarcos | CALLE de las Eras 23 (28755) | Consultorio local Madarcos | CALLE DE LA IGLESIA, Nº 1 | `codigo_postal` |
| CS22316 | Valdeavero | CALLE Castilla La Mancha 2 (28816) | Consultorio local Valdeavero | CALLE LA FUENTE, Nº 1 | `codigo_postal` |
| CS2260 | Madrid | CALLE de Fuentespina 2 (28031) | Centro de salud Cerro Almodóvar | CALLEFUENTESPINA, Nº 2 | `direccion` |
| CS4381 | Madrid | BULEV de Indalecio Prieto 26 (28032) | Centro de salud Valdebernardo | BULEVAR INDALECIO PRIETO, Nº 26 | `direccion` |
| CS5245 | Coslada | AVDA de Madrid 11 (28820) | Centro de salud Ciudad San Pablo | AVENIDA DE MADRID, Nº 9 - 11 | `direccion_municipio` |
| CS6082 | Madrid | CALLE de Valle Inclán 97 (28044) | Centro de salud Valle Inclán | CALLE VALLE INCALLEÁN, Nº 97 | `direccion` |
| CS6876 | Valdemoro | AVDA del Mar Mediterráneo 1 (28340) | Centro de salud El Restón | AVENIDA MAR MEDITERRÁNEO, Nº 1 | `direccion_municipio` |
| CS6878 | Madrid | CALLE de la Isla de Java c/v (28034) | Centro de salud Fuencarral | CALLE ISLA DE JAVENIDAA, S/N | `calle` |
| CS7256 | Villanueva de la Cañada | CALLE Valle de Baztán 4 (28691) | Consultorio local Villafranca del Castillo | CALLE VALLE DE BAZTÁN, Nº 4 | `direccion_municipio` |
| CS7343 | Parla | AVDA de América 6 (28981) | Centro de salud Las Américas | AVENIDA DE LAS AMÉRICAS, Nº 6 | `direccion_municipio` |
| CS7368 | Madrid | CALLE de la Palma 51 (28004) | Centro de salud Palma Norte | CALLE DE LA PALMA, Nº 51 | `direccion_municipio` |
| CS7380 | San Sebastián de los Reyes | CALLE del Real 91 (28700) | Centro de salud V Centenario | CALLE REAL, Nº 91 | `direccion_municipio` |
| CS7528 | Alcalá de Henares | AVDA Reyes Magos 12 (28806) | Centro de salud Reyes Magos | AVENIDA REYES MAGOS, Nº 12 | `direccion_municipio` |
| CS8428 | Majadahonda | CALLE Enrique Granados 2 (28222) | Centro de salud Valle de la Oliva | CALLE ENRIQUE GRANADOS, Nº 2 | `direccion_municipio` |
| CS8736 | San Sebastián de los Reyes | AVDA de Aragón 6 (28700) | Centro de salud Rosa de Luxemburgo | AVENIDA DE ARAGÓN, Nº 6 | `direccion_municipio` |
| CS8886 | Patones | CALLE de los Ingenieros Rafo y Rivera 1 (28189) | Consultorio local Patones | CALLE INGENIEROS RAFO Y RIBERA, Nº 1 | `codigo_postal` |
| CS9007 | Tres Cantos | SECT Oficios 12 (28760) | Centro de salud Tres Cantos I - Sector Oficios | CALLE SECTOR OFICIOS, Nº12 | `direccion` |
| CS9013 | Móstoles | AVDA Olímpica 38 (28933) | Centro de salud El Soto | AVENIDA OLÍMPICA, Nº 38 | `direccion_municipio` |
| CS9043 | Robregordo | CALLE de las Eras 16 (28755) | Consultorio local Robregordo | CALLE DE LAS ERAS, Nº 19 | `calle` |
| CS9144 | Leganés | CALLE Jesús Miguel Haddad Blanco 2 (28914) | Centro de salud María Jesús Hereza | CALLE JESÚS MIGUEL HADDAD BLANCO, Nº 2 | `direccion_municipio` |
| CS9166 | Venturada | CALLE de la Venta 22 (28728) | Consultorio local Venturada | CALLE DE LA VENTA, Nº 22 | `direccion_municipio` |
| CS9240 | Leganés | CALLE Isabel la Católica 1 (28914) | Centro de salud Santa Isabel | CALLE ISABEL LA CATÓLICA, Nº 1 | `direccion_municipio` |
| CS9336 | Fuenlabrada | CALLE de Avilés 2 (28942) | Centro de salud El Naranjo | CALLE AVENIDAILÉS, Nº 2 | `direccion` |
| CS9361 | Leganés | AVDA Europa 1 (28915) | Centro de salud Jaime Vera - Leganés | AVENIDA DE EUROPA, Nº 1 | `direccion_municipio` |
| CS9558 | Alcorcón | CALLE de las Palmeras 3 (28922) | Centro de salud La Rivota | CALLE LAS PALMERAS, Nº 3 | `direccion_municipio` |
| CS9655 | Madrid | CRA de San Jerónimo 32 (28014) | Centro de salud Cortes | CALLE CARRERA SAN JERÓNIMO, Nº 32 | `direccion_municipio` |
| CS9656 | Fuenlabrada | CALLE Teruel 4 (28941) | Centro de salud Castilla la Nueva | CALLE TERUEL, Nº 4 | `direccion_municipio` |
| CS9855 | Pezuela de las Torres | CALLE de la Ronda 6 (28812) | Consultorio local Pezuela de las Torres | CALLE LA RONDA, Nº 6 | `codigo_postal` |

## Cruces que se pierden

- **CS13070** (CALLE Fábrica 6 (28514)) el registro lo da como centro de salud y el catálogo como consultorio local (Nuevo Baztán), y solo coincidían en la calle: por debajo de la dirección completa el tipo tiene que coincidir. Conserva «Centro de salud (Nuevo Baztán)».
- **CS21751** (CALLE Planeta Venus 24 (28983)) tenía «Centro de salud Las Américas» solo por ser el único centro de salud de su código postal. La dirección del catálogo para ese centro (Avenida de las Américas 6) es la de **CS7343** («Avda de América 6», en otro código postal), que ahora lo toma por `direccion_municipio`: la dirección pesa más que compartir código postal.
- **CS6706** (CALLE de la Palma 54 (28015)) es un consultorio en Palma 54 (esquina a Norte 19) que tomaba «Palma Norte» por estar en la misma calle y código postal. El catálogo sitúa ese centro de salud en Palma 51, que es la dirección de **CS7368**, un centro de salud del registro: ahora lo toma él (`direccion_municipio`). Por debajo de la dirección completa el tipo tiene que coincidir.

## Lo que sigue sin nombre y por qué

| Registro CM | Tipo | Municipio | Dirección en el registro | Motivo |
|---|---|---|---|---|
| CH0049 | Hospital general | Madrid | CTRA de Colmenar Viejo KM.9,1 (28034) | **Hospital Universitario Ramón y Cajal** (Fuencarral-El Pardo): el catálogo lo sitúa en «Calle de Ayala 38, 28001» y el registro en la carretera de Colmenar Viejo, km 9,1 (28034). Ninguna regla de dirección los une; solo un fichero de correcciones con fuente oficial (decisión pendiente de Mariano) |
| CH0068 | Hospital general | Madrid | CALLE del Príncipe de Vergara 53 (28006) | no unique entry among 3 in postal code 28006 |
| CH0120 | Hospital general | Madrid | CALLE de Gustavo Pérez Puig 66 (28055) | no unique entry among 1 in postal code 28055 |
| CH0121 | Hospital general | Tres Cantos | CALLE de Santiago Ramón y Cajal 23 (28760) | no entry in postal code 28760 |
| CH0122 | Hospital general | Pozuelo de Alarcón | PASEO de la Casa de Campo 5 (28223) | no unique entry among 1 in postal code 28223 |
| CH0123 | Hospital general | Boadilla del Monte | CMNO Alto de Madrid 21 (28660) | no unique entry among 1 in postal code 28660 |
| CS0177 | Centro de salud | Rozas de Madrid, Las | CALLE Principado de Asturias 30 (28230) | no entry in postal code 28230 |
| CS0293 | Centro de salud | Madrid | CALLE de Pedroches 4 (28053) | no entry in postal code 28053 |
| CS0597 | Centro de salud | Madrid | CALLE de la Guayaba S/N (28044) | no unique entry among 3 in postal code 28044 |
| CS1140 | Centro de salud | Madrid | CALLE de O'Donnell 55 (28009) | dos registros de la CM en O'Donnell 55 (CS1140 y CS21856) reclaman el mismo centro (Goya) |
| CS1178 | Centro de salud | San Sebastián de los Reyes | CALLE Federico García Lorca 3 (28701) | no unique entry among 1 in postal code 28701 |
| CS12726 | Consultorio de atención primaria | Piñuécar-Gandullas | CALLE Carretera s/n (28737) | no unique entry among 5 in postal code 28737 |
| CS13070 | Centro de salud | Nuevo Baztán | CALLE Fábrica 6 (28514) | no unique entry among 1 in postal code 28514 |
| CS13396 | Consultorio de atención primaria | Navarredonda y San Mamés | CALLE de la Fuente Vieja 13 (28739) | no unique entry among 5 in postal code 28739 |
| CS17064 | Centro de salud | Madrid | CALLE de Andrés Mellado 37 (28015) | el registro lo da como «Privado Benéfico (Cruz Roja)» y el catálogo como gestión pública directa (Andrés Mellado): el veto público/privado no lo cruza |
| CS1832 | Centro de salud | Madrid | AVDA de las Águilas 18 (28044) | no unique entry among 3 in postal code 28044 |
| CS20540 | Consultorio de atención primaria | Collado Villalba | CALLE Espinarejo 2 (28400) | no unique entry among 3 in postal code 28400 |
| CS21751 | Centro de salud | Parla | CALLE Planeta Venus 24 (28983) | no unique entry among 1 in postal code 28983 |
| CS21829 | Centro de salud | Madrid | CALLE de Lagasca 122 (28006) | el catálogo publica «Lagasca» sin código (CODIGO_CCN vacío): en cuarentena en el directorio |
| CS21856 | Centro de salud | Madrid | CALLE de O'Donnell 55 (28009) | dos registros de la CM en O'Donnell 55 (CS1140 y CS21856) reclaman el mismo centro (Goya) |
| CS22326 | Centro de salud | Móstoles | AVDA de la Vía Láctea SN (28938) | no unique entry among 1 in postal code 28938 |
| CS22404 | Centro de salud | Madrid | CALLE de Las Camas 1 (28021) | no unique entry among 4 in postal code 28021 |
| CS22480 | Centro de salud | Madrid | CALLE de Ramos Carrión 10 (28002) | no unique entry among 4 in postal code 28002 |
| CS6706 | Consultorio de atención primaria | Madrid | CALLE de la Palma 54 (28015) | no unique entry among 3 in postal code 28015 |
| CS7366 | Consultorio de atención primaria | Santa María de la Alameda | CALLE Buenavista 7 (28296) | no unique entry among 3 in postal code 28296 |
| CS8138 | Consultorio de atención primaria | Madrid | CALLE de Bravo Murillo 317 (28039) | no unique entry among 2 in postal code 28039 |
| CS8139 | Centro de salud | Alcobendas | CALLE de Blas de Otero 13 (28100) | no unique entry among 4 in postal code 28100 |
| CS8737 | Centro de salud | Colmenar Viejo | CALLE del Doctor Cecilio de la Morena S/N (28770) | no unique entry among 2 in postal code 28770 |
| CS9145 | Centro de salud | Leganés | PLAZA Comunidad de Madrid S/N (28914) | no unique entry among 1 in postal code 28914 |
| CS9208 | Consultorio de atención primaria | Valdeolmos-Alalpardo | CALLE San Sebastián 3 (28130) | no unique entry among 2 in postal code 28130 |

## Nombres del catálogo de hospitales que no se usan (empresa u operador, D-218 §5)

| Registro CM | Publicado en el catálogo | Camas |
|---|---|---|
| CH0103 | Casta Guadarrama | 157.0 |
| CH0105 | ID Dalud Móstoles Sa | 362.0 |
| CH0113 | Fraternidad Muprespa, Mutua Colaboradora Con La Seguridad Social Nº 275 | 50.0 |
| CH0117 | HM Hospitales 1.989, S.A. | 51.0 |
| CH0118 | Alm Univass S.L. | 39.0 |
| CH0119 | HM Hospitales 1989, S.A. | 90.0 |

**CH0113** es el «Hospital especializado · 50 camas» de Chamartín (paseo de la Habana 83): el catálogo publica como nombre el de la mutua que lo gestiona («Fraternidad Muprespa, Mutua Colaboradora con la Seguridad Social nº 275»), no el del centro. Por D-218 §5 no se muestra como nombre ni se inventa otro; sí muestra sus camas y `dependency: privada` (una mutua solo atiende accidentes de trabajo de sus afiliados).
