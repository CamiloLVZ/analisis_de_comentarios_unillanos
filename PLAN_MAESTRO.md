# Plan maestro del proyecto CRISP-DM

## 1. Identificación y propósito

**Título:** Temas, sentimiento y emociones en los comentarios de redes sociales de la Universidad de los Llanos.

**Propósito:** construir un análisis exploratorio reproducible sobre los comentarios recolectados de las cuentas institucionales de Facebook, Instagram y YouTube y presentar sus resultados agregados en una aplicación Streamlit que el equipo pueda ejecutar y desplegar.

**Unidad principal:** comentario individual disponible en `data/final/comments_unified.csv`. Se conservan comentarios principales y respuestas, pero no se modela la estructura de los hilos. La interpretación de cada comentario se hace sin contexto conversacional, por lo que textos dependientes de contexto pueden ser ambiguos.

## 2. Objetivos

### Objetivo general

Identificar y describir los principales temas, la polaridad del sentimiento y las emociones expresadas en los comentarios recolectados de las redes institucionales de Unillanos mediante análisis de contenido, modelos preentrenados en español y revisión manual, comunicando resultados y limitaciones en Streamlit.

### Objetivos específicos

1. Auditar la calidad, cobertura, estructura y privacidad de los datos existentes.
2. Preparar una tabla analítica preservando el texto original y documentando normalizaciones/exclusiones.
3. Explorar temas mediante frecuencias y reglas léxicas transparentes, revisando una muestra para orientar futuras mejoras; presentar las reglas como categorías exploratorias.
4. Aplicar `pysentimiento` para estimar sentimiento (POS/NEG/NEU) y emoción en español (alegría, enojo, tristeza, miedo, sorpresa, disgusto y `others`, clase sin emoción básica identificada/neutral).
5. Evaluar predicciones en una muestra revisada por dos integrantes y hacer visibles las limitaciones.
6. Construir una app local/publicable que muestre resúmenes agregados sin exponer información identificable.

## 3. Preguntas de investigación

- ¿Qué temas recurrentes se observan en los comentarios recolectados?
- ¿Cómo se distribuyen las etiquetas de sentimiento y emoción estimadas por el modelo?
- ¿Qué variación descriptiva se observa entre plataformas y tipos de publicación, teniendo en cuenta sus diferentes tamaños de muestra?

**Fuera de alcance:** evolución temporal; comparación entre respuestas y comentarios principales; estudio independiente del aporte de emojis; clasificación de usuarios; análisis causal; estimación de opinión de toda la comunidad; scraping adicional; decisiones o respuesta automática; despliegue remoto realizado por Codex.

## 4. Datos disponibles y supuestos a verificar

El perfil preliminar del archivo unificado reportó 16.471 comentarios: Facebook 12.089, Instagram 4.152 y YouTube 230. Se asociaron a 2.038 publicaciones de Facebook, 1.109 de Instagram y 105 videos de YouTube. Alrededor de 26 % contienen algún emoji/símbolo según un conteo heurístico, y unos 1.307 parecen ser solo emojis/símbolos. Cerca de 2.502 filas (15,2 %) están marcadas como respuestas. Esas cifras deben ser reproducidas por la fase 2 con el script del proyecto antes de presentarse como resultados.

Supuestos: el archivo unificado es la mejor entrada disponible; identificadores no repetidos son locales a la plataforma; los comentarios están predominantemente en español; el alcance de la recolección no se presume exhaustivo; las diferencias por plataforma son descriptivas y no comparaciones representativas.

## 5. Resultados previstos

- `data/processed/`: tabla analítica y predicciones a nivel comentario, restringidas a uso local si contienen texto.
- `crisp_dm/06_deployment/deploy_bundle/data/app/`: archivos agregados y anonimizados que consume Streamlit.
- App con resumen, temas, sentimiento, emociones y filtros por plataforma/tipo de publicación; sin series temporales ni filas de usuarios.
- Informe simplificado en `ARTICULO_FINAL.md` con método, resultados obtenidos, limitaciones y conclusiones.
- Guías CRISP-DM en `crisp_dm/NN_*/README.md`, README de ejecución y scripts reproducibles.

## 6. Plan de fases, productos y criterios de salida

