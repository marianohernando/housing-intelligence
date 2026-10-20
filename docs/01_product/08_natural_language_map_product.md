# Natural Language Map — Producto

## Visión
El usuario podrá controlar el mapa mediante lenguaje natural.

Ejemplo:
> “Enséñame zonas para una familia de cuatro con máximo 1.400 €, colegio público a 15 minutos y Cercanías.”

El sistema:
1. interpreta;
2. convierte preferencias en filtros;
3. llama tools;
4. genera capa;
5. mueve cámara;
6. explica.

## Ejemplos PUBLIC
- “Más barato, pero sin empeorar mucho el trayecto.”
- “Quiero algo parecido a Chamberí con más verde.”
- “Quita zonas donde necesite coche.”
- “¿Qué cambia si subo 150 € el presupuesto?”

## Ejemplos PRO
- “Ilumina zonas con Housing Gap familiar alto y poca obra nueva.”
- “Muéstrame parcelas cerca de Cercanías con demanda senior creciente.”
- “Compara esta parcela con otras similares.”

## Principio
La conversación modifica un `MapState` estructurado.
No genera código/SQL arbitrario.
