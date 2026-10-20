# Features de POIs, Servicios y Accesibilidad
## v0.1

## Problema
Contar POIs sin contexto produce scores malos.

Ejemplo:
30 restaurantes no hacen una zona mejor para una persona mayor si están lejos, cruzando grandes vías o no existen servicios esenciales.

## Principio
Transformar lugares en métricas de acceso.

# 1. Tipos de feature

## Proximidad
- nearest_supermarket_walk_time;
- nearest_pharmacy_walk_time;
- nearest_health_center_time;
- nearest_school_time.

## Cobertura
- supermarkets_within_10min_walk;
- pharmacies_within_10min_walk;
- schools_within_15min_walk.

## Densidad útil
Número de servicios ponderado por:
- distancia;
- población;
- categoría;
- importancia para el perfil.

## Diversidad
- poi_category_diversity;
- essential_service_diversity.

## Redundancia
No basta con tener un único servicio esencial.
Ejemplo:
- pharmacy_resilience_score;
- grocery_resilience_score.

## Accesibilidad temporal
Cuando existan horarios:
- services_open_evening;
- weekend_coverage.

## Accesibilidad real
Priorizar tiempo de red frente a distancia euclídea.

---

# 2. Scores derivados

## Daily Needs Score
Supermercado + farmacia + comercio básico + transporte.

## Family Services Score
Colegios + guarderías + parques + deporte + salud.

## Senior Daily Living Score
Salud + farmacia + supermercado + transporte accesible + centros de día.

## Student Convenience Score
Campus + transporte + supermercados + bibliotecas + ocio.

## Car-Free Score
Capacidad de satisfacer necesidades sin vehículo privado.

## 15-Minute Living Score
Porcentaje de necesidades básicas alcanzables dentro de un umbral temporal.

---

# 3. Personalización

El mismo dato cambia de peso según usuario.

Ejemplo:
- restaurante: peso bajo para muchos perfiles;
- guardería: peso crítico para familia con bebé;
- hospital: muy alto para determinados perfiles;
- nightlife: positivo para unos, negativo para otros.

---

# 4. Saturación y rendimientos decrecientes

No usar scoring lineal.

Tener:
1 supermercado → gran mejora.
2 → mejora.
8 → no ocho veces mejor.

Aplicar funciones de saturación/logísticas.

---

# 5. Competencia vs servicio

En PUBLIC:
más servicios suele implicar comodidad.

En PRO:
los mismos POIs pueden significar:
- demanda cubierta;
- saturación competitiva;
- oportunidad comercial.

Por ello se guardan métricas base y se interpretan de forma diferente por producto.

---

# 6. Calidad

Cuando no exista dato de calidad fiable, no inventarlo.

No usar ratings comerciales como fuente maestra sin revisar:
- sesgo;
- cobertura;
- licencia;
- frescura.

---

# 7. Salida explicable

No:
`services_score = 83`

Sí:
> 2 supermercados a menos de 8 min andando, farmacia a 5 min, centro de salud a 11 min y 14 categorías de servicios básicos accesibles en 15 minutos.
