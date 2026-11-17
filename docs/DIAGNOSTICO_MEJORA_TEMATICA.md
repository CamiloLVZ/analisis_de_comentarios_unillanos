# Diagnóstico de Mejora Temática del Proyecto CRISP-DM

**Proyecto:** Análisis de Comentarios de Redes Sociales de la Universidad de los Llanos (Facebook, Instagram, YouTube)  
**Entorno de ejecución:** Local (`c:\Users\camil\Documents\Projects\Analisis de Datos\analisis_de_comentarios_unillanos`)  
**Fecha:** 16 de noviembre de 2026  
**Autor:** Especialista Senior en Analítica de Texto, Análisis Temático y Evaluación CRISP-DM  
**Propósito:** Diagnóstico técnico, metodológico y empírico para fundamentar el plan de refactorización y consolidación temática.  
**Declaración de conectividad web:** Se intentó conectar a la URL pública de la aplicación (`https://comentarios-unillanos.streamlit.app`), pero la conexión agotó el tiempo de espera (*read operation timed out* / sin acceso a red externa). Toda la inspección de la aplicación se realizó rigurosamente sobre el código fuente local en `crisp_dm/06_deployment/deploy_bundle/app.py` y los datos agregados en `crisp_dm/06_deployment/deploy_bundle/data/app/`.

---

## 1. Resumen Ejecutivo del Diagnóstico

El proyecto ha completado de manera íntegra un ciclo CRISP-DM estructurado: desde la ingesta y unificación de 16.471 filas crudas procedentes de tres plataformas hasta el despliegue interactivo en Streamlit mediante datos agregados y anonimizados. La reproducibilidad de los datos numéricos es sólida (15.885 comentarios analizados tras la exclusión sistemática de 586 registros sin texto).

Sin embargo, el diagnóstico técnico revela una limitación crítica en el núcleo analítico:
1. **Hipertrofia de la categoría residual temática:** El 66,0 % del corpus (10.486 de 15.885 comentarios) está clasificado como `"Otros / tema no identificado"`. Esto diluye el valor de negocio de la taxonomía, pues dos de cada tres comentarios no reciben caracterización temática.
2. **Confusión ontológica en el residual:** La categoría `"Otros / tema no identificado"` mezcla indiscriminadamente textos con contenido temático identificable (no cubierto por las 6 reglas vigentes) con textos que carecen intrínsecamente de sustancia proposicional (comentarios compuestos únicamente por emojis, menciones vacías a otros usuarios, saludos mínimos y frases de una palabra).
3. **Fragilidad de reglas léxicas:** La función de coincidencia actual (`assign_theme` en `crisp_dm/04_modeling/analyze.py`) opera mediante búsqueda de subcadenas (`in`) sin delimitadores de palabra (`\b`), generando colisiones demostradas (por ejemplo, `"curso"` colisiona con `"concurso"`, `"recurso"`, `"discurso"` en 81 casos reales) y falsos positivos por palabras funcionales altamente genéricas (`"cuando"`, `"donde"`, `"cuanto"`).
4. **Asimetría en la madurez de tareas:** Mientras sentimiento y emoción cuentan con una muestra manual de evaluación con doble anotador ciego (120 filas, 78 y 67 casos concordantes no ambiguos evaluados), la taxonomía temática carece por completo de anotación humana (la muestra `theme_review_sample.csv` de 198 filas tiene todas sus columnas *gold* vacías).
5. **Alineación con el objetivo institucional:** El valor estratégico para la gestión universitaria reside prioritariamente en conocer **de qué habla la comunidad** (temas específicos de gestión, bienestar, infraestructura, admisiones, calidad académica) antes que en polaridades afectivas abstractas. Sentimiento y emoción deben reubicarse como dimensiones secundarias y condicionadas al tema.

---

## 2. Hallazgos Comprobados con Rutas y Salidas del Repositorio

A continuación se presentan los hechos comprobados empíricamente mediante inspección de código y análisis de datos en el workspace:

### 2.1 Coherencia de Datos y Trazabilidad de Filas
- **Fuente unificada:** `data/final/comments_unified.csv` contiene exactamente 16.471 filas y 32 columnas. No se encontraron `comment_id` duplicados (`quality_profile.json`).
- **Filtrado de vacíos:** Se eliminaron 586 filas con texto vacío (560 en Facebook, 26 en Instagram, 0 en YouTube), verificado en `crisp_dm/03_data_preparation/prepare.py` (L55-57) y `preparation_summary.json`.
- **Corpus preparado:** `data/preparados/prepared_comments.csv` contiene exactamente 15.885 filas:
  - Facebook: 11.529 comentarios (72,58 %)
  - Instagram: 4.126 comentarios (25,97 %)
  - YouTube: 230 comentarios (1,45 %)
