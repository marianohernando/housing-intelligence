# Lineage & Dependency Graph

## Objetivo
Saber qué se rompe o debe recalcularse cuando cambia una fuente.

## Grafo conceptual
Source → Dataset → Metric → Feature → Model → Score → Product.

## Ejemplo
Alquiler oficial
→ rent_m2
→ affordability_feature
→ ResidentialFit
→ recomendaciones PUBLIC.

## Recalculation
Cuando cambia dataset:
1. identificar métricas dependientes;
2. recalcular features;
3. invalidar caches;
4. identificar modelos que requieren reentrenamiento;
5. recalcular scores materializados.

## Implementación inicial
Metadata tables + dependency registry.

Knowledge Graph dedicado no es necesario inicialmente.
