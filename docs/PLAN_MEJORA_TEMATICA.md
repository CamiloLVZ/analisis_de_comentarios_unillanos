# Plan Maestro de Mejora y Consolidación Temática (CRISP-DM)

**Proyecto:** Análisis de Comentarios de Redes Sociales de la Universidad de los Llanos  
**Destinatario:** Agente Implementador Local  
**Objetivo:** Pulir y finalizar la solución analítica hoy mismo en el repositorio local, sin operaciones destructivas, sin reentrenamientos pesados y con máxima transparencia metodológica.  
**Fecha:** 16 de noviembre de 2026  
**Guía Metodológica:** Basado en el diagnóstico formal en `docs/DIAGNOSTICO_MEJORA_TEMATICA.md`.

---

## 1. Recomendación Principal y Decisión Estratégica

### Decisión de Arquitectura:
**Priorizar la dimensión temática como eje estructurante del proyecto y reubicar sentimiento y emoción como dimensiones secundarias y condicionadas.**

### Justificación Basada en Evidencia:
1. **Relevancia Institucional:** La Universidad de los Llanos necesita identificar de qué temas habla la comunidad (admisiones, bienestar, quejas de infraestructura, eventos, vida académica) para orientar acciones de gestión y comunicación. Saber si un comentario es "positivo" o "neutral" sin saber a qué área temática refiere carece de aplicabilidad práctica.
2. **Desacople del Residual Hipertrofiado (66 %):** Se debe desarticular la categoría `"Otros / tema no identificado"` ($N = 10.486$) separando estructuralmente:
   - **Textos sin sustancia proposicional:** Comentarios compuestos solo por emojis (`emoji_only`, $N = 1.280$), menciones vacías a terceros (`@usuario` con $\le 3$ palabras, $N = 236$) y cortesías mínimas. Estos deben catalogarse como `"Sin contenido temático suficiente (social/emoji/mención)"`.
   - **Temas Específicos Ampliados y Refinados:** Categorías robustecidas mediante patrones de límites de palabra (`\b`), eliminando colisiones léxicas y falsos positivos funcionales.
   - **Residual Genuino:** Comentarios sustantivos ($> 3$ palabras) cuyo tema no encaja en la taxonomía institucional definida (`"Otro tema identificable"`).
3. **Preservación Íntegra de Modelos ML:** No se deben reejecutar las inferencias pesadas de `pysentimiento` (sentimiento y emoción ya calculados para los 15.885 comentarios en `data/processed/model_outputs/scored_comments.csv` son totalmente válidos y costosos de recalcular en CPU). La reasignación temática se ejecuta de forma instantánea mediante la bandera `--themes-only` de `crisp_dm/04_modeling/analyze.py`.
4. **Honestidad Científica en Evaluación:** Al no existir anotación humana para la muestra temática de 198 casos, la taxonomía se documentará rigurosamente como un sistema de *reglas léxicas supervisadas por dominio*, sin inventar métricas pseudo-precisas ni hacer pasar etiquetas de IA como evaluación humana.

---

## 2. Decisiones Metodológicas Inmutables (Reglas del Proyecto)

El agente implementador **NO DEBE** alterar las siguientes decisiones metodológicas sin autorización expresa:
1. **No reejecutar la inferencia ML completa de sentimiento/emoción:** Debe preservarse `scored_comments.csv` y utilizar el flujo `--themes-only` para actualizar la columna `theme`.
2. **No usar `post_text` como clasificador del comentario:** El texto del post o video describe el contenido institucional emitido, no la opinión del usuario. Puede usarse como metadato de contexto en filtros de visualización futuros, pero nunca concatenarse al texto del comentario para inferir la polaridad o el tema expresado por el ciudadano (evita contaminación de contexto).
3. **No descartar comentarios cortos ni emojis:** Deben permanecer dentro de los 15.885 registros analizados; su clasificación correcta es la asignación a la categoría `"Sin contenido temático suficiente"`, garantizando que la suma de filas siga cuadrando de forma exacta en 15.885.
4. **Prohibición de Pseudoetiquetado de IA como "Anotación Humana":** Si no hay tiempo o personal humano para etiquetar la muestra de 198 comentarios de temas, se debe declarar el estado como `exploratorio_reglas_lexicas`. Jamás se debe generar etiquetas con un LLM y reportarlas como "concordancia humana" o "ground truth".
5. **No exponer datos identificables en despliegue:** La aplicación Streamlit y su carpeta de despliegue (`crisp_dm/06_deployment/deploy_bundle/data/app/`) deben contener exclusivamente tablas agrupadas (`groupby`) con supresión de celdas con $n < 10$. No exportar textos, autores, IDs ni URLs.