- **Consistencia en agregados:** Las sumas en `crisp_dm/04_modeling/outputs/theme_counts.csv` ($N = 15.885$), `data/processed/model_outputs/scored_comments.csv` ($N = 15.885$) y los archivos del paquete de despliegue `crisp_dm/06_deployment/deploy_bundle/data/app/themes.csv` y `overview.json` ($N = 15.885$) coinciden de forma exacta.

### 2.2 Diagnóstico de la Clasificación Temática Actual
En `crisp_dm/04_modeling/theme_rules.json` y `crisp_dm/04_modeling/analyze.py`:
- **Estructura:** Se definen 6 categorías específicas ordenadas secuencialmente, más un fallback `"Otros / tema no identificado"`.
- **Mecanismo de asignación:**
  ```python
  # crisp_dm/04_modeling/analyze.py, L60-68
  def assign_theme(text: str, rules: dict) -> str:
      normalized = strip_accents(str(text).lower())
      for category in rules["categories"]:
          for keyword in category["keywords"]:
              needle = strip_accents(keyword.lower())
              if needle and needle in normalized:
                  return category["name"]
      return rules["fallback"]
  ```
- **Distribución de resultados en el corpus:**
  - `Otros / tema no identificado`: 10.486 (66,01 %)
  - `Felicitaciones y reconocimiento`: 2.346 (14,77 %)
  - `Vida académica e investigación`: 989 (6,23 %)
  - `Información y trámites`: 914 (5,75 %)
  - `Admisiones e inscripciones`: 579 (3,64 %)
  - `Programas de acceso y bienestar`: 459 (2,89 %)
  - `Eventos y actividades`: 112 (0,71 %)

### 2.3 Desglose Empírico de la Categoría Residual "Otros" ($N = 10.486$)
Al cruzar `prepared_comments.csv` con `scored_comments.csv`, la categoría residual se descompone en:
- **Comentarios solo emojis (`emoji_only`):** 1.280 comentarios (12,21 % de "Otros"). Son textos sin letras ni dígitos, que no aportan contenido temático lingüístico.
- **Comentarios ultracortos ($\le 2$ palabras):** 2.384 comentarios (22,74 % de "Otros").
- **Comentarios cortos ($\le 3$ palabras):** 3.372 comentarios (32,16 % de "Otros").
- **Menciones directas (`@usuario`):** 639 comentarios en "Otros" contienen menciones a perfiles. De ellos, 236 comentarios son exclusivamente menciones con $\le 3$ palabras (p. ej., amigos etiquetándose para ver un post).
- **Textos sustantivos no categorizados ($> 3$ palabras):** 7.114 comentarios (67,84 % de "Otros"). Este subconjunto representa el verdadero potencial de recuperación temática que la taxonomía actual ignora.

### 2.4 Colisiones Comprobadas por Búsqueda de Subcadenas
Al no emplear límites de palabra (`\b`), la función `in` genera colisiones reales comprobadas en el corpus:
- **Término `"curso"` en "Vida académica":**
  - Textos que contienen la subcadena `"curso"`: 125 comentarios.
  - Textos que contienen la palabra exacta `"curso"` o `"cursos"`: 44 comentarios.
  - **Falsos positivos directos:** 81 comentarios contienen `"concurso"`, `"recurso"`, `"discurso"` o `"transcurso"` y son absorbidos erróneamente por la regla.
- **Palabras interrogativas/funcionales en "Información y trámites":**
  - La regla incluye palabras funcionales como `"cuando"`, `"donde"`, `"cuanto"`.
  - En el corpus normalizado, `"cuando"` aparece en 467 comentarios, `"donde"` en 231 comentarios y `"cuanto"` en 64 comentarios.
  - Gran parte de estos comentarios usan las palabras en sentido narrativo o relativo (*"cuando yo estudiaba..."*, *"donde queda el recuerdo..."*) y no como solicitud de trámites ni preguntas administrativas.
- **Prioridad fija y oculta por orden en JSON:**
  - Si un comentario contiene términos de varias categorías (por ejemplo, felicitar por la admisión: *"felicitaciones por pasar la admisión"*), la regla de orden asigna siempre la categoría que aparezca antes en el array del JSON (`Admisiones e inscripciones` tiene prioridad sobre `Felicitaciones y reconocimiento`).

