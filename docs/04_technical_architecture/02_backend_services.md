# Backend y Servicios

## API Gateway
FastAPI.

## Reglas
- Frontend nunca accede directo a DB.
- Tools MCP llaman a servicios, no a SQL libre.
- Validación de entrada/salida.
- Pydantic schemas.
- permisos por capa.

## Workers
Tareas:
- ingestión;
- normalización;
- embeddings;
- recalculo de features;
- generación de tiles;
- entrenamiento;
- refresco de caches.