---

## 3. Plan de Implementación por Fases CRISP-DM

```
                                FLUJO DE EJECUCIÓN RECOMENDADO
                                
   Fase 03: Preparación          Fase 04: Modelado              Fase 05: Evaluación          Fase 06: Despliegue
┌─────────────────────────┐   ┌───────────────────────────┐   ┌────────────────────────┐   ┌──────────────────────────┐
│ Reglas léxicas con      │   │ Actualizar                │   │ Auditar matriz         │   │ Reconstruir agregados    │
│ límites de palabra (\b) │──>│ theme_rules.json          │──>│ distribución y         │──>│ Streamlit                │
│ y preclasificador       │   │ python analyze.py         │   │ documentar límites     │   │ (build_app_data.py)      │
│ no temático             │   │   --themes-only           │   │ sin falso gold         │   │ Verificar app local      │
└─────────────────────────┘   └───────────────────────────┘   └────────────────────────┘   └──────────────────────────┘
```

---

### Fase 1: Comprensión del Negocio (Business Understanding)
- **Objetivo:** Reflejar que el objetivo primario de la analítica de Unillanos es el mapa de necesidades, trámites y áreas temáticas de la comunidad, y el objetivo secundario es el clima emocional asociado a cada una de ellas.
- **Acción:** Actualizar la documentación de alcance en `crisp_dm/01_business_understanding/README.md` destacando esta jerarquía metodológica.

---

### Fase 2: Comprensión de los Datos (Data Understanding)
- **Objetivo:** Registrar las características empíricas de los textos que explican el residual.
- **Acción:** Asegurar que `crisp_dm/02_data_understanding/outputs/data_dictionary.md` mantenga la advertencia sobre `post_text` (cobertura incompleta en YouTube del 68,26 % y riesgo de contaminación semántica).

---

### Fase 3: Preparación de Datos (Data Preparation)
- **Objetivo:** Facilitar la separación entre texto proposicional y ruido social/interaccional sin alterar `prepared_comments.csv`.
- **Estrategia en la función de asignación temática:**
  Implementar una rutina previa de filtrado de contenido temático suficiente antes de evaluar las reglas léxicas:
  1. Si `emoji_only == True` $\rightarrow$ Clasificar directamente como `"Sin contenido temático suficiente (social/emoji/mención)"`.
  2. Si el texto tras remover menciones (`@\w+`) y signos de puntuación tiene menos de 2 palabras informativas $\rightarrow$ Clasificar como `"Sin contenido temático suficiente (social/emoji/mención)"`.
  3. Si contiene palabras exclusivas de cortesía/saludo básico (*"hola"*, *"buenos días"*, *"gracias"* aislado sin contexto adicional) $\rightarrow$ Si no coincide con ninguna categoría sustantiva previa, clasificar como saludo/reconocimiento o sin contenido suficiente.

---

### Fase 4: Modelado (Modeling) - Núcleo de la Refactorización

#### Tarea 4.1: Rediseño de `crisp_dm/04_modeling/theme_rules.json`
El implementador debe reescribir `theme_rules.json` adoptando una taxonomía de **7 temas específicos** + **1 residual específico** + **1 clase no temática**:

1. `Programas de acceso y bienestar`:
   - *Patrones obligatorios:* `matricula cero`, `hambre cero`, `bienestar universitario`, `beca\w*`, `alimentaci[oó]n`, `apoyo econ[oó]mico`, `subsidio`, `comedor`.
2. `Admisiones, inscripciones y matrículas`:
   - *Patrones obligatorios:* `\binscrip\w*`, `\badmis\w*`, `\baspirante\w*`, `\badmitid\w*`, `\bpregrado\w*`, `\bposgrado\w*`, `\bmatricula\w*`, `\bcupos?\b`.
3. `Información, trámites y certificados`:
   - *Ajuste crítico:* Retirar las palabras genéricas aisladas `"cuando"`, `"donde"`, `"cuanto"`.
   - *Patrones sustitutos precisos:* `c[oó]mo me inscribo`, `d[oó]nde puedo`, `cu[aá]nto cuesta`, `cu[aá]ndo inician`, `\brequisitos?\b`, `\bhorarios?\b`, `\bsolicitud\w*`, `\btr[aá]mite\w*`, `\bcertificad\w*`, `\bconstancia\w*`, `\bhomologaci[oó]n`, `atenci[oó]n al usuario`.
