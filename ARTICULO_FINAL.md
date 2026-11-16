# Temas, sentimiento y emociones en comentarios de redes sociales de la Universidad de los Llanos

## Resumen

Este proyecto presenta un análisis exploratorio de 16.471 comentarios recopilados de publicaciones institucionales de Facebook, Instagram y YouTube. Se siguió CRISP-DM para auditar y preparar los datos, estimar sentimiento y emoción en español con `pysentimiento`, proponer categorías temáticas mediante reglas léxicas y construir una aplicación Streamlit con resultados agregados. Tras retirar 586 registros sin texto y no encontrar IDs duplicados, se analizaron 15.885 comentarios. El sentimiento estimado fue neutral en 58,2 %, positivo en 27,1 % y negativo en 14,6 %. La clase emocional más frecuente fue `others` (66,8 %), seguida de alegría (24,7 %). La categoría temática residual alcanzó 66,0 %, lo cual muestra que el diccionario inicial no cubre gran parte del corpus. En una muestra de 120 comentarios anotada independientemente por dos personas, el acuerdo fue 81,7 % para sentimiento y 75,8 % para emoción. En los casos concordantes no ambiguos, el modelo obtuvo accuracy de 74,4 % para sentimiento y 74,6 % para emoción. Un análisis exploratorio por confianza encontró 92,9 % de accuracy en 56 casos con confianza ≥0,7, pero el umbral se examinó sobre la misma muestra pequeña y no constituye validación independiente. Los emojis y las respuestas se conservaron; no se hizo análisis temporal ni comparación de hilos.

**Palabras clave:** CRISP-DM, análisis de sentimiento, emociones, redes sociales, comentarios, Streamlit.

## 1. Introducción

Los comentarios en redes sociales contienen señales sobre asuntos que generan reconocimiento, consultas, inquietudes y reacciones emocionales. Su análisis automatizado permite organizar grandes colecciones para exploración, aunque los textos breves, la ironía, el contexto conversacional incompleto y los emojis dificultan la interpretación. Las etiquetas de un modelo no equivalen a opiniones verificadas ni representan por sí solas a toda la comunidad universitaria.

El proyecto organiza los comentarios disponibles de las cuentas institucionales de la Universidad de los Llanos en tres dimensiones: temas sugeridos, polaridad del sentimiento y emociones estimadas. El resultado es una herramienta descriptiva para explorar el conjunto capturado, con sus límites visibles.

## 2. Objetivos y alcance

### Objetivo general

Identificar y describir temas, sentimiento y emociones en los comentarios recopilados de Facebook, Instagram y YouTube de Unillanos, mediante un flujo reproducible CRISP-DM y una aplicación de visualización interactiva.

### Objetivos específicos

1. Auditar cobertura, estructura, faltantes y calidad de los datos.
2. Preparar textos y metadatos sin alterar ni publicar los originales.
3. Estimar sentimiento y emoción con modelos preentrenados en español y proponer categorías temáticas mediante reglas transparentes.
4. Comparar anotaciones independientes de dos personas y documentar el acuerdo y el alcance exploratorio de las métricas.
5. Comunicar resultados agregados y limitaciones en Streamlit.

El análisis es transversal y descriptivo. Se excluyeron evolución temporal, comparación entre respuestas y comentarios principales, análisis de usuarios, causalidad y generalizaciones a toda la comunidad. Se conservaron respuestas como unidades textuales individuales, sin contexto del hilo.

## 3. Datos

La entrada unificada contiene **16.471 filas** y 32 columnas: 12.089 de Facebook, 4.152 de Instagram y 230 de YouTube. Los comentarios se vincularon a 3.252 publicaciones o videos. No se detectaron IDs de comentario duplicados. Se excluyeron 586 filas con texto vacío, quedando **15.885** textos analizables: 11.529 de Facebook, 4.126 de Instagram y 230 de YouTube.

De los registros iniciales, 2.502 estaban marcados como respuestas; 2.484 de ellas con texto se conservaron en el conjunto preparado. La tabla analítica retuvo la fuente, tipo de publicación y banderas útiles, pero el conjunto por comentario contiene texto e identificadores y se mantiene local. Los agregados de la aplicación no incluyen texto, autor, IDs, URL ni fecha.