| Fase | Objetivo y trabajo | Productos principales | Criterio de cierre |
|---|---|---|---|
| 1. Comprensión del negocio | Delimitar problema, audiencia académica, objetivo, preguntas, alcance, riesgos y éxito. | `crisp_dm/01_business_understanding/README.md`, acta de alcance y plan. | Preguntas alineadas con campos disponibles; exclusiones explícitas; no se promete representatividad. |
| 2. Comprensión de datos | Si hace falta, unificar los JSON ya recolectados; auditar esquema, tamaños, faltantes, duplicados y cobertura. | `crisp_dm/02_data_understanding/unify_raw_data.py`, `audit.py`, README, perfil y diccionario. | CSV unificado reconstruible desde los archivos locales; calidad y limitaciones documentadas. |
| 3. Preparación | Validar IDs, tipos y textos; conservar fuente; crear versión normalizada y banderas; identificar vacíos/duplicados/no clasificables. | `crisp_dm/03_data_preparation/README.md`, reglas, datos derivados locales. | Preparación ejecutable desde CSV; recuentos antes/después documentados; texto original intacto. |
| 4. Modelado | Aplicar analizadores de sentimiento y emoción; explorar frecuencias y sugerir categorías con reglas léxicas transparentes revisables; persistir resultados. | `crisp_dm/04_modeling/README.md`, código, resultados locales y reglas temáticas. | Completada: resultados y reglas reproducibles; temas descritos explícitamente como exploratorios, no validados semánticamente. |
| 5. Evaluación | Comparar anotaciones independientes de dos personas para sentimiento y emoción; reportar acuerdo, métricas por clase y errores en casos concordantes. | `crisp_dm/05_evaluation/README.md`, muestra anotada, evaluador y reporte. | Completada: 120 casos anotados por dos personas; se explicitan el acuerdo, la selección de casos concordantes y las clases con bajo soporte. |
| 6. Despliegue | Agregar resultados, crear aplicación y documentación de ejecución/despliegue; revisar privacidad y funcionamiento. | `crisp_dm/06_deployment/README.md`, `deploy_bundle/app.py`, agregados y paquete aislado. | La app funciona localmente, usa datos agregados y no revela IDs, autores ni textos completos; el usuario puede desplegar el bundle como repo independiente. |

## 7. Plan de trabajo para dos personas / tres días

No se planifican horas. El equipo puede trabajar en paralelo en partes con interfaces definidas, con revisión cruzada diaria:

| Día | Trabajo CRISP-DM | Reparto orientativo | Resultado |
|---|---|---|---|
| 1 | Fases 1–3: alcance, auditoría, preparación; instalar dependencias y precalentar/validar modelos. | Persona A: auditoría y calidad. Persona B: entorno y estructura de app/datos. Juntos: decisiones de limpieza y etiqueta. | Datos listos y evaluación manual iniciada. |
| 2 | Fases 4–5: temas, predicción, muestra etiquetada, métricas y revisión de errores. | A: codificación de temas y muestra. B: inferencia, agregaciones y gráficos preliminares. Revisar conjuntamente desacuerdos/errores. | Resultados congelados, limitaciones escritas. |
| 3 | Fase 6 y artículo: agregar, construir app, documentación, revisión integral. | B: app. A: artículo y README. Juntos: recorrido de aceptación, corregir defectos y cerrar checklist. | App lista para que el equipo la despliegue y documentación completa. |

Alcance reducido para cumplir plazo: muestra de evaluación de 120 textos (40 por plataforma, muestreo reproducible), anotada independientemente por dos personas para sentimiento y emoción. Se generó también una muestra de revisión temática de 198 comentarios (66 por plataforma); esta no se codificó como gold standard. La clasificación temática actual usa reglas léxicas y su gran categoría residual refleja una taxonomía incompleta. Las muestras no permiten conclusiones poblacionales.

## 8. Decisiones analíticas

### Emojis

Mantener el campo original y crear texto normalizado con `pysentimiento.preprocessing.preprocess_tweet` si la prueba con ejemplos confirma una conversión adecuada. La biblioteca describe soporte de preprocesamiento de emojis; el ejemplo oficial de conversión está en inglés, por lo que no se debe dar por hecho que la descripción en español sea apropiada sin inspección. Si las etiquetas quedan en inglés o son poco naturales, conservar los emojis originales para los modelos y no eliminarlos. Los comentarios solo emoji se identifican y se muestran como grupo; predicciones muy inciertas o sin contenido léxico se reportan como no clasificables, en lugar de imponerles una etiqueta. No se dedica tiempo a un experimento causal de ablation de emojis.

### Respuestas

Conservarlas (15,2 % en el perfil inicial) porque son textos con posible información temática y emocional. Marcar `is_reply` pero no comparar grupos ni analizar hilos. Clasificar el texto individual; contexto-dependientes o demasiado breves se pueden marcar ambiguos en la revisión humana.

### Temas

Para un trabajo introductorio y corto, usar análisis de frecuencias de unigramas/bigramas y reglas léxicas legibles para categorías iniciales. Estas reglas asignan una categoría por comentario; son un mapa exploratorio, no un modelo semántico ni una codificación humana validada. La muestra de 198 comentarios queda lista para que el equipo revise y refine las reglas. No presentar el residual “Otros” como un tema único.

