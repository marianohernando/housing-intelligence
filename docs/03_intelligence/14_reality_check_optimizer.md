# Reality Check Optimizer

## Objetivo
Encontrar la mínima modificación que convierte una búsqueda inviable en una búsqueda viable.

## Variables optimizables
- presupuesto;
- tiempo máximo de viaje;
- dormitorios;
- superficie;
- municipio/radio;
- coche/no coche;
- alquiler/compra;
- servicios imprescindibles vs preferibles.

## Hard constraints
Algunos requisitos pueden declararse no negociables:
- accesibilidad;
- dormitorio mínimo;
- proximidad sanitaria;
- etc.

## Algoritmo MVP
1. ejecutar búsqueda actual;
2. identificar constraints que eliminan más candidatos;
3. generar perturbaciones pequeñas;
4. recalcular disponibilidad;
5. ordenar cambios por “coste para el usuario”;
6. devolver frontera de opciones.

## Ejemplo
Situación actual: 0 zonas.

Alternativas:
- +100 €/mes → 3 microzonas.
- +10 min de trayecto → 9 microzonas.
- ampliar a municipios limítrofes → 14.
- bajar de 3 a 2 dormitorios → 21.

## Salida
No afirmar:
> “debes gastar más”.

Decir:
> “estas son las alternativas y su impacto”.

## PRO
El mismo motor puede analizar sensibilidad de demanda:
> cuánto aumenta el mercado objetivo si el precio baja 100 €/mes.
