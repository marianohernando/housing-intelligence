# Reglas de Documentación

## Objetivo
La documentación debe permitir a un desarrollador o agente nuevo entrar al proyecto sin depender del historial del chat.

## Toda nueva funcionalidad debe tener
- problema que resuelve;
- usuario;
- inputs;
- outputs;
- fuentes;
- reglas;
- servicios;
- UI;
- errores;
- seguridad;
- métricas;
- tests;
- aceptación.

## Toda nueva métrica debe tener
- definición;
- fórmula;
- unidad;
- dirección;
- resolución geográfica;
- fuente;
- frecuencia;
- estrategia de nulos;
- normalización;
- versión.

## Toda decisión de arquitectura importante
Debe registrarse como ADR en `11_engineering/adr/`.

## Regla de consistencia
Si un documento cambia una decisión existente:
1. modificar el documento fuente;
2. actualizar Decision Log;
3. actualizar Changelog;
4. revisar documentos dependientes.

## Nombres
Los nombres de entidades, tools, endpoints y features deben mantenerse estables.
Evitar sinónimos distintos para el mismo concepto.
