# Para inversores y promotores (20 nov, D-248)

Rama `claude/f9-investor-app`, rebasada sobre `claude/sprint-1-public` con la línea A fusionada (#95, D-247). La sección `/inversores` lista los 108 barrios piloto (Madrid capital dentro de la M-40) y `/inversores/{barrio}` da la ficha de un barrio con la calculadora de viabilidad v0. Lleva la etiqueta «Plan Inversor (acceso libre durante el concurso)», sin cobro ni login. Decisión: D-248. Textos: `pitch/textos_web.md` §11.

## Cómo se ha medido

- Web: `next build` con `NEXT_PUBLIC_FEATURE_SEARCH=true` (como en producción) y `next start` en el 3094.
  - Hubo un build completo y dos más con la caché, para las etiquetas de los ámbitos, «0 parcelas» y la nota de la rentabilidad.
  - Al final de cada build, el aviso de seguridad de Next corta el comando; la compilación queda completa.
- API de la rama en el 8094, en dos pasadas:
  - **`housing_inv_b`** (la base de la rama: copia de `housing` con el dataset de los visados y la feature del PEM cargados): e2e, golden y `check-inversores-housing_inv_b.json`. Aquí no están las features de A.
  - **`housing_inv_a`** (la base de la línea A, con sus features cargadas; **solo lectura**): las capturas y `check-inversores.json` / `check-inversores-buenavista.json`. Así se ven el comercio, el remanente con sus notas y el suelo vacante. Esta base no tiene el dataset de los visados, así que el PEM sale de la cifra versionada (`viability_data.py`), con la misma fuente.

## Capturas (1440 y 390 px)

- `*-lista.png`: los 108 barrios por distrito.
  - Cada uno dice lo que falta en su distrito, nombrándolo: «Falta en el distrito de Carabanchel: …».
  - Sus parcelas públicas, la edificabilidad que queda en ámbitos del Plan General (avisa si alguno ocupa también otros barrios) y su precio estimado.
  - A 390 px, la primera pantalla.
- `*-ficha.png`: **Pinar del Rey** (Hortaleza). Secciones, en orden: quién vive aquí, precios, qué falta, suelo, calculadora y fuentes.
  - En «qué falta», cada fila dice «Dato del distrito de Hortaleza», y está el comercio de proximidad del censo de locales.
  - En «suelo», 4 parcelas del Portal del Suelo y 4 ámbitos con 55.628 m².
- `*-ficha-suelo.png`: las parcelas (con su gestor y el enlace al visor) y los ámbitos (con su situación y el tipo de vivienda).
- `*-buenavista-suelo-ambitos-compartidos.png`: **Buenavista** (Carabanchel), dos ámbitos que ocupan también otros barrios.
  - Cada uno lleva su nota: «aquí está el 79 %» y «el 74 % de su superficie».
  - La fuente de la suma dice que cuentan enteros.
  - Sin parcelas, el encabezado no dice «0 parcelas».
- `1440-calculadora.png`: la calculadora.
  - Elegida, la parcela R25-L (de la AVS, con el aviso de que el precio libre y el valor residual no valen para vivienda protegida).
  - Supuestos con su fuente y su desglose, y el aviso junto al coste.
- `*-escenarios-sin-suelo.png`: sin precio del suelo **no hay veredicto**.
  - Lo máximo que se puede pagar por el suelo: 2.939 €/m² edificable en el base, 3.364 en el optimista y 2.513 en el pesimista.
  - La rentabilidad bruta del alquiler cuenta el suelo a ese valor: 5,0 %. Sale igual en los tres escenarios, y lo dice: con el suelo a su valor residual, la inversión es la fracción de los ingresos que no es margen ni comercialización.
  - Comprobación de demanda: hipoteca 42 % y alquiler 37 % de la renta media, por encima del 30 %. No cuenta gastos ni suministros, así que es optimista.
- `*-escenarios-con-suelo.png`: con el suelo a 3.200 €/m² edificable, el semáforo (icono, palabra y color): base 15,1 % «Ajustar», optimista 22,8 % «Sale» y pesimista 5,6 % «No sale».
- `*-impresion.png` y `ficha-inversores.pdf`: «Guardar como PDF».
  - Sin la cabecera ni los botones, con los desgloses abiertos.
  - Con la fecha, la de los datos, las fuentes (una vez cada una) con su dirección y los avisos.

## Comprobaciones

- `apps/web/scripts/check-inversores.mjs`, sobre las dos bases y en Pinar del Rey y Buenavista: la lista, la ficha, la calculadora con suelo y la impresión, a 390 y 1440 px.
  - **0 textos de menos de 16 px** y **0 objetivos de menos de 44 px**.
  - Sin desborde, **axe 0** y sin errores de consola.
  - Sin precio del suelo, ningún «Sale», «Ajustar» ni «No sale».
- `infra/deploy/e2e/e2e_prod.mjs --base http://localhost:3094` (`e2e-report.json`, sobre el último build): **escritorio 1440 px 116/116 y móvil 390 px 92/92**.

## Invariante

`scripts/golden_search.py` contra `housing_inv_b`: **10 de 10**. Ni `/search` ni `/gaps` leen nada de D-248.

## Tests

- `make lint typecheck test-unit`: limpios, con Python 1119 y vitest 598.
- `make test-db`: **167**. Incluye los 6 de `tests/integration/test_api_investors.py`:
  - las features de A, ya en la base de pruebas;
  - la carga del dataset de los visados y su paso por `/datasets`;
  - las consultas de la lista: 6 para los 108 barrios, antes ~216.
