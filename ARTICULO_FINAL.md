# Temas institucionales, sentimiento y emociones en comentarios de redes sociales de la Universidad de los Llanos

## Resumen

Este proyecto presenta un análisis descriptivo y reproducible de 16.471 comentarios recopilados de publicaciones institucionales de Facebook, Instagram y YouTube de la Universidad de los Llanos. Se siguió la metodología CRISP-DM para auditar y preparar los datos, estructurar una taxonomía temática supervisada por dominio, estimar sentimiento y emociones en español mediante `pysentimiento` (RoBERTuito) y construir una aplicación Streamlit basada en agregados seguros. Tras excluir 586 registros sin texto, se analizaron de forma exhaustiva 15.885 comentarios. La dimensión temática se priorizó como eje organizativo: mediante expresiones regulares compiladas con límites de palabra (`\b`), se eliminaron colisiones léxicas y se diferenció el contenido puramente social o de emojis (25,8 %, 4.090 casos) de las áreas sustantivas universitarias, reduciendo el residual no identificado del 66,0 % original a 34,4 % (5.469 casos). En la dimensión afectiva, el sentimiento global estimado fue neutral en 58,2 %, positivo en 27,1 % y negativo en 14,6 %, mientras que la emoción predominante fue `others` (66,8 %), seguida de alegría (24,7 %). Al evaluar una muestra de 120 comentarios anotada de forma independiente y ciega por dos evaluadores humanos, se obtuvo un acuerdo de 81,7 % en sentimiento y 75,8 % en emoción; en los casos concordantes no ambiguos, la exactitud fue de 74,4 % para sentimiento ($N=78$) y 74,6 % para emoción ($N=67$). La aplicación desplegada permite explorar no solo volúmenes temáticos, sino la polaridad de sentimiento condicionada a cada área institucional.

**Palabras clave:** CRISP-DM, analítica de texto, clasificación temática, análisis de sentimiento, redes sociales universitarias, Streamlit.

## 1. Introducción

Los comentarios en redes sociales institucionales constituyen canales abiertos de retroalimentación donde convergen inquietudes administrativas, solicitudes académicas, quejas sobre servicios y expresiones de reconocimiento. No obstante, su análisis automatizado enfrenta retos significativos: lenguaje informal, ambigüedad sintáctica, alta densidad de emojis, menciones a terceros y ausencia de contexto en hilos de respuesta.

Para la gestión de la Universidad de los Llanos, identificar **de qué asuntos específicos habla la comunidad** (admisiones, bienestar, oferta académica, infraestructura, eventos o trámites) es prioritario frente a una mera clasificación afectiva abstracta. El presente trabajo estructura un mapa temático riguroso y transparente, reubicando el sentimiento y las emociones como dimensiones secundarias y complementarias.

## 2. Objetivos y alcance

### Objetivo general
Desarrollar un flujo reproducible bajo CRISP-DM para identificar, categorizar y describir temas clave, polaridad de sentimiento y emociones en los comentarios de Facebook, Instagram y YouTube de Unillanos, comunicando resultados agregados y limitaciones en una aplicación interactiva.

### Objetivos específicos
1. Auditar cobertura, calidad, estructura y privacidad del corpus unificado.
2. Preparar el texto preservando comentarios íntegros, emojis y respuestas, derivando indicadores de contenido mínimo.
3. Construir una taxonomía temática con reglas léxicas delimitadas (`\b`), separando textos proposicionales de interacciones sociales mínimas.
4. Aplicar modelos preentrenados en español para estimar polaridad y emociones básicas.
5. Evaluar la concordancia de las predicciones afectivas contra una muestra anotada por dos evaluadores humanos independientes, explicitando las limitaciones éticas y metodológicas de la taxonomía.
6. Publicar los resultados en Streamlit con agregados seguros y visualización de sentimiento condicionado al tema.

**Fuera de alcance:** Evolución temporal de publicaciones; comparación causal de hilos; desanonimización de perfiles; representatividad poblacional de toda la comunidad regional; concatenación del texto del post con el comentario.

## 3. Datos

