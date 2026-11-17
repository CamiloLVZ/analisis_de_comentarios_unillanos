# Temas, Sentimiento y Emociones en Comentarios de Unillanos

Las cuentas institucionales en redes sociales (Facebook, Instagram y YouTube) concentran miles de interacciones digitales que reflejan inquietudes académicas, trámites administrativos, expresiones de reconocimiento y posturas frente a coyunturas universitarias. No obstante, la brevedad de los mensajes, el uso intensivo de emojis, la dependencia del contexto de publicación y el volumen de datos dificultan su seguimiento manual y estructurado.

Este proyecto implementa un flujo analítico que:

- **Audita y consolida** un corpus de 16.471 registros brutos (15.885 comentarios analizables tras limpieza de texto vacío).
- **Estima polaridad afectiva y emociones básicas** en español mediante modelos basados en transformadores (`pysentimiento` / RoBERTuito).
- **Clasifica temáticas institucionales** mediante reglas léxicas determinísticas auditadas y congeladas criptográficamente (incorporando categorías como movilización estudiantil, bienestar y trámites).
- **Valida empíricamente** los resultados frente a evaluación humana independiente a ciegas ($n = 198$).
- **Despliega visualizaciones interactivas** en una aplicación web en Streamlit con agregaciones seguras.

---

## Organización del Repositorio

- **`crisp_dm/`**: Ciclo metodológico estructurado en sus seis fases CRISP-DM (01 a 06), con código auditable, perfiles de calidad y tablas agregadas.
- **`crisp_dm/06_deployment/deploy_bundle/`**: Aplicación web interactiva en Streamlit (`app.py`), lista para despliegue con datos agregados precalculados.
- **`data/`**: Capturas institucionales originales (`data/raw/`) y corpus canónico unificado auditado (`data/final/comments_unified.csv`).
- **`docs/articulo/`**: Artículo científico formal en formato IEEE (`articulo_unillanos.pdf`), fuente LaTeX (`articulo_unillanos.tex`), figuras vectoriales y paquete de envío (`comentarios-unillanos.zip`).
- **`docs/`**: Guion técnico del video de presentación de 3 minutos con interpretación analítica (`GUION_VIDEO_PRESENTACION_UNILLANOS.pdf` y `.md`).
- **`scripts/`**: Utilidades para regenerar las figuras vectoriales del artículo (`generate_article_figures.py`).

---

## Fin y Alcance

El fin de este proyecto es estrictamente académico, descriptivo y de auditoría de métodos de PLN sobre redes sociales en entornos universitarios.

Para garantizar la privacidad y la ética en el manejo de datos, el repositorio y la aplicación operan bajo principios de minimización de datos: no se exponen textos individuales, nombres de usuario ni identificadores personales, y se aplica supresión estricta de celdas con baja frecuencia ($n < 10$). Los hallazgos describen el conjunto recolectado y no deben generalizarse como representativos de toda la comunidad universitaria.

- **Aplicación web:** [comentarios-unillanos.streamlit.app](https://comentarios-unillanos.streamlit.app)
