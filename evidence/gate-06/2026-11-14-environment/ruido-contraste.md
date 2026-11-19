# Ruido de la calle: antes y después de la revisión del PR #65 (R-02, R-03)

Mismas calles residenciales que los minutos a pie (residencial, de convivencia, sin clasificar, peatonal y terciaria, de OpenStreetMap), en `housing_ruido`. Fuente: Mapa Estratégico de Ruido 2021 del Ayuntamiento de Madrid, ruido del tráfico rodado calculado a 4 m de altura.

| % de calle residencial | Chamberí, día | Chamberí, noche | Usera, día | Usera, noche | Madrid, día | Madrid, noche |
|---|---|---|---|---|---|---|
| Antes: Lden > 65 y Ln > 55, leído en los nodos (cruces) | 77,5 | 84,6 | 28,5 | 36,1 | 34,0 | 41,7 |
| Paso intermedio: Ld > 65, en los nodos | 52,5 | 84,6 | 16,1 | 36,1 | 20,3 | 41,7 |
| **Ahora: Ld > 65 y Ln > 55, cada 10 m a lo largo de cada tramo** | **42,4** | **76,7** | **14,1** | **32,2** | **18,2** | **37,9** |
| Tabla 7 de la memoria del MER 2021: % de **personas** expuestas por encima de los mismos objetivos (método CNOSSOS, en fachada) | 6,9 | 24,8 | 3,3 | 7,1 | 3,4 | 10,2 |

- **R-02.** Lden (24 h, con 5 dB más por la tarde y 10 por la noche) no es «de día». El objetivo de 65 dB del RD 1367/2007 es de Ld (7–19 h). Cambiar a Ld baja Chamberí de 77,5 a 52,5 % de día.
- **R-03.** Un nodo es un cruce, donde se suma el tráfico de dos calles. Leer cada 10 m a lo largo del tramo, ponderado por la longitud, baja otra vez Chamberí: de 52,5 a 42,4 % de día y de 84,6 a 76,7 % de noche.
- **Frente a la tabla 7 de la memoria**, la calle sigue saliendo muy por encima de las personas:
  - La memoria cuenta **vecinos**, con el nivel en su fachada.
  - Vida Fácil cuenta **calle**, con el nivel en el eje de la calzada, que es donde está el tráfico.
  - Por eso la web dice «Calles con ruido alto: X % de las calles» y nunca «vecinos expuestos». La ayuda y «Cómo lo calculamos» lo explican.
  - El orden es parecido: Chamberí está por encima de Usera, de día y de noche, en las dos medidas.
- Memoria: «Mapa Estratégico de Ruido de Madrid 2021», tabla 7 «Población expuesta en el municipio de Madrid para el año 2021», infraestructuras viarias, § 5.3.2. Leída el 14 nov 2026 en transparencia.madrid.es.
