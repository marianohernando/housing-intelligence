# DATA-020 · Seguridad: evaluación de la fuente candidata (D-224)

Fecha: 2026-11-12. Línea A. Solo lectura de la fuente; no se ha cargado nada en la base.

## Fuente
- Portal de datos abiertos de la Comunidad de Madrid: «Hechos conocidos de infracciones penales por tipología en municipios mayores de 20.000 habitantes por municipio» (`hechos_conocidos_penales_por_tipologia_municipios_mayores_20000_por_municipio`), CC BY 4.0. Fuente según la ficha: «Estadísticas de Criminalidad. Ministerio del Interior». Actualizada el 05-10-2026.
- Definición de la ficha: «Hechos conocidos: Se entienden el conjunto de infracciones penales y administrativas, que han sido conocidas por las distintas Fuerzas y Cuerpos de Seguridad, bien por medio de denuncia interpuesta o por actuación policial realizada motu proprio».
- CSV de 5.280 filas: `Año;Concepto;Tipo territorio;Código territorio;Territorio;Municipio;Valor;Unidad;Estado dato`. Años 2016–2025; 2025 está marcado «Provisional». 37 municipios, solo por nombre: no trae código INE. 15 conceptos por municipio y año (total, cibercriminalidad, hurtos, robos, lesiones, delitos sexuales, homicidios, etc.).
- **Sin características de personas:** no trae nacionalidad, sexo ni edad. Cumple CLAUDE.md §11 (oficial y agregado) y no le aplica el motivo de descarte de D-205.

## Tasa de 2024 (último año no provisional)
Criminalidad convencional (total menos cibercriminalidad, que no ocurre en un sitio) por 1.000 habitantes del padrón de 2024 (`poblacion_censada`, ya cargada). Los 37 nombres casan con su municipio. Referencia (los 37 juntos): **47,9**. Es un cálculo de evaluación con el CSV descargado el 12 nov y el padrón de la base local. No hay pipeline y no se versiona ningún script.

    Tres Cantos                  28903 conv/1000=20.7 total=1612 ciber=519.0 pop=52825
    Boadilla del Monte           28022 conv/1000=21.4 total=2319 ciber=918.0 pop=65528
    Pozuelo de Alarcón           28115 conv/1000=21.6 total=2339 ciber=417.0 pop=89123
    Fuenlabrada                  28058 conv/1000=22.9 total=5964 ciber=1610.0 pop=190496
    Paracuellos de Jarama        28104 conv/1000=23.4 total=1047 ciber=410.0 pop=27241
    Algete                       28009 conv/1000=28.2 total=870 ciber=275.0 pop=21134
    Villanueva de la Cañada      28176 conv/1000=30.1 total=943 ciber=230.0 pop=23714
    Torrejón de Ardoz            28148 conv/1000=30.8 total=5231 ciber=884.0 pop=141047
    Torrelodones                 28152 conv/1000=30.9 total=1177 ciber=396.0 pop=25250
    Móstoles                     28092 conv/1000=31.1 total=8580 ciber=1958.0 pop=213268
    Rozas de Madrid              28127 conv/1000=32.8 total=4629 ciber=1373.0 pop=99193
    Villaviciosa de Odón         28181 conv/1000=33.1 total=1312 ciber=341.0 pop=29294
    Colmenar Viejo               28045 conv/1000=33.3 total=2477 ciber=584.0 pop=56878
    Alcorcón                     28007 conv/1000=33.9 total=6970 ciber=1049.0 pop=174740
    Navalcarnero                 28096 conv/1000=34.1 total=1505 ciber=391.0 pop=32684
    Alcobendas                   28006 conv/1000=34.2 total=5428 ciber=1275.0 pop=121446
    Coslada                      28049 conv/1000=35.9 total=3525 ciber=625.0 pop=80688
    San Fernando de Henares      28130 conv/1000=36.0 total=1711 ciber=308.0 pop=38969
    Galapagar                    28061 conv/1000=36.1 total=1821 ciber=518.0 pop=36112
    Mejorada del Campo           28084 conv/1000=36.4 total=1221 ciber=324.0 pop=24632
    Aranjuez                     28013 conv/1000=36.8 total=2816 ciber=518.0 pop=62508
    San Martín de la Vega        28132 conv/1000=37.0 total=1044 ciber=280.0 pop=20664
    San Sebastián de los Reyes   28134 conv/1000=37.3 total=4391 ciber=854.0 pop=94942
    Alcalá de Henares            28005 conv/1000=37.8 total=9752 ciber=2199.0 pop=199804
    Getafe                       28065 conv/1000=38.0 total=8983 ciber=1702.0 pop=191560
    Leganés                      28074 conv/1000=39.3 total=9008 ciber=1387.0 pop=193934
    Valdemoro                    28161 conv/1000=39.3 total=4287 ciber=1001.0 pop=83582
    Pinto                        28113 conv/1000=39.5 total=3024 ciber=815.0 pop=55989
    Rivas-Vaciamadrid            28123 conv/1000=39.7 total=5312 ciber=1279.0 pop=101637
    Collado Villalba             28047 conv/1000=40.4 total=3333 ciber=613.0 pop=67323
    Ciempozuelos                 28040 conv/1000=42.3 total=1456 ciber=354.0 pop=26046
    Arganda del Rey              28014 conv/1000=45.7 total=3423 ciber=718.0 pop=59209
    Parla                        28106 conv/1000=47.7 total=7682 ciber=1246.0 pop=134876
    Majadahonda                  28080 conv/1000=48.3 total=4731 ciber=1180.0 pop=73547
    Arroyomolinos                28015 conv/1000=52.0 total=2448 ciber=508.0 pop=37299
    Madrid                       28079 conv/1000=58.6 total=237020 ciber=36591.0 pop=3422416
    Humanes de Madrid            28073 conv/1000=116.2 total=2635 ciber=305.0 pop=20054

## Por qué no entra en el buscador
1. **El denominador no es quien está en la zona.** Es la población empadronada, pero los hechos se cuentan donde se denuncian o donde actúa la policía. Las zonas con mucha actividad y poca población salen muy altas. Humanes de Madrid, con unos 20.000 vecinos, da 116,2: 2,4 veces la referencia. Madrid capital, que cada día recibe a quien trabaja allí o la visita, da 58,6. El padrón no cuenta a esas personas. Una tasa así no mide la seguridad del sitio donde se vive, y ordenar zonas con ella señalaría municipios por su actividad económica.
2. **Cobertura.** Solo hay 36 de las 199 zonas del buscador. Las 142 de menos de 20.000 habitantes quedan SIN DATOS, y también los 21 distritos de Madrid: la fuente da la ciudad entera, y repartir esa tasa entre los distritos supondría barrios homogéneos (§11). Las actuaciones de la Policía Municipal por distrito (D-205) son otra medida y no se pueden comparar con esta.
3. **Modelo y producto.** Convertir la tasa en un % de encaje exige una curva sobre un dato sensible. Es una decisión de modelo y de producto (CLAUDE.md §4) y no se cierra sin Mariano.

## Qué queda
- La prioridad «Seguridad» sigue diciendo «Seguridad: aún sin datos oficiales». Nunca puntúa 0 y nunca pone etiquetas.
- Opción para Mariano: enseñar la tasa como dato de contexto en la vista de zona, solo en los 36 municipios. Iría con la cifra absoluta, la referencia, el año y el aviso del denominador. No puntuaría ni ordenaría zonas. Sin decisión, no se carga.