4. `Oferta académica e investigación`:
   - *Ajuste crítico:* Resolver colisión de `"curso"` mediante límites de palabra `\bcursos?\b`.
   - *Patrones:* `\bfacultad\w*`, `\bcarreras?\b`, `\bprogramas?\b`, `\bestudiantes?\b`, `\bdocentes?\b`, `\bprofesor\w*`, `\binvestigaci[oó]n\w*`, `\bsemilleros?\b`, `\bcursos?\b`, `\bclases?\b`, `\bpensum\b`, `\bgraduaci[oó]n\w*`, `\bgrado\b`.
5. `Infraestructura, sedes y tecnología` *(Nueva categoría rescatada de "Otros"):*
   - *Patrones:* `\bsedes?\b`, `barcelona`, `san antonio`, `boquemonte`, `laboratorio\w*`, `biblioteca\w*`, `campus`, `internet`, `wifi`, `aulas?`, `transporte`, `bus\b`.
6. `Eventos, cultura y actividades institucionales`:
   - *Patrones:* `\beventos?\b`, `\bferias?\b`, `\bconferencias?\b`, `\bforos?\b`, `\bfestival\w*`, `\bcongresos?\b`, `\btalleres?\b`, `semana universitaria`, `concierto`.
7. `Felicitaciones y reconocimiento institucional`:
   - *Patrones:* `\bfelicit\w*`, `\bgracias\b`, `\bexcelente\b`, `\b[eé]xitos?\b`, `\borgullo\w*`, `\bbendici[oó]n\w*`, `\bmaravillos\w*`, `\benhorabuena\b`.
8. `Sin contenido temático suficiente (social/emoji/mención)` *(Pre-filtro / Categoría funcional)*.
9. `Otros temas no identificados` *(Residual estricto para comentarios con contenido léxico que no calzan en 1-7)*.

#### Tarea 4.2: Actualización de la lógica en `crisp_dm/04_modeling/analyze.py`
Sustituir la búsqueda ingenua de subcadenas `needle in normalized` por expresiones regulares compiladas con límites de palabra (`\b`):
```python
# Ejemplo de lógica que debe implementar en assign_theme:
def assign_theme(text: str, is_emoji_only: bool, word_count: int, rules: dict) -> str:
    # 1. Regla de ausencia de contenido temático
    if is_emoji_only or word_count <= 2:
        return "Sin contenido temático suficiente (social/emoji/mención)"
        
    normalized = strip_accents(str(text).lower())
    
    # 2. Iteración por reglas usando regex con límites de palabra
    for category in rules["categories"]:
        for pattern in category["compiled_patterns"]:
            if pattern.search(normalized):
                return category["name"]
                
    return rules["fallback"]
```

#### Tarea 4.3: Ejecución segura
El implementador debe ejecutar:
```powershell
python crisp_dm/04_modeling/analyze.py --themes-only
```
Esto recalcula los temas en `scored_comments.csv` y actualiza `theme_counts.csv` y `model_summary.json` en pocos segundos, **sin tocar los modelos ML**.

---

### Fase 5: Evaluación (Evaluation)
- **Objetivo:** Presentar las métricas de sentimiento/emoción con transparencia y documentar el estado de la validación temática.
- **Acciones:**
  1. Ejecutar:
     ```powershell
     python crisp_dm/05_evaluation/evaluate.py
     ```
  2. Verificar que `crisp_dm/05_evaluation/outputs/evaluation_report.md` conserve las notas metodológicas:
     - Las métricas de sentimiento (74,4 % acc) y emoción (74,6 % acc) corresponden exclusivamente a los 78 y 67 casos concordantes no ambiguos de la muestra manual de 120 comentarios.
     - El umbral $\ge 0,7$ de sentimiento es exploratorio (in-sample).
     - La taxonomía temática no posee evaluación cuantitativa de F1 por carecer de ground-truth humano en `theme_review_sample.csv`; se reporta su distribución de cobertura y análisis de colisiones léxicas resueltas.

---

### Fase 6: Despliegue (Deployment)

#### Tarea 6.1: Reconstrucción de Datos de Despliegue
Ejecutar el script de empaquetado:
```powershell
python crisp_dm/06_deployment/build_app_data.py
```
Esto regenera automáticamente los agregados anonimizados en `crisp_dm/06_deployment/deploy_bundle/data/app/`:
- `themes.csv`
- `sentiment.csv`
- `emotions.csv`
- `sentiment_confidence.csv`
- `overview.json`
- `deployment_manifest.json`

