# Propuesta del proyecto: temas y emociones en comentarios de redes de Unillanos

## Resumen y alcance

Esta propuesta define el alcance inicial; el desarrollo ejecutado y sus resultados están documentados en `PLAN_MAESTRO.md`, en los README de `crisp_dm/` y en `ARTICULO_FINAL.md`.

El proyecto analizará los comentarios recolectados de las cuentas de Facebook, Instagram y YouTube de la Universidad de los Llanos para identificar los temas que aparecen y describir el sentimiento y las emociones que expresan. Los resultados se presentarán en una aplicación sencilla en Streamlit, con gráficos agregados y documentación para reproducir el análisis.

El trabajo se limita a los comentarios disponibles en el archivo unificado. No medirá cambios a lo largo del tiempo, no comparará comentarios principales con respuestas y no pretende representar la opinión de toda la comunidad universitaria. En este proyecto “sentimiento” se refiere a polaridad (positivo, negativo o neutral) y “emoción” a categorías como alegría, tristeza o enojo; son tareas relacionadas pero distintas.

**Objetivo general:** identificar y describir los principales temas, sentimientos y emociones expresados en los comentarios recolectados de las redes institucionales de Unillanos, mediante análisis exploratorio y modelos de lenguaje en español, y comunicar los resultados en una aplicación interactiva.

**Objetivos específicos:**

1. Revisar la calidad y cobertura de los comentarios y preparar una tabla analítica reproducible.
2. Identificar temas recurrentes mediante exploración de palabras/frases y codificación temática de una muestra.
3. Estimar sentimiento y emoción con `pysentimiento` y revisar sus predicciones en una muestra etiquetada manualmente.
4. Mostrar distribuciones y hallazgos mediante gráficos comprensibles en Streamlit, indicando alcance y limitaciones.

### Preguntas que sí aborda el proyecto

- ¿Qué temas recurrentes aparecen en los comentarios?
- ¿Qué proporción de los comentarios se clasifica como positivo, negativo o neutral?
- ¿Qué emociones identifica el modelo entre las categorías que ofrece para español?
- ¿Cómo varían los temas, sentimientos y emociones entre plataformas y tipos de publicación, con cautela ante sus diferentes volúmenes?

No se plantean preguntas sobre evolución temporal, diferencias entre respuestas y comentarios principales ni el efecto de emojis como una pregunta de investigación independiente.

## Revisión preliminar del conjunto de datos

El archivo `data/final/comments_unified.csv` contiene **16.471 comentarios** y 32 campos que incluyen plataforma, texto, fecha, publicación asociada, respuestas, “me gusta” y algunos datos de las publicaciones. La revisión preliminar encontró:

| Plataforma | Comentarios | Publicaciones/videos asociados | Con emoji o símbolo* | Solo símbolos/emojis* |
|---|---:|---:|---:|---:|
| Facebook | 12.089 | 2.038 | 1.741 (14,4 %) | 193 (1,6 %) |
| Instagram | 4.152 | 1.109 | 2.492 (60,0 %) | 1.100 (26,5 %) |
| YouTube | 230 | 105 | 55 (23,9 %) | 14 (6,1 %) |
| **Total** | **16.471** | — | **4.288 (26,0 %)** | **1.307 (7,9 %)** |

\* Estimación automática preliminar por caracteres Unicode; puede contar algunos símbolos gráficos como emojis y no equivale a una clasificación semántica.

Unos **2.502 comentarios (15,2 %)** están marcados como respuestas o anidados: 2.111 de Facebook, 364 de Instagram y 27 de YouTube. El archivo tiene IDs únicos y fechas no vacías en la revisión inicial. YouTube tiene un volumen pequeño en comparación con las demás plataformas, por lo que sus gráficos deben mostrar el número de casos y sus conclusiones serán exploratorias.