## 4. Metodología: CRISP-DM ejecutado

### 4.1 Comprensión del negocio

Se definió como propósito apoyar la exploración académica de los comentarios recopilados, no medir satisfacción institucional ni representar a todos los estudiantes o ciudadanos. Se acotaron preguntas a temas recurrentes y distribución descriptiva de sentimiento y emociones. La fase quedó documentada en `crisp_dm/01_business_understanding/README.md` y el alcance consolidado en `PLAN_MAESTRO.md`.

### 4.2 Comprensión de los datos

El script `crisp_dm/02_data_understanding/audit.py` perfiló tamaños, campos, faltantes, duplicados, plataformas, respuestas y contenido textual. Se detectó cobertura muy desigual: YouTube aporta 230 filas, frente a más de once mil de Facebook. Por eso los conteos absolutos no son comparables como tasas de reacción o alcance. Se registraron 4.288 comentarios con indicios de emojis/símbolos y 1.280 textos identificados como solo emoji en la preparación; los detectores son heurísticos. Los detalles y el diccionario están en `crisp_dm/02_data_understanding/outputs/`.

### 4.3 Preparación

`crisp_dm/03_data_preparation/prepare.py` retiró los textos vacíos, normalizó texto para inspección, mantuvo la forma original para el modelado y preservó respuestas. No se eliminaron emojis: `pysentimiento` los procesa internamente y el análisis auxiliar los representa mediante descripciones en texto. Esta representación puede aportar señales de aprobación o afecto, aunque sus palabras (“aplaudiendo”, “corazones”) pueden inflar frecuencias léxicas y no equivalen a menciones literales. Los textos compuestos únicamente por emojis se identifican como tales, pero no se forzó una etiqueta alternativa.

Se generaron una muestra de evaluación de **120 comentarios** (40 por plataforma) y una muestra para revisar temas de **198 comentarios** (66 por plataforma). Ambas contienen texto e identificadores internos, son productos locales y no forman parte del paquete de despliegue.

En los 15.885 textos preparados, 1.280 (8,1 %) son solo emojis y 2.728 (17,2 %) tienen dos palabras o menos. La longitud se usa como indicador de posible información limitada, no como criterio para eliminar: los comentarios cortos pueden comunicar una opinión, una pregunta o una reacción válida.

### 4.4 Modelado

El sentimiento se estimó con `pysentimiento.create_analyzer(task="sentiment", lang="es")`; la emoción con `create_analyzer(task="emotion", lang="es")`. Se aplicaron los analizadores a los 15.885 comentarios y se guardaron etiquetas, probabilidades y metadatos localmente. Los modelos son clasificadores preentrenados; las etiquetas no son anotaciones humanas.

Para temas se calcularon frecuencias de unigramas y bigramas y se aplicaron reglas léxicas mutuamente excluyentes definidas en `theme_rules.json`. Son categorías exploratorias, no tópicos aprendidos ni una codificación semántica revisada comentario por comentario. La categoría “Otros / tema no identificado” es residual y no debe interpretarse como tema cohesivo.

**Sentimiento estimado:**

| Clase | N | % |
|---|---:|---:|
| Neutral (NEU) | 9.250 | 58,2 |
| Positivo (POS) | 4.312 | 27,1 |
| Negativo (NEG) | 2.323 | 14,6 |

**Emoción estimada:**

| Clase | N | % |
|---|---:|---:|
| Otros / sin emoción básica clara (`others`) | 10.615 | 66,8 |
| Alegría (`joy`) | 3.916 | 24,7 |
| Enojo (`anger`) | 799 | 5,0 |
| Tristeza (`sadness`) | 466 | 2,9 |
| Sorpresa (`surprise`) | 79 | 0,5 |
| Miedo (`fear`) | 9 | 0,1 |
| Disgusto (`disgust`) | 1 | <0,1 |

La configuración del modelo instalado usa la etiqueta `others`, mientras que la ficha del modelo describe esa clase como neutral/sin una emoción básica identificada. Para evitar confundirla con la etiqueta NEU del modelo de sentimiento, se muestra como “Otros / sin emoción básica clara”.

