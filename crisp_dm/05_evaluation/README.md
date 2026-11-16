# Fase 5 — Evaluación

## Estado

**Completada con revisión independiente de dos personas.** Cada anotador etiquetó sentimiento y emoción en una muestra de 120 comentarios (40 por plataforma). Las anotaciones originales se conservaron y se compararon antes de contrastar el modelo.

## Procedimiento

1. La investigadora y un segundo anotador etiquetaron sentimiento y emoción de forma independiente.
2. Se compararon las etiquetas y se calculó el acuerdo para las 120 filas de cada tarea.
3. Para las métricas del modelo se usaron solo los casos donde ambos anotadores coincidieron y la etiqueta no era ambigua.
4. Se ejecutó `python crisp_dm/05_evaluation/evaluate.py`.

Las anotaciones se guardan en `data/processed/model_outputs/evaluation_sample.csv`. El archivo contiene comentarios e IDs internos; es privado y no se incluye en el paquete público.

## Resultados

| Tarea | Acuerdo entre personas | Casos concordantes no ambiguos | Accuracy | Macro-F1 |
|---|---:|---:|---:|---:|
| Sentimiento | 81,7 % (98/120) | 78 | 74,4 % | 0,739 |
| Emoción | 75,8 % (91/120) | 67 | 74,6 % | 0,429 |

El acuerdo se calcula sobre todos los casos etiquetados, incluidos pares donde ambos eligieron `ambiguo`. Las métricas del modelo excluyen los ambiguos y solo usan casos concordantes. Este subconjunto puede favorecer comentarios más claros, por lo que los valores podrían ser optimistas frente a todos los comentarios.

En emoción, varias clases tienen muy pocos casos o ninguno en el subconjunto evaluado. El macro-F1 promedia las siete clases establecidas y asigna F1 de cero a clases sin soporte en esta muestra; por eso no debe interpretarse como una estimación estable del desempeño general. El tamaño y el muestreo tampoco permiten generalizar a toda la comunidad ni comparar de forma precisa plataformas.

Los resultados detallados, matrices de confusión y métricas por clase están en `outputs/evaluation_report.json` y `outputs/evaluation_report.md`.

## Limitaciones

- El acuerdo entre personas no demuestra que la etiqueta acordada sea una verdad absoluta; sirve para detectar ambigüedad y fijar una referencia reproducible.
- La muestra es pequeña y estratificada por plataforma; no representa proporcionalmente el volumen total recolectado.
- Sentimiento y emoción se anotaron manualmente; las categorías temáticas siguen basadas en reglas léxicas exploratorias y no cuentan con evaluación humana equivalente.
- No se deben editar las etiquetas para que coincidan con las predicciones del modelo.
- No vuelvas a ejecutar `prepare.py` sin respaldar `evaluation_sample.csv`: la preparación regenera esa muestra y podría borrar las etiquetas. El modelado puede volver a ejecutarse por separado.
