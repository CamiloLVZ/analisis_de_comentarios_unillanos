# Fase 3 — Preparación de los datos

## Estado

**Completada.** Preparación reproducible ejecutada con `prepare.py`.

## Reglas aplicadas

- Leer `data/final/comments_unified.csv` sin modificarlo.
- Eliminar IDs duplicados (0 en esta ejecución) y excluir texto vacío.
- Mantener respuestas con su bandera `is_reply`.
- Conservar `text` y crear `text_normalized` con `pysentimiento.preprocessing.preprocess_tweet(lang="es")` para explorar términos. Si el preprocesador falla, el script se detiene.
- Crear indicadores `has_emoji`/`emoji_only` con heurística Unicode.
- Crear muestra determinística de hasta 40 comentarios por plataforma (máximo 120) con columnas de etiquetas vacías para dos revisores.

## Resultados

- 16.471 filas de entrada; 0 IDs repetidos; 586 comentarios vacíos excluidos.
- La tabla analítica quedó con **15.885 comentarios**: Facebook 11.529, Instagram 4.126, YouTube 230.
- Se conservaron **2.484 respuestas con texto**; las respuestas vacías se excluyeron por la regla de texto vacío.
- Texto analítico marcó 4.288 comentarios con emoji/símbolo y 1.280 como símbolos sin letras ni números. La auditoría reporta 1.307 “solo símbolos” bajo una definición más amplia que incluye puntuación. Las dos medidas son aproximadas y no equivalentes.
- La normalización produjo etiquetas textuales de emojis comprensibles en español en los ejemplos comprobados (aplausos, cañón de confeti). El modelado usa el original y deja a `pysentimiento` aplicar su propio preprocesamiento para evitar doble normalización.
- Se generó una muestra fija de 120 registros, 40 por plataforma, para anotación manual. Contiene textos e IDs internos; se mantiene local y no se comparte.

## Salidas y uso

- `data/preparados/prepared_comments.csv`: entrada de la fase 4, con texto original y normalizado; privada.
- `data/processed/model_outputs/evaluation_sample.csv`: plantilla para la fase 5; privada.
- `data/processed/model_outputs/theme_review_sample.csv`: muestra estratificada de 198 textos (66 por plataforma) para revisión temática; privada.
- `outputs/preparation_summary.json`: conteos agregados sin texto.

La fase 4 usa `prepared_comments.csv`. La fase 5 une predicciones con `evaluation_sample.csv`. La fase 6 solo usará tablas agregadas.

## Ejecución

```powershell
python crisp_dm/03_data_preparation/prepare.py
```