**Temas asignados por reglas:**

| Categoría exploratoria | N | % |
|---|---:|---:|
| Otros / tema no identificado | 10.486 | 66,0 |
| Felicitaciones y reconocimiento | 2.346 | 14,8 |
| Vida académica e investigación | 989 | 6,2 |
| Información y trámites | 914 | 5,8 |
| Admisiones e inscripciones | 579 | 3,6 |
| Programas de acceso y bienestar | 459 | 2,9 |
| Eventos y actividades | 112 | 0,7 |

Las palabras frecuentes incluyeron “manos”, “aplaudiendo”, “felicitaciones”, “gracias”, “excelente”, “corazones”, “educación”, “estudiantes” y “matrícula”. Parte de las primeras procede de la descripción automática de emojis. La gran proporción residual apunta a ampliar y revisar las reglas antes de usar temas como una taxonomía final.

### 4.5 Evaluación

La muestra estratificada contiene 120 comentarios (40 por plataforma), etiquetados de forma independiente por dos personas para sentimiento y emoción. El acuerdo se calculó en todas las filas con ambas etiquetas; las etiquetas ambiguas también cuentan como acuerdo cuando ambos anotadores las asignaron. Las métricas del modelo se calcularon solo en casos concordantes y no ambiguos.

| Tarea | Acuerdo entre anotaciones | N con acuerdo y no ambiguos | Accuracy del modelo | Macro-F1 |
|---|---:|---:|---:|---:|
| Sentimiento | 81,7 % (98/120) | 78 | 74,4 % | 0,739 |
| Emoción | 75,8 % (91/120) | 67 | 74,6 % | 0,429 |

Estas métricas comparan el modelo con las etiquetas acordadas solo donde ambas personas coinciden y no hay ambigüedad. Este filtro puede favorecer los casos más claros y elevar las métricas frente al conjunto entero. La muestra es pequeña; para emoción, varias clases tuvieron muy pocos o ningún caso concordante válido. El macro-F1 promedia las siete clases y asigna cero a las clases sin soporte en esta muestra, por lo que no es una estimación estable del desempeño general.

Como diagnóstico adicional, se midió la exactitud selectiva del sentimiento al excluir predicciones con menor confianza. Con umbral ≥0,7, 52 de 56 predicciones evaluables coincidieron con la anotación humana (92,9 %), cubriendo 71,8 % de los 78 casos concordantes no ambiguos. En el corpus completo, 8.235 de 15.885 predicciones (51,8 %) alcanzan ese umbral. Este corte se eligió después de observar varios umbrales sobre la misma muestra; la exactitud puede estar sobreestimada y debe leerse como evidencia exploratoria. La app muestra esta banda separada y mantiene intactas las etiquetas originales.

### 4.6 Despliegue

Se construyó una app Streamlit con pestañas de resumen, temas, sentimiento, emociones y método, con filtros por plataforma y tipo de publicación. Los gráficos usan conteos agregados; los grupos menores de diez se agrupan. La pestaña de sentimiento incluye bandas de confianza y una métrica de cobertura para el umbral exploratorio de 0,7; no cambia las etiquetas. La app advierte que la evaluación usa una muestra pequeña y casos concordantes no ambiguos. No incluye fechas ni evolución temporal.

El paquete autocontenido para despliegue está en `crisp_dm/06_deployment/deploy_bundle/`: incluye `app.py`, dependencias ligeras y cinco archivos de datos agregados. Debe usarse como raíz de un repositorio separado, no desplegarse desde la raíz del repositorio de análisis, que contiene datos originales. El despliegue remoto queda a cargo del usuario.

## 5. Reproducibilidad

Con el entorno y dependencias documentados en `README.md` y `requirements.txt`, el flujo se ejecuta en este orden. El CSV se reconstruyó desde los JSON locales usando `unify_raw_data.py`; la prueba se escribió a un archivo separado y su SHA-256 coincidió con la entrada canónica.