### 2.5 Cobertura y Naturaleza del Campo `post_text`
En `data/final/comments_unified.csv`, la columna `post_text` (texto del post/video al que pertenece el comentario) presenta:
- **Total de filas:** 16.471 | Nulos o vacíos: 118 (0,72 %)
- **Por plataforma:**
  - Facebook: 12.089 filas | 43 vacíos (0,36 % faltante) $\rightarrow$ Cobertura del 99,64 %.
  - Instagram: 4.152 filas | 2 vacíos (0,05 % faltante) $\rightarrow$ Cobertura del 99,95 %.
  - YouTube: 230 filas | 73 vacíos (31,74 % faltante) $\rightarrow$ Cobertura del 68,26 % (videos sin descripción en API).
- **Uso actual:** `crisp_dm/03_data_preparation/prepare.py` excluye deliberadamente `post_text` de las columnas preparadas (L67). El diccionario de datos declara: *"No clasificar como si fuera comentario; contexto incompleto, fuera de alcance"*.

### 2.6 Estado de las Muestras de Evaluación
- **Muestra de Sentimiento y Emoción (`evaluation_sample.csv`):** 120 filas balanceadas (40 por plataforma). Ambas anotaciones (`gold_1` y `gold_2`) están completadas.
  - Acuerdo observador: 81,7 % en sentimiento (98/120) y 75,8 % en emoción (91/120).
  - Casos concordantes no ambiguos evaluados: 78 en sentimiento y 67 en emoción.
- **Muestra Temática (`theme_review_sample.csv`):** Generada por `prepare.py` con 198 filas (66 por plataforma, expandida a 204 líneas físicas por saltos de línea). **Las columnas `theme_gold_1` y `theme_gold_2` están 100 % vacías.** No existe una verdad terreno humana para validar métricas formales de precisión/recall en temas.

### 2.7 Mecánica de la Supresión de Grupos Pequeños en Despliegue
En `crisp_dm/06_deployment/build_app_data.py` (L38-40):
- Si un grupo en el cruce de `(platform, post_type, theme)` tiene $n < 10$, se renombra la etiqueta a `"Otros grupos de baja frecuencia"`.
- Al acumularse en `themes.csv`, esto introduce un pseudotema que la aplicación presenta. Esto no es un error de cálculo (la suma total se mantiene en 15.885), pero sí introduce una discrepancia semántica si no se advierte que es un artificio de privacidad y legibilidad estadística.

---

## 3. Hipótesis Aún No Comprobadas

Las siguientes afirmaciones son hipótesis verosímiles pero no demostradas rigurosamente en los datos actuales:

1. **Hipótesis de temas latentes en los 7.114 textos sustantivos de "Otros":** Se presume que existen subtemas institucionales recurrentes de alta relevancia no cubiertos por la taxonomía (p. ej., "Infraestructura, sedes y transporte", "Graduación, títulos y ceremonias", "Calidad docente y reclamos laborales", "Deportes, cultura y vida universitaria"). No se ha corrido un modelado no supervisado o clusterización que demuestre cuantitativamente sus fronteras.
2. **Hipótesis del impacto de emojis en la polaridad:** Se asume que los emojis de aplausos o corazones determinan la predicción de "alegría" y "positivo" en comentarios breves. Aunque `pysentimiento` procesa emojis internamente, no se ha realizado un estudio de ablación (comparar predicciones con y sin emojis) para aislar su peso causal.
3. **Hipótesis sobre el texto del post como desambiguador:** Se plantea la hipótesis de que vincular el texto de la publicación original (`post_text`) permitiría clasificar comentarios dependientes de contexto (como *"Totalmente de acuerdo"* o *"¿Dónde será?"*). No está comprobado si el ruido contextual del post induciría más errores de atribución temática que aciertos.

---

## 4. Discrepancias Encontradas y Métodos de Verificación

Durante el análisis se identificaron reportes y variaciones menores en recuentos que requieren clarificación explícita:

