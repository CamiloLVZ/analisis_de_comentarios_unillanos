# Fase 1 — Comprensión del negocio

## Estado

**Completada y refactorizada.** El objetivo y el alcance se fijaron con la información disponible en el repositorio; se priorizó la dimensión temática como eje estructurante del proyecto y se reubicó sentimiento y emoción como dimensiones secundarias y condicionadas al ámbito temático.

## Contexto y problema

El proyecto cuenta con comentarios recolectados de las páginas institucionales de Unillanos en Facebook, Instagram y YouTube. Para la toma de decisiones institucionales y la gestión universitaria, el valor principal radica en identificar **de qué habla la comunidad** (admisiones, programas de bienestar, trámites y certificados, oferta académica, infraestructura y sedes, actividades culturales y eventos, o reconocimiento institucional).

Analizar polaridades afectivas o emociones abstractas sin contexto temático ofrece utilidad limitada; por tanto, el sistema organiza los comentarios prioritariamente por áreas de conversación y, en segundo nivel, examina el clima emocional asociado a cada una.

## Objetivo y preguntas

El objetivo general es estructurar una taxonomía temática transparente mediante reglas léxicas supervisadas por dominio, describir la polaridad del sentimiento (positivo/negativo/neutral) y las emociones básicas, y comunicar resultados agregados en Streamlit.

Preguntas priorizadas:

1. ¿Qué temas específicos de gestión, vida académica y bienestar emergen en los comentarios recopilados?
2. ¿Cómo se distribuyen los comentarios entre contenido proposicional sustantivo y reacciones estrictamente sociales/emojis/menciones?
3. ¿Cómo varía la polaridad de sentimiento al condicionarse por área temática institucional?
4. ¿Qué diferencias descriptivas aparecen por plataforma o tipo de publicación, considerando el tamaño desigual de los grupos?

## Alcance y exclusiones

- Se analizará el CSV unificado existente y sus comentarios ligados a metadatos de publicaciones.
- No se recolectarán nuevos datos ni se analizará la evolución temporal.
- Las respuestas se conservarán como comentarios individuales; no se compararán grupos ni se modelará contexto del hilo.
- Los emojis se conservarán para el análisis afectivo; en la taxonomía temática, los comentarios solo emoji se distinguen explícitamente como "Sin contenido temático suficiente" para no distorsionar las áreas sustantivas.
- El texto de la publicación (`post_text`) no se concatena al comentario para evitar contaminación de contexto en la opinión del usuario.
- No se afirmará validación humana de temas mientras no exista una anotación manual independiente en la muestra respectiva.
- La aplicación será entregada para ejecución/despliegue local por el usuario. No se publicará automáticamente desde este flujo.

## Éxito

1. Cada cifra puede rastrearse exactamente al código y a los datos (15.885 comentarios analizados).
2. Se desarticula la hipertrofia del residual "Otros", distinguiendo claramente entre temas sustantivos, comentarios sin contenido proposicional suficiente y residual estricto.
3. Se eliminan colisiones léxicas y falsos positivos mediante expresiones regulares con delimitadores de palabra (`\b`).
4. La aplicación expone solo agregados protegidos con umbral de supresión ($n < 10$).
5. El informe final y los documentos CRISP-DM documentan con honestidad metodológica el estado real de cada componente.

## Riesgos y mitigaciones

- **Riesgo:** Confundir neutralidad afectiva con baja confianza o ausencia de emoción.  
  *Mitigación:* Se presentan bandas de confianza separadas y se documenta la clase `others` de emoción como ausencia de emoción básica identificada.
- **Riesgo:** Sobreclasificación por palabras genéricas en reglas léxicas.  
  *Mitigación:* Delimitación por fronteras de palabra (`\b`), sustitución de palabras interrogativas sueltas por sintagmas de trámite y preclasificación de contenido mínimo.
- **Riesgo:** Atribuir validación humana a componentes heurísticos.  
  *Mitigación:* Se distingue formalmente entre la evaluación de sentimiento/emoción (120 casos con doble anotación humana) y la taxonomía temática (supervisión por reglas léxicas sin ground-truth manual).
