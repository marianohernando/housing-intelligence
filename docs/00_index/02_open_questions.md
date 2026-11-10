# Preguntas / Dependencias todavía abiertas

Tras la auditoría integral, las cuestiones conceptuales principales están cerradas.

Lo que queda abierto no debe confundirse con documentación olvidada: son variables que solo pueden resolverse al investigar, adquirir datos, implementar o validar con usuarios/clientes.

## Datos — ejecución
- Selección definitiva de 30–50 datasets de Comunidad de Madrid para primera ingestión.
- Catálogo ampliado de 100–200 candidatos.
- Cobertura real por dataset.
- Licencia/condiciones verificadas dataset a dataset.
- Acceso autorizado a portales inmobiliarios / feeds de mercado.
- Calidad real de atributos de accesibilidad a nivel calle/edificio.
- Cobertura de urbanismo/planeamiento por municipio.

## Modelos — calibración
- Pesos numéricos iniciales definitivos del Residential Fit.
- Thresholds finales de confidence.
- Dimensión final del Place Embedding dentro del rango definido.
- Métricas finales de price/rent model según disponibilidad real de labels.
- Calibración del Housing Gap con demanda observada.
- Thresholds definitivos de JEV por workflow.

Estos números no deben fijarse por intuición antes de tener datos.

## Negocio — validación externa
- Precio exacto PLUS/PRO/Enterprise.
- TAM/SAM/SOM cuantificado.
- CAC real.
- tasa de cierre real.
- coste real por usuario/consulta.
- contratos/partners.
- disposición a pagar de promotoras.

## Legal — revisión externa antes de producción pública
- base jurídica/consentimientos finales;
- DPIA formal si procede;
- DPA con proveedores;
- textos de Privacy Policy / Terms;
- licencia final del repositorio open-source;
- revisión final de fuentes de terceros.

## DATAMAD
- ~~qué trabajo previo está permitido~~ → resuelto por las bases (D-174).
- licencia open source del repositorio (card LEGAL-001, puntúa en §10).
- ~~política sobre Google Maps/Gosom~~ → REJECTED, alternativas abiertas registradas (D-185).
- perfil/caso exacto de la demo final;
- datasets definitivos usados en la demo;
- qué capabilities se mantienen activadas en la build del 26 de noviembre.

## Importante
Ninguna de estas dependencias debe bloquear la creación de la hoja de ruta.
Cada una tiene un punto de decisión/gate documentado.