La ingesta unificada recopiló **16.471 filas** y 32 columnas procedentes de 3.252 publicaciones y videos (Facebook: 12.089; Instagram: 4.152; YouTube: 230). Se eliminaron 586 registros cuyo texto era nulo o de espacios en blanco, consolidando **15.885 comentarios analizables**:
- **Facebook:** 11.529 comentarios (72,58 %)
- **Instagram:** 4.126 comentarios (25,97 %)
- **YouTube:** 230 comentarios (1,45 %)

Se preservaron 2.484 respuestas con texto (15,6 %) y 1.280 comentarios formados exclusivamente por emojis (8,1 %). El texto de la publicación (`post_text`) tiene una cobertura del 99,6 % en Facebook, 99,9 % en Instagram y 68,3 % en YouTube; se conservó como metadato pero se mantuvo estrictamente separado del comentario para evitar atribuciones contextuales falsas.

## 4. Metodología: CRISP-DM ejecutado

### 4.1 Comprensión del negocio
Se definió como prioridad estratégica descubrir las áreas institucionales de mayor interés ciudadano antes que polaridades aisladas. El alcance y los criterios de aceptación se documentaron en `crisp_dm/01_business_understanding/README.md` y `PLAN_MAESTRO.md`.

### 4.2 Comprensión de los datos
Mediante `audit.py`, se perfiló la cobertura y se detectaron sesgos de plataforma. Se confirmó la ausencia de IDs duplicados y se identificó la alta prevalencia de comentarios breves y menciones entre usuarios.

### 4.3 Preparación
En `prepare.py`, se conservó el texto original para inferencia en `pysentimiento` y se generó una versión normalizada para exploración léxica. Se establecieron indicadores booleanos de contenido simbólico (`has_emoji`, `emoji_only`) y longitud (`word_count`).

### 4.4 Modelado Temático y Afectivo

#### Taxonomía Temática Refinada
A diferencia del esquema inicial (que dejaba 66,0 % en un residual indiferenciado), se refinaron las reglas léxicas en `theme_rules.json` empleando expresiones regulares compiladas con fronteras de palabra (`\b`), eliminando colisiones léxicas (p. ej., `\bcursos?\b` para no absorber *"concurso"* o *"recurso"*), retirando palabras funcionales genéricas (*"cuando"*, *"donde"*) e incorporando infraestructura.

Adicionalmente, se estableció un pre-clasificador de contenido mínimo que asigna a `"Sin contenido temático suficiente"` a aquellos comentarios `emoji_only` o que contienen $\le 2$ palabras tras retirar menciones (`@usuario`).

**Distribución Temática ($N = 15.885$):**
| Categoría Temática | Comentarios | Porcentaje |
|---|---:|---:|
| Otros temas no identificados (residual sustantivo) | 5.469 | 34,4 % |
| Sin contenido temático suficiente (social/emoji/mención) | 4.090 | 25,8 % |
| Felicitaciones y reconocimiento institucional | 2.377 | 15,0 % |
| Oferta académica e investigación | 1.941 | 12,2 % |
| Admisiones, inscripciones y matrículas | 691 | 4,4 % |
| Programas de acceso y bienestar | 480 | 3,0 % |
| Información, trámites y certificados | 462 | 2,9 % |
| Infraestructura, sedes y tecnología | 229 | 1,4 % |
| Eventos, cultura y actividades institucionales | 146 | 0,9 % |

#### Sentimiento y Emoción
Calculados con RoBERTuito (`pysentimiento`):
- **Sentimiento:** Neutral (NEU) 58,2 % (9.250), Positivo (POS) 27,1 % (4.312), Negativo (NEG) 14,6 % (2.323).
- **Emoción:** `others` (sin emoción básica clara) 66,8 % (10.615), alegría 24,7 % (3.916), enojo 5,0 % (799), tristeza 2,9 % (466), sorpresa 0,5 % (79), miedo 0,1 % (9), disgusto <0,1 % (1).

