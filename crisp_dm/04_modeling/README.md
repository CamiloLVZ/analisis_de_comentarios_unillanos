# Fase 4 — Modelado y análisis

## Estado

**Completada.** Sentimiento y emoción se calcularon para todos los comentarios con texto; las reglas de temas se asignaron y los términos exploratorios se filtraron de descriptores genéricos de emojis.

## Métodos ejecutados

- Sentimiento: `pysentimiento.create_analyzer(task="sentiment", lang="es")`, modelo español predeterminado `robertuito-sentiment-analysis`.
- Emoción: `pysentimiento.create_analyzer(task="emotion", lang="es")`, modelo español predeterminado `robertuito-emotion-analysis`.
- Entrada del clasificador: texto original. El analizador aplica el preprocesamiento social de `pysentimiento`, incluyendo emojis; no se le vuelve a preprocesar el texto.
- Temas: reglas léxicas mutuamente excluyentes en `theme_rules.json`, con seis grupos definidos y un grupo residual. Se revisaron frecuencias de palabras/frases antes de ajustar las reglas. Son categorías exploratorias, no un modelo de tópicos validado ni etiquetas humanas revisadas una a una.
- Términos: frecuencias de unigramas/bigramas en la copia normalizada; se retiraron tokens genéricos como `emoji`, `tono`, `piel`, `hashtag`, `usuario` y `url`. El vocabulario de las descripciones de emojis permanece; por eso “manos” y “aplaudiendo” pueden representar tanto texto como iconografía.

## Resultados

Se calcularon **15.885** comentarios. Las frecuencias de polaridad fueron:

| Sentimiento | Comentarios | Porcentaje |
|---|---:|---:|
| Neutral (NEU) | 9.250 | 58,2 % |
| Positivo (POS) | 4.312 | 27,1 % |
| Negativo (NEG) | 2.323 | 14,6 % |

Las emociones predichas fueron:

| Salida del modelo | Significado mostrado | Comentarios | Porcentaje |
|---|---|---:|---:|
| `others` | Otros / sin emoción básica clara (clase neutral del model card) | 10.615 | 66,8 % |
| `joy` | Alegría | 3.916 | 24,7 % |
| `anger` | Enojo | 799 | 5,0 % |
| `sadness` | Tristeza | 466 | 2,9 % |
| `surprise` | Sorpresa | 79 | 0,5 % |
| `fear` | Miedo | 9 | 0,1 % |
| `disgust` | Disgusto | 1 | <0,1 % |

La configuración efectivamente descargada tiene `id2label: others` para la clase 0, aunque el texto del model card la denomina “neutral”. Se conserva el nombre bruto en la salida de análisis y se presenta como “Otros / sin emoción básica clara” en la app, para evitar confundirlo con NEU de sentimiento.

Las reglas temáticas asignaron:

| Tema sugerido por reglas | Comentarios | Porcentaje |
|---|---:|---:|
| Otros / tema no identificado | 10.486 | 66,0 % |
| Felicitaciones y reconocimiento | 2.346 | 14,8 % |
| Vida académica e investigación | 989 | 6,2 % |
| Información y trámites | 914 | 5,8 % |
| Admisiones e inscripciones | 579 | 3,6 % |
| Programas de acceso y bienestar | 459 | 2,9 % |
| Eventos y actividades | 112 | 0,7 % |

La categoría residual grande indica que el diccionario es incompleto. No debe leerse como un tema sustantivo único ni como prueba de que el tema no exista.

Entre los términos normalizados más frecuentes aparecen “manos”, “aplaudiendo”, “felicitaciones”, “gracias”, “excelente”, “corazones”, “educación”, “estudiantes” y “matrícula”. Parte de la frecuencia de “manos/aplaudiendo/corazones” proviene de emojis convertidos a descripciones, por lo que sirve como señal afectiva exploratoria, no como conteo puramente verbal.

### Diagnóstico de información disponible en el texto

En el corpus preparado, 1.280 comentarios (8,1 %) son solo emojis y 2.728 (17,2 %) tienen como máximo dos palabras. Estas señales pueden ayudar a explicar parte de las predicciones neutrales o sin emoción básica, pero no prueban que esos textos sean inútiles: “¿Cuándo abren?” o “¡Excelente!” son breves y sí comunican algo. Por eso no se eliminaron ni se recodificaron automáticamente. La muestra para revisar temas (198 filas) está disponible, pero sus columnas `theme_gold_1` y `theme_gold_2` siguen vacías; no se cambiaron reglas a partir de intuiciones no contrastadas.

## Salidas y uso

- `outputs/top_terms.csv`: frecuencias agregadas de 100 unigramas y 100 bigramas; apoya revisión/cambio de categorías.
- `outputs/theme_counts.csv`: conteos de temas sugeridos por plataforma.
- `outputs/model_summary.json`: modelos usados y distribución global de etiquetas/temas.
- `data/processed/model_outputs/scored_comments.csv`: predicciones/probabilidades/indicadores por ID; local e ignorado por Git.
- La distribución por confianza de sentimiento se deriva para la aplicación desde `sentiment_confidence` sin modificar las etiquetas originales.

La fase 5 contrasta estas predicciones con una muestra pequeña etiquetada por dos revisores. La fase 6 consume únicamente categorías y conteos agregados. Los benchmarks de los autores no predicen necesariamente este dominio: sus resultados para RoBERTuito son aproximados a macro-F1 70 en sentimiento y 55 en emoción, medidos en sus conjuntos de evaluación ([resultados de `pysentimiento`](https://github.com/pysentimiento/pysentimiento/blob/master/docs/TASKS.md)).

## Reproducibilidad

```powershell
python crisp_dm/04_modeling/analyze.py
python crisp_dm/04_modeling/analyze.py --terms-only
python crisp_dm/04_modeling/analyze.py --themes-only
```

`--terms-only` y `--themes-only` actualizan frecuencia o temas sin volver a ejecutar inferencia. Para obtener etiquetas completamente nuevas se ejecuta el comando sin opciones.