#### Tarea 6.2: Ajuste en la Interfaz de Usuario (`app.py`)
En `crisp_dm/06_deployment/deploy_bundle/app.py`:
1. **Pestaña "Temas":**
   - Presentar la distinción clara entre temas de gestión institucional y la categoría `"Sin contenido temático suficiente (social/emoji/mención)"`.
   - Incluir una métrica de impacto que muestre cómo el residual genuino de "Otros" se redujo drásticamente al separar los mensajes no proposicionales.
2. **Cruce Temas $\times$ Sentimiento:**
   - Enriquecer la visualización permitiendo filtrar o visualizar el sentimiento estimado condicionado al tema seleccionado (así la universidad puede ver: *¿Cuál es el sentimiento específico en Admisiones vs. Bienestar vs. Infraestructura?*).
3. **Pestaña "Método y límites":**
   - Incorporar explícitamente los hallazgos del diagnóstico: delimitadores de palabra aplicados, emojis preservados como dimensión interactiva, y carácter exploratorio de la confianza $\ge 0,7$.

#### Tarea 6.3: Verificación de la Aplicación Local
Verificar la app local ejecutando:
```powershell
streamlit run crisp_dm/06_deployment/deploy_bundle/app.py
```

---

## 4. Secuencia Concreta de Comandos para el Implementador

El siguiente bloque representa la secuencia exacta de tareas y comandos que el implementador debe seguir en la terminal de PowerShell:

```powershell
# Paso 1: Actualizar reglas léxicas y script de modelado
# Editar crisp_dm/04_modeling/theme_rules.json y crisp_dm/04_modeling/analyze.py

# Paso 2: Reasignar temas de forma instantánea (sin inferencia pesada)
python crisp_dm/04_modeling/analyze.py --themes-only

# Paso 3: Regenerar frecuencias de unigramas y bigramas si se actualizaron stopwords
python crisp_dm/04_modeling/analyze.py --terms-only

# Paso 4: Ejecutar la auditoría y reporte de evaluación
python crisp_dm/05_evaluation/evaluate.py

# Paso 5: Reconstruir el paquete de datos agregados para Streamlit
python crisp_dm/06_deployment/build_app_data.py

# Paso 6: Actualizar ARTICULO_FINAL.md reflejando las nuevas distribuciones temáticas

# Paso 7: Comprobar el despliegue local
streamlit run crisp_dm/06_deployment/deploy_bundle/app.py
```

---

## 5. Criterios de Término y Lista de Verificación (Checklist)

El implementador habrá terminado exitosamente cuando se cumpla cada uno de los siguientes puntos:

- [ ] **Consistencia de Totales:** La suma de comentarios categorizados en `theme_counts.csv`, `scored_comments.csv` y `themes.csv` es exactamente **15.885**.
- [ ] **Desarticulación del Residual:** La categoría `"Otros / tema no identificado"` se redujo sustancialmente (a menos del 35 % del corpus), habiéndose canalizado los comentarios sin texto proposicional a `"Sin contenido temático suficiente"`.
- [ ] **Eliminación de Colisiones:** Búsquedas de subcadenas como `"curso"` ya no absorben erróneamente palabras como `"concurso"`, `"recurso"` o `"discurso"`.
- [ ] **Palabras Funcionales Limpias:** Términos como `"cuando"`, `"donde"`, `"cuanto"` fueron reemplazados por patrones específicos de solicitud de trámites.
- [ ] **Preservación de Modelos:** Los puntajes y probabilidades de sentimiento y emoción en `scored_comments.csv` se mantuvieron idénticos a los originales.
- [ ] **Privacidad 100 % Garantizada:** Ningún archivo dentro de `crisp_dm/06_deployment/deploy_bundle/data/app/` contiene texto de comentarios, identificadores de autor, IDs de comentario ni URLs.
- [ ] **Honestidad en Evaluación:** Ningún informe menciona "validación temática con F1 del 90 %" salvo que provenga de una verdadera anotación humana. Se reporta el estatus real de las reglas supervisadas.
- [ ] **Documentación Sincronizada:** `ARTICULO_FINAL.md` y `crisp_dm/06_deployment/README.md` reflejan fielmente las nuevas cifras y la jerarquía temática.