### 4.5 Evaluación
Se evaluó una muestra balanceada de 120 comentarios (40 por plataforma) anotada independientemente por dos personas para polaridad y emociones:
- **Acuerdo inter-anotador:** 81,7 % (98/120) en sentimiento; 75,8 % (91/120) en emoción.
- **Rendimiento en concordantes no ambiguos:**
  - Sentimiento ($N=78$): Accuracy = 74,4 %, Macro-F1 = 0,739.
  - Emoción ($N=67$): Accuracy = 74,6 %, Macro-F1 = 0,429 (penalizado por clases minoritarias sin soporte).
- **Diagnóstico por Confianza ($\ge 0,7$):** Cubrió el 71,8 % de los casos evaluables de sentimiento con 92,9 % de exactitud (52/56 aciertos); en el corpus completo, 51,8 % alcanza este umbral. Es un hallazgo exploratorio in-sample.
- **Estado de la Muestra Temática:** La muestra de 198 comentarios carece de etiquetas humanas independientes; se prohíbe éticamente presentar pseudoetiquetas de IA como ground-truth. La taxonomía se evalúa por consistencia y delimitación léxica.

### 4.6 Despliegue
La aplicación en `crisp_dm/06_deployment/deploy_bundle/app.py` se actualizó para ofrecer:
1. Vista global y distribución por plataforma.
2. Desglose temático refinado con desarticulación del residual.
3. Módulo interactivo de **Sentimiento por tema institucional**, permitiendo auditar la polaridad interna de Admisiones, Bienestar, Infraestructura, etc.
4. Diagnósticos de confianza y consideraciones metodológicas completas.
5. Agregación segura con umbral de supresión ($n < 10$).

## 5. Reproducibilidad

El flujo completo se ejecuta de forma secuencial y determinista:

```powershell
# Fase 2: Unificación y auditoría
python crisp_dm/02_data_understanding/unify_raw_data.py
python crisp_dm/02_data_understanding/audit.py

# Fase 3: Preparación de tabla analítica y muestras
python crisp_dm/03_data_preparation/prepare.py

# Fase 4: Modelado (actualización de reglas temáticas sin re-inferencia ML pesada)
python crisp_dm/04_modeling/analyze.py --themes-only

# Fase 5: Evaluación contra muestra manual concordante
python crisp_dm/05_evaluation/evaluate.py

# Fase 6: Construcción de agregados para despliegue y app
python crisp_dm/06_deployment/build_app_data.py
streamlit run crisp_dm/06_deployment/deploy_bundle/app.py
```

## 6. Limitaciones

1. **Evaluación Afectiva en Subconjunto Concordante:** El filtrado a casos donde ambos humanos coinciden favorece instancias prototípicas y excluye la ambigüedad real de redes sociales.
2. **Confianza No Calibrada Independientemente:** El umbral de 0,7 fue explorado en la misma muestra de evaluación; es indicativo y no una garantía probabilística.
3. **Naturaleza Heurística de la Taxonomía Temática:** Pese al uso de límites de palabra (`\b`), las reglas léxicas no capturan estructuras sintácticas complejas, ironías o metáforas.
4. **Desbalance de Plataformas:** Facebook concentra el 72,6 % de los datos; YouTube (1,4 %) no permite contrastes estadísticos generalizables.
5. **Aislamiento de Respuestas:** El 15,6 % de los textos son respuestas evaluadas fuera del hilo conversacional.

## 7. Conclusiones

Se consolidó un sistema analítico CRISP-DM robusto, reproducible y transparente sobre los comentarios institucionales de Unillanos. Al priorizar la dimensión temática y refactorizar las reglas léxicas, se logró desarticular el residual ambiguo (reduciéndolo a la mitad) y aislar las interacciones puramente sociales de las áreas temáticas estratégicas. El cruce condicionado de temas y sentimientos entrega por primera vez una herramienta de analítica descriptiva accionable para orientar la gestión y comunicación institucional de la universidad.

## Referencias técnicas

- Pérez, J. M. et al. (2021). *pysentimiento: A Python Toolkit for Sentiment Analysis and SocialNLP tasks*.
- Streamlit Documentation (2026). *Data apps and visualization principles*.
