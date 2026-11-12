# Alquiler de contratos nuevos: evaluación del índice CM 1934428 y alternativa (D-228)

Fecha: 2026-11-12. Línea A. Decisión de partida de Mariano: «Ajustar con el índice CM».

## 1. Problema
El alquiler por m² de la búsqueda (`alquiler_m2_mensual`, D-214) es la media de los alquileres declarados en el IRPF de 2024: contratos en vigor, la mayoría firmados años atrás. Ejemplos con 77 m²: Fuencarral-El Pardo ≈ 1.107 €/mes y Salamanca ≈ 1.526 €/mes. El presupuesto casi nunca limita y el Reality Check con +150 € no añade zonas.

## 2. Dataset CM 1934428: qué publica (comprobado el 12 nov)
- **Título:** «Índice de precios de la vivienda en alquiler por antigüedad de contrato (Base 2015)». Organización: Instituto de Estadística de la CM.
- **Licencia:** CC BY (`cc-by`). Metadatos: «Fecha Actualización 02-06-2026»; recursos modificados el 05-11-2026. Fuente declarada: «Estadística experimental. Índice de Precios de la Vivienda en Alquiler (IPVA). INE».
- **Contenido completo (8 filas):** dos índices anuales, 2021–2024, unidad «Índice» (2015 = 100), tipo de territorio «Otros», sin código ni nombre de territorio.

  | Año | Contrato nuevo | Contrato existente |
  |---|---|---|
  | 2021 | 113,661 | 112,298 |
  | 2022 | 119,327 | 114,531 |
  | 2023 | 124,319 | 117,106 |
  | 2024 | 135,753 | 120,323 |

- **Territorio:** los metadatos dicen «Ámbito: Toda España», pero los valores son idénticos a los de «Madrid, Comunidad de» en la tabla 59004 del INE («Índices nacionales y por comunidades autónomas: general y por antigüedad de contrato»); la serie nacional es otra (137,041 y 120,637 en 2024). Es **la Comunidad de Madrid entera: ni municipios ni distritos**.
- Variación anual en la CM (INE 59004): contrato nuevo +9,2 % en 2024 y existente +2,7 %. Peso de los contratos nuevos en la CM en 2024 (INE 59009): 10,8 %.

## 3. Por qué no sirve para ajustar el nivel del alquiler
1. **Es un índice de evolución, no un precio.** Cada serie vale 100 en su propio 2015. 135,753 / 120,323 = 1,128 solo dice que desde 2015 los contratos nuevos se han encarecido un 12,8 % más que los existentes. No dice cuánto más cuesta hoy un contrato nuevo que uno en vigor, porque no sabemos cuánto costaba cada uno en 2015.
2. **El propio INE avisa** (nota de prensa del IPVA 2021, «Novedades metodológicas»): «en los casos donde la vivienda haya estado alquilada con dos contratos diferentes en el mismo año, el precio anual utilizado para el cálculo del índice incluye ambos, por lo que la variación calculada solo recoge una parte del efecto del cambio de contrato».
3. **Un solo valor para toda la región.** Cualquier factor sacado de aquí subiría igual Salamanca y Villaverde. Sería un ajuste uniforme sin base para el nivel, es decir, un ajuste a ojo.

## 4. Alternativa con fuente oficial: la AEAT publica el alquiler de los contratos nuevos
- **Fuente:** Agencia Tributaria, «Estadística de viviendas declaradas en IRPF», ejercicio 2024 (metodología fechada el 01/07/2026). Es la misma estadística que la CM republica y que ya usamos (`cm_alquiler_m2_municipios` y `cm_alquiler_m2_codigo_postal_madrid` son sus tablas de 2024).
- **Tablas:**
  - «Comparativa de rentabilidad y precios de alquiler como vivienda habitual con los nuevos contratos para municipios de más de 20.000 habitantes»: 37 municipios de la CM;
  - «… por códigos postales para municipios de más de 20.000 viviendas…»: los 54 códigos postales de Madrid capital.

  Columnas: alquiler medio mensual y m² medios, del total y de los nuevos contratos.
- **Definición (metodología AEAT):** «nuevos contratos» son «los contratos de arrendamiento formalizados en el ejercicio de referencia de los datos», es decir, firmados en 2024.
- **No está en el portal de la CM.** Búsqueda en el CKAN de la CM el 12 nov: «"nuevos contratos"» da 0 resultados, y «alquiler nuevos» solo devuelve 1934428 y el Plan Alquila.
- **Reutilización (aviso legal de la AEAT):** permitida, también comercial. Es obligatorio citar la fuente y la fecha de última actualización, y está prohibido desnaturalizar el contenido.
- **Extracto de la CM:** `aeat_irpf_vivienda_2024_nuevos_contratos_cm.csv`, con 37 municipios y 54 códigos postales.
  - `factor = (alquiler nuevos / m² nuevos) / (alquiler total / m² total)`.
  - Municipios: de 1,054 a 1,264 (mediana 1,155). Madrid: 1.012 € por 71 m² frente a 1.167 € por 68 m², factor 1,204.
  - Códigos postales de Madrid: de 1,104 a 1,257 (mediana 1,166).

## 5. Propuesta (pendiente de Mariano)
**Opción A, recomendada: factor oficial por zona.**
- El alquiler de la búsqueda pasaría a ser el €/m² de la CM (el mismo dataset de hoy) multiplicado por el factor de contratos nuevos de la AEAT de la misma zona y el mismo año.
- Municipios: su factor. Distritos: el de sus códigos postales, con la misma ponderación de D-214.
- La CM sigue siendo la fuente del nivel, y la AEAT aporta solo la diferencia entre contratos nuevos y todos.
- Se aplica el factor y no el cociente directo de la AEAT porque el €/m² publicado es una media de cocientes por vivienda. El cociente de medias no coincide con él (la AEAT lo advierte en su metodología), pero el factor es comparable entre las dos columnas.
- **Hecho propuesto:** «Alquiler ≈ 1.270 €/mes por 77 m² (contratos firmados en 2024; los anuncios de hoy pueden pedir más)».
- **Efecto aproximado con 77 m²:** Fuencarral-El Pardo, de 1.107 a ~1.270 € (factor ~1,15). Salamanca, de 1.526 a ~1.880 € (~1,23). Con 1.500 € el presupuesto empezaría a limitar en los distritos centrales.
- **Límites declarados:**
  - parte del factor se debe a que los contratos nuevos son de pisos algo más pequeños (68 frente a 71 m² en Madrid), y un piso pequeño cuesta más por m²;
  - los municipios sin tabla de la AEAT (los de menos de 20.000 habitantes) siguen sin alquiler, como hoy.

**Opción B: solo un aviso más fuerte, sin cambiar la cifra.**
- Texto propuesto: «Media de los alquileres en vigor en 2024. Un contrato firmado en 2024 costaba de media un 15–25 % más por m² (Agencia Tributaria) y en la Comunidad de Madrid los contratos nuevos subieron un 9,2 % en 2024 (INE)».
- El presupuesto seguiría sin limitar.

**Descartado:**
- usar el índice 1934428 como factor de nivel (§3);
- los precios de anuncios de portales privados.