El volumen por plataforma no es directamente comparable: no hay datos de alcance/impresiones que permitan normalizarlo y las plataformas pueden tener audiencias, formas de recolección y formatos distintos. Algunos campos también faltan por diseño en ciertas plataformas. La primera fase debe confirmar qué tan completa fue la extracción.

## Decisiones de preparación: emojis y respuestas

### Emojis: conservar y convertir, no eliminar

Los emojis aportan señales de tono y emoción, en especial en Instagram, donde aparecen en aproximadamente 6 de cada 10 comentarios. Además, 1.307 comentarios parecen estar compuestos únicamente por emojis o símbolos. Eliminarlos antes del análisis borraría una parte importante del significado y de la señal afectiva. Se conservará siempre el texto original; en una columna de trabajo se probará la normalización de emojis a descripciones textuales. `pysentimiento` ofrece `preprocess_tweet`, un preprocesador para texto de redes que maneja elementos como usuarios, URL, hashtags y emojis; su documentación muestra la conversión de emojis a etiquetas descriptivas. La configuración de idioma de las descripciones debe comprobarse con ejemplos antes de aplicarla al conjunto. ([Repositorio oficial y preprocesamiento](https://github.com/pysentimiento/pysentimiento))

Para ajustarse a tres días, no se hará un experimento amplio para medir causalmente cuánto “aportan” los emojis al modelo. La decisión práctica será mantenerlos y usar una representación textual si queda natural y comprensible en español. Se revisarán manualmente ejemplos cortos, emoji-texto y solo-emojis. Los que consistan solo en emojis se marcarán como “solo emojis”; se mostrarán aparte o se considerarán no clasificables si el modelo no entrega una interpretación suficientemente confiable. No se asignará automáticamente un sentimiento fijo a cada emoji.

### Respuestas/anidados: mantenerlos, sin analizarlos como hilos

Se recomienda mantener las respuestas porque representan el 15,2 % del conjunto y pueden contener opiniones, solicitudes o emociones relevantes. Excluirlas reduciría los datos y podría sesgar los temas observados. Se conservará el indicador de respuesta para poder distinguirlas técnicamente, pero no se estudiará la diferencia entre respuesta y comentario principal. El análisis clasificará cada texto por separado, sin inferir contexto de la cadena; respuestas muy breves o cuyo sentido dependa claramente del comentario anterior se etiquetarán como insuficientes/no clasificables en la revisión manual. Se quitarán solo filas vacías, duplicados confirmados y registros que no sean comentarios analizables, dejando registro de cuántos se excluyeron.

## Uso de `pysentimiento`

La biblioteca permite analizar **sentimiento en español** con clases POS, NEG y NEU, y **emoción en español** con alegría, enojo, tristeza, miedo, sorpresa, disgusto y la clase `others` (sin emoción básica identificada/neutral). La configuración del modelo ejecutado devuelve literalmente `others`; la app conserva esa distinción. También tiene detección de ironía, pero no se incluyó en el alcance. ([Tareas y clases disponibles](https://github.com/pysentimiento/pysentimiento/blob/master/docs/TASKS.md), [configuración del modelo de emociones](https://huggingface.co/pysentimiento/robertuito-emotion-analysis/blob/main/config.json))

La propuesta es usarla como modelo preentrenado de referencia, no como verdad. El repositorio informa en sus benchmarks resultados moderados para español (por ejemplo, alrededor de 70 de macro-F1 en sentimiento y 55 en emoción para RoBERTuito); son cifras de conjuntos de evaluación de los autores, no una garantía de desempeño en comentarios de Unillanos. Los datos breves, regionalismos, ironía, contexto faltante y lenguaje institucional pueden inducir errores. Por eso se etiquetará manualmente una muestra pequeña y diversa, y se reportarán errores y limitaciones. ([Resultados publicados por el proyecto](https://github.com/pysentimiento/pysentimiento/blob/master/docs/TASKS.md#results))

En la muestra manual, cada comentario se revisará con una guía corta que defina positivo/negativo/neutral, las emociones y “no clasificable/ambiguo”. Se sugiere que dos integrantes etiqueten de forma independiente al menos 100 comentarios, incluyendo plataformas, mensajes con y sin emojis y textos cortos; discutirán desacuerdos y contrastarán con las predicciones. Esta comprobación no constituye una validación estadística robusta, pero ayuda a detectar errores evidentes. Se reportarán proporciones de acuerdo y ejemplos anonimizados, además de métricas por clase si las etiquetas alcanzan para calcularlas. No se deben combinar sentimiento y emoción en una sola etiqueta: una persona puede expresar una emoción negativa con texto neutral o mixto.

Para temas, no se recomienda entrenar un modelo complejo en este plazo. Se usará una exploración de términos/frases y una codificación temática simple revisada manualmente, consolidando un número manejable de categorías descriptivas. Los temas deben nombrarse a partir de ejemplos reales revisados, no solo de palabras más frecuentes.

## Plan CRISP-DM para dos personas en tres días

El plan concentra el trabajo en seis fases pequeñas. Los dos integrantes pueden repartirse análisis/documentación y aplicación/visualización, revisando mutuamente las decisiones. No requiere datos nuevos, entrevistas ni validación de actores externos. La aplicación se construye con resultados ya procesados, para que no ejecute el modelo pesado cada vez que alguien abre Streamlit.

| Día | Fases CRISP-DM | Resultado esperado |
|---|---|---|
| 1 | Comprensión del negocio, comprensión y preparación de datos | Alcance cerrado, tabla analítica y muestra manual listas |
| 2 | Modelado y análisis, evaluación | Temas, predicciones de sentimiento/emoción y revisión manual completadas |
| 3 | Despliegue/documentación y cierre de evaluación | Aplicación local, informe breve y README listos |

Para repartir el trabajo, una persona puede liderar preparación, etiquetado y revisión del modelo mientras la otra arma la estructura de Streamlit y los gráficos con datos de muestra; al cerrar el día 2 integran los resultados reales y revisan juntos las conclusiones.

### 1. Comprensión del negocio

**Tareas:** acordar objetivo, audiencia académica, alcance y definiciones de sentimiento, emoción y tema; confirmar que se excluye evolución temporal; decidir qué gráficos responderán las preguntas.

**Entregable:** una página de planteamiento con objetivo, preguntas y exclusiones.

**Cierre:** ambos integrantes pueden explicar en una frase qué se quiere identificar y qué no se afirmará con estos datos.

### 2. Comprensión de los datos

**Tareas:** revisar columnas, conteos por plataforma, vacíos, duplicados, cobertura, respuestas y comentarios solo emoji; inspeccionar una muestra pequeña anonimizada; anotar campos no comparables.

**Entregable:** resumen de calidad y diccionario breve de los campos usados.

**Cierre:** se identifican las filas utilizables y las limitaciones principales, y el análisis puede continuar sin depender de información externa.

### 3. Preparación de datos

**Tareas:** preservar el CSV original; preparar un archivo derivado con texto original, texto normalizado, indicador de emoji, indicador de respuesta, plataforma, publicación y campos analíticos; aplicar normalización de `pysentimiento` y revisar manualmente ejemplos; excluir solo vacíos/duplicados confirmados/no analizables.

**Entregable:** conjunto de trabajo reproducible y tabla de exclusiones.

**Cierre:** el análisis y la aplicación usan el mismo archivo preparado; ninguna transformación destruye el texto fuente.

### 4. Modelado y análisis

**Tareas:** ejecutar los analizadores de sentimiento y emoción de `pysentimiento`; seleccionar y etiquetar manualmente la muestra; inspeccionar predicciones y errores; calcular distribución por clase; extraer términos/frases y consolidar temas manualmente; agregar resultados por plataforma y tipo de publicación, mostrando denominadores.

**Entregable:** archivo de resultados por comentario (sin datos personales en la salida compartida), categorías temáticas y gráficos preliminares.

**Cierre:** cada categoría y cifra tiene definición, denominador y al menos una revisión de plausibilidad; resultados inciertos se marcan como exploratorios.

### 5. Evaluación

**Tareas:** contrastar predicciones contra la muestra manual; revisar confusiones de neutral/positivo/negativo y emociones; comprobar casos de emojis y respuestas cortas; ajustar exclusiones o etiquetas si hay errores sistemáticos; redactar límites.

**Entregable:** nota de evaluación, ejemplos de errores anonimizados y decisiones finales del método.

**Cierre:** el equipo no presenta la salida del modelo como certeza y puede explicar las principales formas en que se equivoca.

### 6. Despliegue y documentación

**Tareas:** crear una aplicación Streamlit con resumen general, gráficos de temas, sentimiento y emociones, filtros por plataforma/tipo de publicación y notas de interpretación; no incluir gráficos de evolución temporal. Escribir `README` con propósito, datos utilizados, metodología, dependencias e instrucciones para ejecutar la app. Usar tablas agregadas o anonimizadas y no mostrar nombres, IDs de autor, enlaces a perfiles ni texto completo de comentarios. Ejecutar localmente para la entrega; el alojamiento público es opcional y solo si el curso lo requiere y se puede publicar con datos seguros.

**Entregable:** aplicación local funcional, README, script/notebook reproducible, resultados procesados y presentación/informe breve.

**Cierre:** desde un entorno limpio se puede seguir el README para ejecutar la aplicación y explorar gráficos cuyos títulos aclaran sus denominadores y limitaciones.

**Condición de viabilidad:** el plazo no da para depurar exhaustivamente modelos ni construir un sistema de temas avanzado. Si la descarga de modelos o la memoria del equipo impide procesar todos los textos, se procesará por lotes o se reducirá la muestra analítica, informando el tamaño y método de selección. La clasificación y la app deben usar resultados guardados, no hacer inferencia completa en cada sesión.

## Aplicación y resultados que mostrará

Se recomienda una aplicación pequeña en Streamlit con estas vistas:

- **Resumen:** total de comentarios analizables y distribución por plataforma.
- **Temas:** barras de las categorías identificadas y frecuencia de términos/frases relevantes.
- **Sentimiento:** porcentajes de positivo, negativo y neutral, con cantidad de comentarios como denominador.
- **Emociones:** distribución entre las categorías de `pysentimiento` en español, incluida `others` (sin emoción básica identificada/neutral).
- **Filtros:** plataforma y tipo de publicación, si la calidad y el volumen lo permiten.
- **Método y límites:** descripción corta del modelo, la revisión manual, los casos no clasificables y la advertencia de que no es representativo de toda la comunidad.

No se recomienda mostrar ejemplos de comentarios o tablas de registros a nivel individual en una aplicación abierta. El volumen por plataforma debe mostrarse junto al porcentaje para que YouTube no parezca comparable estadísticamente con Facebook o Instagram cuando su muestra es mucho menor.

## Criterios generales de éxito

- El análisis temático y de sentimiento/emoción puede reproducirse desde archivos y pasos documentados.
- Las predicciones de `pysentimiento` se revisan contra etiquetas humanas, con limitaciones explícitas.
- Las decisiones sobre emojis y respuestas conservan la información que puede aportar valor y no exceden lo que permite el plazo.
- La aplicación muestra gráficos interactivos sin datos personales identificables y funciona localmente siguiendo el README.
- El informe distingue los comentarios recolectados de la opinión de toda la comunidad universitaria.

## Fuentes consultadas

- [Repositorio oficial de pysentimiento](https://github.com/pysentimiento/pysentimiento): instalación, analizadores y preprocesamiento.
- [Tareas y resultados de pysentimiento](https://github.com/pysentimiento/pysentimiento/blob/master/docs/TASKS.md): idiomas, clases y resultados reportados por el proyecto.
