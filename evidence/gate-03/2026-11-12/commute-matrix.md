# Tiempo en transporte público al trabajo (CORE-009, `commute-0.1`)

Llegada a las 08:30, 08:45, 09:00 (mediana de las tres), servicio desde las 05:30; a pie a 4 km/h con un rodeo de 1.3 sobre la línea recta; transbordos a pie hasta 250 m, acceso y salida hasta 1000 m, 120 s para cambiar en la misma parada.

## GTFS usados (día de referencia de cada uno) y limpieza

| Dataset | Día | trips_going_back | calls_interpolated | calls_estimated_by_speed | trips_estimated_by_speed | lines_without_any_time | trips_too_fast |
|---|---|---|---|---|---|---|---|
| crtm_gtfs_autobuses_urbanos | 2027-04-20 | 514 | 2122 | 39366 | 1250 | 12 | 2 |
| crtm_gtfs_cercanias | 2026-11-24 | 0 | 0 | 0 | 0 | 0 | 0 |
| crtm_gtfs_emt | 2026-11-24 | 0 | 0 | 0 | 0 | 0 | 0 |
| crtm_gtfs_interurbanos | 2027-04-20 | 98 | 6954 | 171273 | 5730 | 35 | 584 |
| crtm_gtfs_metro | 2025-11-25 | 0 | 0 | 0 | 0 | 0 | 0 |
| crtm_gtfs_metro_ligero | 2027-04-27 | 0 | 0 | 0 | 0 | 0 | 0 |

## Cobertura

| Destinos | Nº | Filas | Con minutos | Mediana (min) |
|---|---|---|---|---|
| station | 379 | 75800 | 56136 | 90.2 |
| zone | 200 | 40000 | 17647 | 114.0 |

## Hasta Puerta del Sol (metro)

| Zona | Minutos | Secciones que llegan |
|---|---|---|
| Centro | 9.4 | 111/111 |
| Chamartín | 23.6 | 101/101 |
| Ciudad Lineal | 25.9 | 170/170 |
| Villaverde | 29.4 | 105/105 |
| Leganés | 34.4 | 142/143 |
| Getafe | 38.6 | 121/122 |
| Torrejón de Ardoz | 47.4 | 78/78 |
| Móstoles | 51.6 | 136/136 |
| Tres Cantos | 51.9 | 25/25 |
| Collado Villalba | 61.4 | 31/32 |
| Alcalá de Henares | 69.6 | 125/125 |
| Aranjuez | 75.3 | 31/32 |
| Navalcarnero | 75.9 | 14/14 |
| Buitrago del Lozoya | 112.2 | 1/1 |
| Colmenar Viejo | 121.6 | 21/24 |
| San Martín de Valdeiglesias | sin dato | 1/4 |

Sin dato (50 zonas): Acebeda (La), Arroyomolinos, Atazar (El), Batres, Berzosa del Lozoya, Brea de Tajo, Bustarviejo, Canencia, Cenicientos, Chinchón, Corpa, Estremera, Fuentidueña de Tajo, Gascones, Guadalix de la Sierra, Hiruela (La), Horcajo de la Sierra-Aoslos, Horcajuelo de la Sierra, Madarcos, Manzanares el Real, Miraflores de la Sierra, Montejo de la Sierra, Moraleja de Enmedio, Navalafuente, Navas del Rey, Patones, Pedrezuela, Pezuela de las Torres, Piñuécar-Gandullas, Prádena del Rincón, Puebla de la Sierra, Ribatejada, Robledillo de la Jara, Robregordo, San Martín de Valdeiglesias, Santa María de la Alameda, Somosierra, Soto del Real, Titulcia, Valdaracete, Valdemanco, Valdepiélagos, Vellón (El), Venturada, Villaconejos, Villa del Prado, Villamanrique de Tajo, Villar del Olmo, Villarejo de Salvanés, Zarzalejo.

## Hasta Nuevos Ministerios (metro)

| Zona | Minutos | Secciones que llegan |
|---|---|---|
| Chamartín | 13.6 | 101/101 |
| Centro | 15.8 | 111/111 |
| Ciudad Lineal | 23.2 | 170/170 |
| Villaverde | 33.0 | 105/105 |
| Leganés | 43.5 | 141/143 |
| Getafe | 43.9 | 121/122 |
| Tres Cantos | 45.8 | 25/25 |
| Torrejón de Ardoz | 47.4 | 78/78 |
| Móstoles | 55.2 | 136/136 |
| Collado Villalba | 56.7 | 31/32 |
| Alcalá de Henares | 65.4 | 125/125 |
| Aranjuez | 75.3 | 31/32 |
| Navalcarnero | 81.3 | 14/14 |
| Colmenar Viejo | 106.6 | 21/24 |
| Buitrago del Lozoya | 112.2 | 1/1 |
| San Martín de Valdeiglesias | sin dato | 1/4 |

Sin dato (48 zonas): Acebeda (La), Arroyomolinos, Atazar (El), Batres, Berzosa del Lozoya, Brea de Tajo, Bustarviejo, Canencia, Cenicientos, Chinchón, Corpa, Estremera, Fuentidueña de Tajo, Gascones, Guadalix de la Sierra, Hiruela (La), Horcajo de la Sierra-Aoslos, Horcajuelo de la Sierra, Madarcos, Manzanares el Real, Miraflores de la Sierra, Montejo de la Sierra, Moraleja de Enmedio, Navalafuente, Navas del Rey, Patones, Pezuela de las Torres, Piñuécar-Gandullas, Prádena del Rincón, Puebla de la Sierra, Ribatejada, Robledillo de la Jara, Robregordo, San Martín de Valdeiglesias, Santa María de la Alameda, Somosierra, Soto del Real, Titulcia, Valdaracete, Valdemanco, Vellón (El), Venturada, Villaconejos, Villa del Prado, Villamanrique de Tajo, Villar del Olmo, Villarejo de Salvanés, Zarzalejo.