### Sentimiento y emociones

Usar `pysentimiento` como clasificación preentrenada. Sentimiento y emoción son dos salidas diferentes y no deben fusionarse. Cargar/ejecutar modelos solo por script y persistir resultados. Verificar una muestra de predicciones y no reportar probabilidades como certeza. La documentación del proyecto reporta aproximadamente 70 macro-F1 en sentimiento y 55 en emoción para uno de sus modelos de español en sus conjuntos benchmark; el desempeño local puede diferir notablemente. Referencia: [tareas y resultados](https://github.com/pysentimiento/pysentimiento/blob/master/docs/TASKS.md).

## 9. Evaluación y métricas

- Revisión manual independiente de 120 comentarios estratificados por plataforma. Dos personas etiquetan sentimiento y emoción; los temas permanecen como reglas exploratorias y pueden revisarse en una fase futura.
- Etiquetas: sentimiento POS/NEG/NEU/ambiguo; emoción según clases en español/ambiguo. Se omiten del cálculo de métricas las filas acordadas como no clasificables, informando cuántas fueron.
- Reportar matriz de confusión, precisión/recall/F1 por clase y macro-F1 si cada clase tiene ejemplos suficientes. Añadir proporción de acuerdo; no llamar “validación robusta” a una muestra pequeña.
- Mostrar cada porcentaje con su N. No afirmar causalidad o representatividad.

## 10. Visualizaciones de Streamlit

1. Resumen: N analizable, volumen y distribución por plataforma.
2. Temas: frecuencia/categorías y filtro de plataforma.
3. Sentimiento: barras o dona con conteos y porcentajes, acompañadas de bandas de confianza; el corte ≥0,7 es exploratorio y no recodifica predicciones.
4. Emociones: distribución por clase, con tabla aclaratoria.
5. Filtros opcionales por plataforma y tipo de publicación; retirar opciones si generan celdas muy pequeñas.
6. Método y límites visibles. Sin fechas en filtros/gráficos, comentarios completos, nombres de autor, URLs ni IDs.

## 11. Privacidad y administración de datos

Los archivos crudos y resultados por comentario pueden contener texto e identificadores; no deben copiarse a la aplicación pública ni a documentación. La app usa solo agregados. No se publicarán ejemplos buscables o capturas de perfiles. Mantener `.env` fuera de Git; el entorno, caché y archivos temporales están en `.gitignore`. Revisar los términos de las plataformas y las normas académicas aplicables antes de publicar datos, pues este proyecto no revisa autorizaciones institucionales.

## 12. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Modelo no instalado o modelos no descargables | Mantener script de instalación/ejecución documentado; fail fast, probar ejemplos antes del lote; si se bloquea, no fabricar etiquetas automáticas y restringir resultados al análisis manual, dejando estado. |
| Inferencia en CPU toma demasiado o entorno Python incompatible | Ejecutar por lotes/cachear salida; fijar versiones compatibles; usar muestra piloto antes de procesar todo. |
| Comentarios cortos, ironía, negación, emojis y contexto faltante | Revisión humana, clase ambiguo, ejemplos de error y lenguaje prudente. |
| Temas inestables | Codificar manualmente muestra y revisar vocabulario/categorías con dos integrantes. |
| Muestra desigual o cobertura incompleta | Denominadores visibles, nota de extracción y comparación descriptiva prudente. |
| Información personal publicada | Exportaciones agregadas, no presentar texto/autor/URLs; revisar archivos antes del despliegue del usuario. |

## 13. Inventario y arquitectura final

```text
FLUJO_DE_TRABAJO.md
PLAN_MAESTRO.md
README.md
ARTICULO_FINAL.md
requirements.txt
config/analysis.json
crisp_dm/01_business_understanding/README.md
crisp_dm/02_data_understanding/{README.md,unify_raw_data.py,audit.py,outputs/}
crisp_dm/03_data_preparation/{README.md,prepare.py,outputs/}
crisp_dm/04_modeling/{README.md,analyze.py,theme_rules.json,outputs/}
crisp_dm/05_evaluation/{README.md,evaluate.py,outputs/}
crisp_dm/06_deployment/{README.md,build_app_data.py,outputs/,deploy_bundle/app.py,deploy_bundle/data/app/}
scripts/legacy/             # scraping y descarga histórica
data/raw/                 # entradas existentes, no alterar
data/preparados/          # preparación con texto, local y no publicable
data/processed/           # resultados detallados del análisis actual
data/legacy/processed/    # listados y lotes históricos de scraping
crisp_dm/06_deployment/deploy_bundle/data/app/ # agregados seguros para app
```

Los scripts de extracción actuales se mantienen en `scripts/legacy/` como antecedentes, no se ejecutan durante este proyecto de análisis.

