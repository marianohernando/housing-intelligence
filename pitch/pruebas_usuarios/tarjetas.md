# Tarjetas para la tarea 1

Se enseña una sola tarjeta a cada persona. Están pensadas para que la búsqueda dé resultados en la demo: el 12 nov, la A daba 54 zonas y la B, 15.

---

## Tarjeta A · Familia

**Sois dos adultos y un niño de 6 años.**

**Podéis pagar hasta 1.300 € al mes de alquiler.**

**Uno de vosotros trabaja cerca de la estación de Atocha.**

**Queréis un colegio cerca de casa.**

---

<div style="page-break-after: always"></div>

## Tarjeta B · Persona mayor

**Vives sola o solo y tienes 72 años.**

**Puedes pagar hasta 900 € al mes de alquiler.**

**Quieres tener el centro de salud y la farmacia a un paseo.**

---

<!--
Nota para el moderador (no se enseña):
- Comprobado con POST /api/v1/search en producción el 12 nov.
  - Tarjeta A (2 adultos, 1 menor de 6 años, 1.300 €/mes, trabajo en Atocha, sin servicios obligatorios): pasan 54 zonas.
  - Tarjeta B (1 adulto, 900 €/mes, centro de salud a 15 min y farmacia a 10 min, imprescindibles): pasan 15 zonas.
  - En las dos, en muchas zonas falta el precio del alquiler, porque la Comunidad solo lo publica en municipios grandes. La web lo dice: es un buen momento para ver si se entiende.
- Si la persona elige otros minutos o no marca nada como imprescindible, también vale: lo que importa es cómo lo encuentra.
-->
