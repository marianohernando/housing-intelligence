# Formulario de preselección DATAMAD 2026: lo que enviamos

**Enviado el 12 nov por Mariano, resumen principal (98 palabras).** Formulario: https://forms.gle/NyatKHN95aPxvQro8 («DATAMAD 2026 | Presentación de propuestas»). Los datos personales (nombre, correo y teléfono) no se guardan aquí porque el repositorio es público.

## Nombre del proyecto
Vida Fácil — Encuentra tu sitio en Madrid

## Resumen (98 palabras)

<!-- resumen:inicio -->
Vida Fácil convierte los datos abiertos de la Comunidad de Madrid en un mapa de lo que falta. A cada persona le recomienda dónde vivir según su alquiler, hogar y trabajo, explica el porqué en lenguaje cotidiano y, si nada encaja, enseña cuántas zonas aparecen al relajar cada condición. A ayuntamientos y empresas les muestra, por municipio y por distrito de Madrid, qué falta, qué está justo y qué está cubierto: escuelas infantiles, colegios, salud, mayores, farmacias y vivienda. Usa 26 datasets del portal regional y cada resultado cita su fuente y su fiabilidad. Código abierto con API.
<!-- resumen:fin -->

Recuento:
```bash
awk '/^<!-- resumen:fin/{f=0} f; /^<!-- resumen:inicio/{f=1}' pitch/formulario.md | wc -w   # 98
```

## Enlaces

```text
Demo: https://vidafacil-madrid.vercel.app
Código abierto (Apache-2.0): https://github.com/marianohernando/housing-intelligence
Datasets que integra, con licencia y control de calidad: https://github.com/marianohernando/housing-intelligence/blob/claude/sprint-1-public/pitch/datasets_cm.md
```

## Dónde se comprueba cada afirmación

Las llamadas a la API van contra la demo pública (https://vidafacil-madrid.vercel.app/api/v1) y se comprobaron el 12 nov.

| Afirmación | Dónde se comprueba |
|---|---|
| «Usa 26 datasets del portal regional» | [`pitch/datasets_cm.md`](datasets_cm.md): la lista se genera desde el catálogo del repositorio, con el enlace, la licencia y el control de calidad de cada conjunto. **El resumen se envió el 12 nov con 26; desde el 13 nov son 27, al añadir el valor tasado de la vivienda (Comprar).** La API da lo mismo que la lista: `GET /datasets?cm_only=true` devuelve `cm_open_data_count: 27` |
| «un mapa de lo que falta» · «qué falta, qué está justo y qué está cubierto» | `GET /gaps/distrito/2807913`: en Puente de Vallecas faltan escuelas infantiles, 2,8 al alcance a pie por cada 1.000 niños de 0 a 4 años frente a 4,9 en los demás municipios urbanos. El método está explicado en la pestaña [«Cómo lo calculamos»](https://vidafacil-madrid.vercel.app/como-lo-calculamos) de la demo |
| «escuelas infantiles, colegios, salud, mayores, farmacias y vivienda» | Las 6 filas de `GET /gaps/{nivel}/{código}`. La vivienda sale SIN DATOS en los distritos de Madrid, porque la Comunidad no la publica a ese nivel |
| «por municipio y por distrito de Madrid» | Los 179 municipios y los 21 distritos de Madrid capital. Por ejemplo, Chamartín: `GET /gaps/distrito/2807905` |
| «recomienda dónde vivir según su alquiler, hogar y trabajo» | `POST /search` con el caso de ejemplo ([`scenario_state.familia_castellana.fixture.json`](../data/fixtures/contracts/scenario_state.familia_castellana.fixture.json)): encajan 33 de 199 zonas. La primera es Fuencarral-El Pardo, con un 100 % y «29 min en transporte público hasta Paseo de la Castellana (Azca), llegando a las 9:00» |
| «si nada encaja, enseña cuántas zonas aparecen al relajar cada condición» | La misma búsqueda: «+5 min a pie hasta colegio con primaria: saldrían 50 zonas, 17 más» |
| «explica el porqué en lenguaje cotidiano» | Cada fila trae su frase. Por ejemplo, en Puente de Vallecas: «2,8 escuelas infantiles al alcance a pie por cada 1.000 niños de 0 a 4 años; en los demás municipios urbanos de la Comunidad de Madrid, 4,9 (en toda la Comunidad, 4,7)» |
| «cada resultado cita su fuente y su fiabilidad» | Cada fila de «Qué falta» y cada dato del buscador llevan los conjuntos de los que salen (nombre, enlace, versión y licencia) y su fiabilidad |
| «Código abierto con API» | [`LICENSE`](../LICENSE) (Apache-2.0) y las rutas de la API en [`docs/04_technical_architecture/31_public_api_routes.md`](../docs/04_technical_architecture/31_public_api_routes.md) |
