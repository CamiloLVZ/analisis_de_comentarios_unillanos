# Fase 5 — Evaluación

## Estado

**Completada con validación humana independiente de dos personas para sentimiento, emoción y taxonomía temática (reglas léxicas definidas manualmente).** Ambos autores etiquetaron sentimiento y emoción en una muestra de 120 comentarios (40 por plataforma), y la taxonomía temática en una muestra estratificada de 198 comentarios (66 por plataforma). Las anotaciones originales se conservaron y los desacuerdos fueron resueltos mediante consenso humano independiente antes de contrastar los modelos y las reglas.

## Procedimiento

1. Los dos autores del proyecto (Juan Camilo Londoño Velasquez y Juan David Burgos Atuesta) etiquetaron de forma independiente y a ciegas:
   - Sentimiento y emoción en la muestra estratificada de 120 comentarios (`evaluation_sample.csv`).
   - Categorías temáticas en la muestra estratificada de 198 comentarios (`theme_review_sample.csv`).
2. Se calcularon métricas de acuerdo inter-anotador observado ($P_o$) y coeficiente $\kappa$ de Cohen tanto globales como excluyendo casos ambiguos.
3. Para sentimiento y emoción, las métricas del modelo se calcularon sobre los casos concordantes no ambiguos (`evaluate.py`).
4. Para la taxonomía temática, los desacuerdos fueron acordados mediante consenso humano y evaluados contra las reglas léxicas congeladas (`evaluate_themes.py`).

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

## Evaluación del Componente Temático (Fase 5)

Para evaluar la taxonomía temática formalmente contra las anotaciones independientes de dos personas, se desarrolló el script `evaluate_themes.py`:

```powershell
python crisp_dm/05_evaluation/evaluate_themes.py `
    --anotador-a data/processed/model_outputs/theme_labeling_anotador_A.csv `
    --anotador-b data/processed/model_outputs/theme_labeling_anotador_B.csv `
    --clave data/processed/model_outputs/theme_labeling_clave.csv `
    --scores data/processed/model_outputs/scored_comments.csv
```

### Procedimiento de Dos Pasos:
1. **Paso 1 (Acuerdo Inter-Anotador y Detección de Desacuerdos):**  
   Calcula el acuerdo observado ($P_o$) y el índice Kappa de Cohen ($\kappa$) entre los dos anotadores independientes para todas las filas ($N=198$) y excluyendo casos ambiguos. Exporta automáticamente a `data/processed/model_outputs/desacuerdos_para_resolver.csv` (privado e ignorado por git) todas las filas donde hubo discrepancia o ambigüedad, dejando la columna `tema_final` vacía para que ambos anotadores acuerden el consenso humano.
2. **Paso 2 (Evaluación Formal contra Reglas Congeladas):**  
   Una vez los anotadores hayan resuelto y completado la columna `tema_final` en `desacuerdos_para_resolver.csv`, se vuelve a ejecutar el script (o pasando `--consenso ruta/al/archivo.csv`). El script calcula:
   * Precisión y Recall por categoría (ponderados por plataforma y sin ponderar).
   * Intervalos de confianza de Wilson al 95 % para precisión y recall.
   * Regla de supresión de grupos pequeños: las categorías con soporte menor a 10 ($n < 10$) se marcan explícitamente como "no interpretables".
   * Cobertura real y fugas hacia las categorías de respaldo ("Otros temas no identificados" y "Sin contenido temático suficiente").
   * Reportes agregados anónimos en `outputs/evaluation_themes.json` y `outputs/evaluation_themes.md`, registrando el hash `theme_rules_sha256`.

## Limitaciones

- El acuerdo entre personas no demuestra que la etiqueta acordada sea una verdad absoluta; sirve para detectar ambigüedad y fijar una referencia reproducible.
- La muestra es pequeña y estratificada por plataforma; no representa proporcionalmente el volumen total recolectado.
- La taxonomía temática opera con reglas léxicas definidas manualmente; la muestra de validación humana ($n=198$) proporciona una evaluación descriptiva del acuerdo y cobertura, mas no una garantía infalible para el 100 % del corpus.
- No se deben alterar las etiquetas originales para forzar coincidencias artificiales con los modelos.
