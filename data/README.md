# Organización de datos

## Entradas mantenidas

- `raw/`: respuestas originales de scrapers por plataforma. No editar ni regenerar durante el análisis.
- `final/comments_unified.csv`: archivo unificado que se audita y usa como entrada canónica actual. Conservarlo intacto.

## Productos del proyecto CRISP-DM

- `preparados/prepared_comments.csv`: texto original y preprocesado, IDs internos y variables derivadas. Contiene texto de comentarios; es local, ignorado por Git y no debe desplegarse.
- `processed/model_outputs/`: predicciones por comentario y plantillas de anotación con texto/IDs. Local e ignorado por Git.
- `app/`: tablas agregadas para visualización, sin comentarios, IDs, nombres, fechas o URLs. Esta es la única carpeta de datos que la app necesita.

El paquete preparado para despliegue está en `../crisp_dm/06_deployment/deploy_bundle/`; al publicarlo como repositorio separado solo contendrá la aplicación y estos agregados.

## Material heredado

`processed/facebook/`, `processed/instagram/` y `final/processed/` pertenecen a pasos previos de scraping/unificación. No son entradas para la aplicación final. Cada fase CRISP-DM mantiene perfil, documentación y salidas agregadas bajo su directorio en `crisp_dm/`.