```powershell
# Opcional: reconstruir data/final/comments_unified.csv desde data/raw/.
python crisp_dm/02_data_understanding/unify_raw_data.py
python crisp_dm/02_data_understanding/audit.py
python crisp_dm/03_data_preparation/prepare.py
python crisp_dm/04_modeling/analyze.py
python crisp_dm/05_evaluation/evaluate.py
python crisp_dm/06_deployment/build_app_data.py
streamlit run crisp_dm/06_deployment/deploy_bundle/app.py
```

La inferencia completa se ejecutó sobre CPU. La preparación fija semilla para las muestras. Las salidas detalladas con texto permanecen fuera del paquete público. La configuración y las versiones instaladas están registradas en los archivos del proyecto.

## 6. Limitaciones

1. **Evaluación exploratoria:** las métricas se calculan en un subconjunto concordante no ambiguo de una muestra de 120 comentarios; el filtrado puede favorecer los casos claros y no permite generalizar al corpus completo.
2. **Umbral de confianza exploratorio:** el corte 0,7 se escogió tras comparar su resultado en la misma muestra usada para evaluar; no es calibración independiente, y su accuracy selectiva puede estar sobreestimada.
3. **Temas exploratorios:** reglas léxicas simples no resuelven sinonimia, ironía, polisemia ni temas nuevos; 66 % quedó en la categoría residual. La muestra temática aún no tiene etiquetas humanas.
4. **Desbalance de plataformas:** el tamaño de la recolección varía mucho y no hay denominadores de impresiones o alcance.
5. **Contexto limitado:** las respuestas se analizaron individualmente sin su hilo; comentarios como “sí” pueden ser ambiguos.
6. **Emojis:** conservarlos evita perder señales potenciales, pero su interpretación depende del contexto y las descripciones automáticas afectan frecuencias de términos.
7. **Cobertura:** la extracción disponible no necesariamente representa todas las publicaciones o comentarios de las cuentas.
8. **Clases raras:** algunas emociones aparecen con muy baja frecuencia; sus porcentajes no deben sobreinterpretarse.

Los benchmarks publicados por los autores de `pysentimiento` no son métricas de este estudio y no se trasladan como garantía de desempeño local.

## 7. Conclusiones

Se completó un flujo reproducible CRISP-DM desde la auditoría hasta una app Streamlit local, aplicando modelos en español a 15.885 comentarios con texto. Las estimaciones muestran predominio de sentimiento neutral y de la clase `others` en emoción; la regla temática inicial solo identificó categorías específicas en cerca de un tercio del corpus. La banda de confianza muestra un modo más prudente de explorar el sentimiento, aunque su resultado alto procede de una muestra pequeña y no independiente. Los resultados sirven para explorar y generar hipótesis sobre los comentarios capturados, no para medir la opinión de toda la comunidad.

La decisión metodológica fue conservar emojis y respuestas: pueden aportar contenido temático y afectivo y su eliminación habría borrado señales, aunque se documentó el riesgo de ruido. No se analizaron comparativamente las respuestas ni se hizo experimento de ablación de emojis, conforme al alcance. El trabajo futuro es revisar los desacuerdos de las anotaciones humanas y ampliar las reglas de temas con una codificación manual de la muestra temática; después se pueden actualizar los agregados.

## Referencias técnicas

- Pérez, J. M. et al. (2021). *pysentimiento: A Python Toolkit for Sentiment Analysis and SocialNLP tasks*. [Repositorio y documentación](https://github.com/pysentimiento/pysentimiento).
- Modelo de emoción en español. [Ficha y configuración de `pysentimiento/robertuito-emotion-analysis`](https://huggingface.co/pysentimiento/robertuito-emotion-analysis).
- Streamlit. [Documentación oficial](https://docs.streamlit.io/).

## Artefactos del proyecto

- Plan y alcance: `PLAN_MAESTRO.md`.
- Registro operativo y avance: `FLUJO_DE_TRABAJO.md`.
- Documentación por fase: `crisp_dm/01_business_understanding/` a `crisp_dm/06_deployment/`.
- Aplicación canónica y paquete: `crisp_dm/06_deployment/deploy_bundle/app.py`.