| Discrepancia Observada | Cifra A | Cifra B | Causa Raíz Comprobada | Procedimiento de Verificación |
|---|---|---|---|---|
| **Conteo de comentarios solo emojis** | 1.307 (`audit.py` / `quality_profile.json`) | 1.280 (`prepare.py` / `preparation_summary.json`) | `audit.py` utiliza `seems_emoji_only` que captura cualquier texto sin letras/números (incluye signos de puntuación pura como `...` o `???`). `prepare.py` exige estrictamente `has_emoji=True` AND `no_letras_numeros`. | Ejecutar filtro diferencial en `comments_unified.csv`: exactamente 27 filas son pura puntuación sin caracteres Unicode de emoji. |
| **Respuestas identificadas vs. retenidas** | 2.502 (`comments_unified.csv`) | 2.484 (`prepared_comments.csv`) | 18 filas marcadas como `is_reply=True` tenían texto vacío y fueron descartadas durante la limpieza de nulos en `prepare.py`. | Comprobar `df[df['is_reply'] & (df['text'].str.strip() == '')]`: exactamente 18 filas. |
| **Etiqueta en app vs. salida del modelo para emoción neutral** | `others` (en `scored_comments.csv` y `model_summary.json`) | `"Otros / sin emoción básica clara"` (en `app.py` y `emotions.csv`) | `build_app_data.py` (L29) renombra explícitamente `others` para evitar que el usuario de la app lo confunda con el sentimiento `NEU`. | Comprobar mapeo en `build_app_data.py`, L29: `replace({"others": "Otros / sin emoción básica clara"})`. |
| **Temas agregados en Streamlit vs. modelado** | 7 temas canónicos en `model_summary.json` | 8 categorías en `themes.csv` de despliegue | `build_app_data.py` agrupa combinaciones de celda con $n < 10$ bajo `"Otros grupos de baja frecuencia"`. | Verificar suma por plataforma y tipo de publicación; el total siempre cierra en 15.885. |

---

## 5. Limitaciones de Datos, Modelos y Muestras

Para preservar la rigurosidad científica y no sobrestimar las conclusiones:

1. **Sesgo por filtrado de concordancia en evaluación:**
   - La métrica de Sentiment Accuracy (74,4 %) y Emotion Accuracy (74,6 %) se evaluó únicamente sobre los 78 y 67 casos donde ambos anotadores humanos coincidieron y no hubo ambigüedad.
   - Este procedimiento descarta los 22 casos de sentimiento y 29 de emoción donde hubo discrepancia o ambigüedad, lo que favorece a los casos prototípicos y sesga las métricas al alza respecto al rendimiento real en producción.
2. **Naturaleza exploratoria del umbral de confianza $\ge 0,7$:**
   - La aparente exactitud del 92,9 % en sentimiento para confianza $\ge 0,7$ (52/56 aciertos) se evaluó en la misma muestra sobre la cual se observaron los puntos de corte. No constituye una validación en conjunto de prueba independiente (*held-out test set*). En el corpus completo, solo el 51,8 % de los comentarios alcanza este umbral.
3. **Fragilidad de clases minoritarias en emoción:**
   - En la muestra de evaluación concordante, las clases `fear` y `surprise` tuvieron 0 casos de soporte, y `disgust` tuvo 3 casos (todos fallados por el modelo). El Macro-F1 de emoción reportado (0,429) está fuertemente penalizado por ceros matemáticos en clases sin soporte muestral.
4. **Ausencia de validación humana en temas:**
   - No es ético ni metodológicamente admisible calcular métricas de evaluación temática (F1, precisión, recall) usando pseudoetiquetas generadas por IA o modelos sin supervisión humana directa.
   - Actualmente, la taxonomía temática tiene carácter **estrictamente heurístico-exploratorio**.
5. **Representatividad poblacional nula:**
   - La distribución por plataforma está fuertemente desbalanceada (Facebook 72,6 %, Instagram 26,0 %, YouTube 1,4 %) debido a los métodos de captura y algoritmos de cada red. No se cuenta con datos de alcance, impresiones ni demografía. Las cifras reflejan exclusivamente el volumen de comentarios capturados, no la opinión de la comunidad universitaria de Unillanos.
6. **Desconexión conversacional (hilos no modelados):**
   - El 15,6 % de los comentarios preparados son respuestas (`is_reply=True`). Al evaluarse aisladas de su comentario padre, textos elípticos (p. ej., *"sí"*, *"a las 3"*, *"no me parece"*) carecen de significado autónomo, provocando sobreclasificación en neutral o en la categoría residual.

---

## 6. Conclusión Diagnóstica

El sistema actual tiene una base de ingeniería de datos impecable (trazabilidad, limpieza, anonimización, reproducibilidad). Sin embargo, su **arquitectura temática es insuficiente para orientar la toma de decisiones institucionales**, debido al volumen desmedido del residual (66,0 %) y a las colisiones léxicas no delimitadas.

La prioridad estratégica del proyecto debe virar hacia la **reestructuración profunda del componente temático**, refinando las reglas con delimitadores de palabra y desacoplando el contenido genuinamente temático del ruido conversacional (emojis y menciones), al tiempo que sentimiento y emoción se conservan como descriptores complementarios agregados.
