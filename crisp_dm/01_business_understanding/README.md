# Fase 1 — Comprensión del negocio

## Estado

**Completada.** El objetivo y el alcance se fijaron con la información disponible en el repositorio; no se necesitó consultar a actores externos.

## Contexto y problema

El proyecto ya cuenta con comentarios recolectados de las páginas institucionales de Unillanos en Facebook, Instagram y YouTube. Se necesita convertir esas filas en una descripción entendible de los temas tratados y el tono/emociones expresados, con una salida visual que pueda explorar el equipo.

## Objetivo y preguntas

El objetivo general es identificar y describir temas, sentimiento (positivo/negativo/neutral) y emociones (clases disponibles en el modelo español) en los comentarios disponibles, y comunicar resultados agregados en Streamlit.

Preguntas priorizadas:

1. ¿Qué temas recurrentes se observan en los comentarios?
2. ¿Cómo se distribuyen las estimaciones de sentimiento y emoción?
3. ¿Qué diferencias descriptivas aparecen por plataforma o tipo de publicación, considerando el tamaño desigual de los grupos?

## Alcance y exclusiones

- Se analizará el CSV unificado existente y sus comentarios ligados a metadatos de publicaciones.
- No se recolectarán nuevos datos ni se analizará la evolución temporal.
- Las respuestas se conservarán como comentarios; no se compararán grupos ni se modelará contexto del hilo.
- Los emojis se conservarán y se probará su normalización textual; no se hará un experimento separado de ablación.
- No se entrenará un modelo propio, no se hará inferencia causal ni se inferirá opinión de toda la comunidad.
- La aplicación será entregada para ejecución/despliegue por el usuario. No se publicará desde este flujo.

## Éxito

1. Cada cifra puede rastrearse a los datos y el código.
2. Se entrega una muestra para evaluación manual; las predicciones se presentan como estimaciones mientras esa evaluación esté pendiente.
3. Las categorías temáticas se describen como reglas exploratorias hasta que el equipo revise la muestra temática.
4. La aplicación expone solo agregados; el README permite ejecutarla localmente.
5. El artículo incluye denominadores, limitaciones y estado real de cada fase.

## Riesgos iniciales

Modelo de dominio distinto; textos cortos o emoji-only; comentarios dependientes de contexto; volumen desigual por plataforma; cobertura de scraping desconocida; dependencias pesadas del modelo. Se atenderán con evaluación manual, etiqueta ambigua, denominadores visibles y documentación de cobertura.

## Uso de las salidas

Este acuerdo de alcance guía la auditoría de la fase 2. Si el CSV no tiene campos requeridos, se ajustará el alcance aquí antes de inferir resultados. El plan detallado está en `PLAN_MAESTRO.md`.

