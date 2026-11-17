# Auditoría de Reglas Temáticas (CRISP-DM Fase 4)

**Fecha de ejecución:** 16 de noviembre de 2026  
**Script de verificación:** `verificacion_reglas.py`  
**Hash SHA-256 de `theme_rules.json`:** `a69292d738828d2bbd1c8569b5dea235b404e7cd59708e811868bf0f969f3266`  
**Corpus analizado:** 15.885 comentarios (Facebook: 11.529, Instagram: 4.126, YouTube: 230).

---

## 1. Distribución Temática Replicada

| Categoría Temática | N Comentarios | % Corpus |
|---|---:|---:|
| Otros temas no identificados (residual sustantivo) | 5.501 | 34,63 % |
| Sin contenido temático suficiente (social/emoji/mención) | 4.004 | 25,21 % |
| Felicitaciones y expresiones de aprecio | 2.405 | 15,14 % |
| Oferta académica e investigación | 1.426 | 8,98 % |
| Admisiones, inscripciones y matrículas | 678 | 4,27 % |
| Protesta y movilización | 603 | 3,80 % |
| Información, trámites y certificados | 460 | 2,90 % |
| Programas de acceso y bienestar | 421 | 2,65 % |
| Infraestructura, sedes y tecnología | 234 | 1,47 % |
| Eventos, cultura y actividades institucionales | 153 | 0,96 % |
| **Total comentarios analizados** | **15.885** | **100,0 %** |

- **Cobertura de temas específicos:** 6.380 / 15.885 = **40,2 %** (frente a 34,0 % del diccionario inicial).
- **Coincidencias en más de una categoría:** 1.586 de los 6.380 comentarios con coincidencia (24,9 %) cumplieron patrones de más de una categoría y se resolvieron determinísticamente por el orden de precedencia de las reglas.

---

## 2. Diagnóstico de Categorías Clave

### A. Protesta y movilización
- **Comentarios asignados:** 603 (3,80 % del corpus).
- **Efecto de depuración sobre Oferta académica:** Al retirar el término suelto `\beducaci[oó]n\b` de Oferta académica y posicionar Protesta y movilización en primer orden, **467 comentarios** que antes caían erróneamente en temas de currículo/oferta fueron reclasificados en protesta (principalmente por el hashtag recurrente `#hambredeeducacion` y variantes).
- Oferta académica se redujo de 1.941 a **1.426 comentarios**.

### B. Oferta académica e investigación
- **Términos genéricos:** 687 de 1.426 comentarios (48,2 %) se asignaron únicamente por términos de amplio espectro (`estudiante`, `programa`, `docente`, `profesor`, `clase`, `grado`, `academia`).
- Esto evidencia que el crecimiento de esta categoría respecto al inicio del proyecto (989 inicial) se explica principalmente por el vocabulario formativo amplio y no solo por la delimitación de `\bcursos?\b`.

### C. Felicitaciones y expresiones de aprecio
- **Elogio genérico:** 1.138 de 2.405 comentarios (47,3 %) se asignaron exclusivamente por términos de cortesía o aprecio genérico (`gracias`, `excelente`, `feliz`, `hermoso`, `bendiciones`), sin términos explícitos de felicitación institucional.

### D. Efecto de la normalización de emojis
- Al evaluar las asignaciones temáticas sustituyendo la descripción textual de emojis por espacios en blanco, solo **28 comentarios (0,18 %)** cambian de categoría temática. Esto demuestra que la descripción de emojis tiene un impacto marginal en la asignación de temas y no distorsiona las categorías sustantivas.

### E. Composición del Residual y Sin Contenido
- **Residual ("Otros temas no identificados", N = 5.501):**
  - Comentarios con 11 o más palabras: 1.493 (textos argumentativos o narrativos no contemplados en la taxonomía institucional).
  - Comentarios con signo de interrogación (`?`): 657 (preguntas sustantivas no administrativas).
- **Sin contenido temático suficiente (N = 4.004):**
  - Comentarios sin letras ni números (`emoji_only` o pura puntuación): 1.307.
  - Comentarios de 1 a 2 palabras con texto mínimo (saludos o menciones limpias): 2.459.
