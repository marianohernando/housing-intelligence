# ADR-001 — PostgreSQL + PostGIS + pgvector

## Estado
ACCEPTED.

## Contexto
Necesitamos datos relacionales, geoespaciales y embeddings.

## Decisión
Usar PostgreSQL como base principal, PostGIS para GIS y pgvector para embeddings.

## Motivos
- reduce complejidad;
- transacciones;
- GIS maduro;
- combina filtros SQL + distancia + vector;
- suficiente para MVP y bastante más.

## Consecuencia
No introducir Pinecone/Qdrant inicialmente.
Reevaluar solo si escala/latencia lo exige.
