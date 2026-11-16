# Organización de datos

## Entradas mantenidas

- `raw/`: respuestas originales de scrapers por plataforma. No editar ni regenerar durante el análisis.
- `final/comments_unified.csv`: CSV canónico reconstruible desde `raw/` con `crisp_dm/02_data_understanding/unify_raw_data.py`; es la entrada auditada por CRISP-DM.

## Productos del proyecto CRISP-DM

- `preparados/prepared_comments.csv`: texto original y preprocesado, IDs internos y variables derivadas. Contiene texto de comentarios; es local, ignorado por Git y no debe desplegarse.
- `processed/model_outputs/`: predicciones por comentario y muestra anotada con texto/IDs. Local e ignorado por Git.
- `../crisp_dm/06_deployment/deploy_bundle/data/app/`: tablas agregadas para visualización, sin comentarios, IDs, nombres, fechas o URLs. Esta es la única carpeta de datos que la app necesita.

El paquete preparado para despliegue está en `../crisp_dm/06_deployment/deploy_bundle/`; la app y su única copia de agregados viven juntas en ese paquete.

## Material heredado

`legacy/processed/facebook/` y `legacy/processed/instagram/` contienen listados y lotes auxiliares de la recolección histórica. No son entradas para la aplicación final. `processed/` queda reservado para los resultados analíticos actuales.

