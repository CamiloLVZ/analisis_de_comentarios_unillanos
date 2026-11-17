# Fase 5 — Evaluación

## Estado

**Completada con revisión independiente de dos personas para sentimiento y emoción; taxonomía temática con reglas léxicas definidas manualmente.** Cada anotador etiquetó sentimiento y emoción en una muestra de 120 comentarios (40 por plataforma). Las anotaciones originales se conservaron y se compararon antes de contrastar el modelo. La muestra de temas (`theme_review_sample.csv`, 198 filas) no cuenta con etiquetas humanas independientes, por lo que la taxonomía temática se evalúa mediante cobertura, ausencia de colisiones y consistencia de categorías.

## Procedimiento

1. La investigadora y un segundo anotador etiquetaron sentimiento y emoción de forma independiente.
2. Se compararon las etiquetas y se calculó el acuerdo para las 120 filas de cada tarea.
3. Para las métricas del modelo se usaron solo los casos donde ambos anotadores coincidieron y la etiqueta no era ambigua.
4. Se ejecutó `python crisp_dm/05_evaluation/evaluate.py`.

Las anotaciones se guardan en `data/processed/model_outputs/evaluation_sample.csv`. El archivo contiene comentarios e IDs internos; es privado y no se incluye en el paquete público.

## Resultados Afectivos

| Tarea | Acuerdo entre personas | Casos concordantes no ambiguos | Accuracy | Macro-F1 |
|---|---:|---:|---:|---:|
| Sentimiento | 81,7 % (98/120) | 78 | 74,4 % | 0,739 |
| Emoción | 75,8 % (91/120) | 67 | 74,6 % | 0,429 |

El acuerdo se calcula sobre todos los casos etiquetados, incluidos pares donde ambos eligieron `ambiguo`. Las métricas del modelo excluyen los ambiguos y solo usan casos concordantes. Este subconjunto puede favorecer comentarios más claros, por lo que los valores podrían ser optimistas frente a todos los comentarios.

En emoción, varias clases tienen muy pocos casos o ninguno en el subconjunto evaluado (`fear` y `surprise` con 0 casos de soporte; `disgust` con 3 fallados). El macro-F1 promedia las siete clases establecidas y asigna F1 de cero a clases sin soporte en esta muestra; por eso no debe interpretarse como una estimación estable del desempeño general.

Los resultados detallados, matrices de confusión y métricas por clase están en `outputs/evaluation_report.json` y `outputs/evaluation_report.md`.

### Análisis selectivo por confianza (Sentimiento)

Se calculó la accuracy entre los casos concordantes no ambiguos cuya confianza de sentimiento supera varios umbrales:
- Confianza $\ge 0,6$: 63/78 casos (80,8 % cobertura), Accuracy: 84,1 %.
- Confianza $\ge 0,7$: 52/56 casos acertados (71,8 % cobertura de casos evaluables), Accuracy: 92,9 %.
- Confianza $\ge 0,8$: 40/43 casos (55,1 % cobertura), Accuracy: 93,0 %.
- Confianza $\ge 0,9$: 25/26 casos (33,3 % cobertura), Accuracy: 96,2 %.

En todo el corpus, 8.235 de 15.885 predicciones (51,8 %) alcanzan el umbral $\ge 0,7$. El umbral se eligió tras observar estos resultados en la misma muestra; por tanto, la mejora aparente es exploratoria y probablemente optimista. No debe presentarse como una nueva métrica de validación independiente.

## Evaluación del Componente Temático Refinado

Al no existir anotación humana independiente en `theme_review_sample.csv`, se evaluó la robustez de las reglas léxicas mediante:
1. **Reducción de colisiones léxicas:** Se verificó que patrones como `\bcursos?\b` no capturan palabras ajenas como *"concurso"*, *"recurso"* o *"discurso"* (81 falsos positivos corregidos frente a la versión preliminar).
2. **Eliminación de palabras funcionales ambiguas:** Palabras como *"cuando"*, *"donde"* y *"cuanto"* fueron sustituidas por sintagmas claros de consulta de trámites.
3. **Desarticulación del residual:** Se separó con éxito el 25,8 % de interacciones puramente sociales o sin texto (`Sin contenido temático suficiente`), permitiendo que el residual no categorizado bajara del 66,0 % al 34,4 %.
4. **Declaración ética:** No se calculan métricas formales de precisión/recall en temas ni se generan pseudoetiquetas con IA presentadas como humanas.

## Limitaciones

- El acuerdo entre personas no demuestra que la etiqueta acordada sea una verdad absoluta; sirve para detectar ambigüedad y fijar una referencia reproducible.
- La muestra es pequeña y estratificada por plataforma; no representa proporcionalmente el volumen total recolectado.
- La taxonomía temática opera con reglas léxicas definidas manualmente y carece de validación humana en muestra independiente.
- No se deben alterar las etiquetas originales para forzar coincidencias artificiales con los modelos.
