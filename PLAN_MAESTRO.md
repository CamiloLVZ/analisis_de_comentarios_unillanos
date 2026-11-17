# Plan maestro del proyecto CRISP-DM

## 1. Identificación y propósito

**Título:** Temas institucionales, polaridad de sentimiento y emociones en los comentarios de redes sociales de la Universidad de los Llanos.

**Propósito:** Construir un análisis descriptivo y reproducible sobre los comentarios recolectados de las cuentas institucionales de Facebook, Instagram y YouTube, priorizando el descubrimiento de áreas temáticas clave para la gestión universitaria y presentando sus resultados agregados en una aplicación Streamlit.

**Unidad principal:** Comentario individual disponible en `data/final/comments_unified.csv`. Se conservan comentarios principales y respuestas. La interpretación de cada comentario se hace sin concatenar el texto de la publicación original para preservar la autenticidad de la opinión ciudadana y evitar contaminación de contexto.

## 2. Objetivos

### Objetivo general

Estructurar un mapa temático comprensivo de los comentarios institucionales mediante reglas léxicas supervisadas por dominio, evaluando conjuntamente la polaridad de sentimiento y las emociones en español, y comunicando resultados agregados y limitaciones en Streamlit.

### Objetivos específicos

1. Auditar la calidad, cobertura, estructura y privacidad de los datos existentes.
2. Preparar una tabla analítica preservando el texto original y documentando normalizaciones/exclusiones.
3. Categorizar los comentarios en una taxonomía temática institucional refinada (7 áreas sustantivas, una clase para contenido mínimo/emojis y un residual estricto).
4. Aplicar `pysentimiento` para estimar sentimiento (POS/NEG/NEU) y emociones en español (alegría, enojo, tristeza, miedo, sorpresa, disgusto y `others`).
5. Evaluar las predicciones afectivas en una muestra de 120 casos con doble anotación humana independiente, documentando con transparencia la naturaleza heurística de las reglas temáticas.
6. Construir una app local/publicable en Streamlit con agregados seguros y desglose de sentimiento por área temática.

## 3. Preguntas de investigación

- ¿Qué áreas temáticas institucionales concentran la conversación de la comunidad universitaria?
- ¿Qué proporción de los comentarios corresponde a interacciones puramente sociales o reacciones con emojis frente a comentarios con contenido proposicional?
- ¿Cómo varía la polaridad del sentimiento según el tema institucional analizado?
- ¿Qué variación descriptiva se observa entre plataformas y tipos de publicación?

**Fuera de alcance:** Evolución temporal; comparación causal de hilos; clasificación de perfiles o personas; generalización de representatividad a toda la población del Meta; inferencias que fusionen el texto del post con el comentario.

## 4. Datos disponibles y balance del corpus

De los 16.471 comentarios recopilados, 586 carecían de texto y fueron excluidos, consolidando un corpus analítico exacto de **15.885 comentarios**:
- Facebook: 11.529 comentarios (72,6 %)
- Instagram: 4.126 comentarios (26,0 %)
- YouTube: 230 comentarios (1,4 %)

Se identificaron 1.280 comentarios compuestos exclusivamente por emojis (`emoji_only`) y 2.484 respuestas con texto.

## 5. Resultados previstos y estructura

- `data/processed/model_outputs/scored_comments.csv`: tabla analítica completa a nivel de comentario (restringida a uso local y confidencial).
- `crisp_dm/06_deployment/deploy_bundle/data/app/`: archivos agregados anonimizados consumidos por Streamlit (`themes.csv`, `theme_sentiment.csv`, `sentiment.csv`, `emotions.csv`, `sentiment_confidence.csv`, `overview.json`).
- Aplicación interactiva con navegación temática, análisis condicionado de sentimiento y transparencia metodológica.
- `ARTICULO_FINAL.md`: informe consolidado con metodología, hallazgos y limitaciones.

## 6. Plan de fases y criterios de salida

| Fase | Objetivo y trabajo | Productos principales | Criterio de cierre |
|---|---|---|---|
| 1. Comprensión del negocio | Delimitar el problema, priorizando áreas temáticas sobre polaridades abstractas. | `crisp_dm/01_business_understanding/README.md`. | Enfoque temático formalizado; exclusión de representatividad poblacional. |
| 2. Comprensión de datos | Auditar esquema, cobertura de `post_text`, calidad y faltantes. | `crisp_dm/02_data_understanding/` scripts y reportes. | Perfil completo; trazabilidad de 16.471 a 15.885 comentarios. |
| 3. Preparación | Retirar vacíos, derivar banderas (`emoji_only`, `word_count`) y texto normalizado. | `data/preparados/prepared_comments.csv`. | Limpieza reproducible sin alterar texto original; muestras estratificadas. |
| 4. Modelado | Asignar temas con expresiones regulares delimitadas (`\b`) y clasificar sentimiento/emociones. | `theme_rules.json`, `analyze.py`, `scored_comments.csv`. | Residual temático reducido de 66 % a 34,4 %; 4.090 casos aislados en contenido mínimo; modelos afectivos intactos. |
| 5. Evaluación | Comparar concordancia en 120 casos para sentimiento/emoción; auditar consistencia temática. | `evaluation_report.md`, `evaluate.py`. | Reporte de 74,4 % en sentimiento y 74,6 % en emoción sobre concordantes; límites éticos explícitos. |
| 6. Despliegue | Agregación segura ($n \ge 10$), visualización por tema y verificación local. | `deploy_bundle/app.py`, datos en `data/app/`. | App verificada localmente; suma total exacta en 15.885; sin datos privados expuestos. |

## 7. Decisiones analíticas clave

1. **Jerarquía Analítica:** La clasificación temática es la dimensión organizativa primaria; el sentimiento y la emoción se evalúan como dimensiones secundarias y condicionadas.
2. **Desarticulación del Residual:** Separación explícita de `"Sin contenido temático suficiente (social/emoji/mención)"` para evitar la sobreestimación del desconocimiento temático.
3. **Delimitación Léxica:** Empleo estricto de límites de palabra (`\b`) para eliminar colisiones demostradas (p. ej., `\bcursos?\b`).
4. **Independencia Contextual:** El texto del post (`post_text`) no se concatena al comentario del usuario para prevenir sesgos de atribución.
5. **Transparencia en Evaluación:** Al no existir anotación humana independiente para la muestra temática de 198 comentarios, se declaran las reglas como heurísticas supervisadas y no se fabrican métricas artificiales con IA.
