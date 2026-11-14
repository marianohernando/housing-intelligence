# Días de oficina, teletrabajo, familia o amigos y «Qué falta» plegada (D-240)

Feedback de usuarios de prueba del 14 nov e ideas de Mariano. Rama `claude/s1-family-telework`, ya con la base `15393cb` (#53, #54 y #56).

Cómo se comprobó:
- API de esta rama (`fit-0.8`) sobre la base local `housing`, en solo lectura (`default_transaction_read_only=on`), frente a la API de producción.
- Web con `next build` y `next start`, con el buscador activo y esa API.
- Playwright con Chromium, a 1440 y a 390 px, y axe (WCAG 2.2 AA).

## Invariante del pitch (`invariante-produccion.txt`, `golden-search.txt`)

El caso del ejemplo (4 días, sin límite y sin familia) da lo mismo que producción:
- 27 zonas que encajan y 15 sin dato;
- top 10: Latina, Moratalaz, Ciudad Lineal, Puente de Vallecas, Fuencarral-El Pardo, Usera, Carabanchel, Hortaleza, San Blas-Canillejas y Villaverde;
- «Casi encajan»: Chamartín, Salamanca, Centro, Chamberí y Retiro;
- `data` igual salvo `methodology_version` (`fit-0.8` frente a `fit-0.7`); `/search/barrios` igual en los 21 distritos;
- `scripts/golden_search.py`: 9 de 9 (incluye `ranked_order` y `near_miss_order` de D-239).

## Casos (`casos-dias-familia.txt`, API local)

| Caso | Zonas que encajan | Qué cambia |
|---|---|---|
| Ejemplo, 3 días | 27 | Igual que con 4 |
| Ejemplo, 1 o 2 días | 27 | El trayecto pesa la mitad: Alcorcón y Leganés entran en el top 10 |
| Ejemplo, teletrabajo total | 27 | El trayecto no puntúa: las 10 primeras al 100 %, ordenadas por servicios a pie (D-239) |
| Teletrabajo total y 45 min como mucho | 10 | El límite se aplica: la condición que más quita es `commute:0` |
| Familia en Getafe Central | 27 | Dos hechos de trayecto en cada zona |
| Familia en Getafe Central, 30 min | 5 | Villaverde, Leganés, Getafe, Fuenlabrada y Parla (`commute:1`) |
| Familia en un punto cualquiera (lon −3,38, lat 40,49), 45 min | 2 | Torrejón de Ardoz y Alcalá de Henares, sin avisos de destino |

## Capturas

| Fichero | Qué se ve |
|---|---|
| `formulario-familia-dias-1440.png`, `formulario-familia-dias-390.png` | El ejemplo con «2 días» y su ayuda, y «Cerca de mi familia o amigos» con Getafe Central y 30 min |
| `formulario-teletrabajo-1440.png`, `formulario-teletrabajo-390.png` | «Teletrabajo total», con su ayuda y el límite de 45 min, que se sigue aplicando |
| `resultados-familia-dias-1440.png`, `resultados-familia-dias-390.png` | La búsqueda anterior: 5 zonas, y lo que más limita es el trayecto a la familia |
| `que-falta-plegada-1440.png`, `que-falta-plegada-390.png` | «Qué falta» sin zona: «Madrid (toda la ciudad)» y el botón «Ver las 199 zonas» |
| `que-falta-plegada-pantalla-390.png` | La misma lista en el móvil, dentro de la página |

## Comprobaciones de la web (`capture-report.json`)

- **El formulario envía** los dos lugares, el trabajo primero: `days_per_week: 2` y `max_minutes: null` en el trabajo, y `kind: "family"` con `max_minutes: 30`. Con «Teletrabajo total» envía `days_per_week: 0` y conserva `max_minutes: 45`.
- **«Qué falta» plegada:**
  - el botón empieza con `aria-expanded="false"` y solo se ve el enlace de Madrid; abierta, `aria-expanded="true"` y 199 enlaces;
  - al escribir «Getafe», sale aunque la lista esté plegada y el botón desaparece;
  - en el móvil, la página mide 5.090 px plegada frente a 14.524 abierta.
- **axe:** 0 incidencias en el formulario, en los resultados y en «Qué falta» (plegada y abierta), a 1440 y a 390 px. Ningún desborde horizontal y ningún error en la consola.
