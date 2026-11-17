# Fase 4 — Modelado y análisis

## Estado

**Completada y actualizada.** Sentimiento y emoción se conservan intactos calculados mediante `pysentimiento` para los 15.885 comentarios analizados. Las reglas temáticas fueron refactorizadas integralmente: se sustituyó la búsqueda ingenua de subcadenas por expresiones regulares con delimitadores de palabra (`\b`), se eliminaron falsos positivos por palabras funcionales genéricas, se incorporó la categoría de infraestructura/sedes y se desacopló el ruido social/emojis del residual temático.

## Métodos ejecutados

- **Sentimiento:** `pysentimiento.create_analyzer(task="sentiment", lang="es")`, modelo español `robertuito-sentiment-analysis`.
- **Emoción:** `pysentimiento.create_analyzer(task="emotion", lang="es")`, modelo español `robertuito-emotion-analysis`.
- **Entrada del clasificador afectivo:** Texto original intacto (el modelo procesa internamente emojis y menciones).
- **Temas Refinados:** Reglas léxicas compiladas con patrones regex (`\b`) en `theme_rules.json`, integrando 7 áreas sustantivas, una categoría funcional de contenido mínimo y un residual genuino:
  1. `Programas de acceso y bienestar`
  2. `Admisiones, inscripciones y matrículas`
  3. `Información, trámites y certificados` (sin palabras funcionales aisladas como "cuando" o "donde")
  4. `Oferta académica e investigación` (con delimitador `\bcursos?\b` para evitar colisiones con concurso/recurso)
  5. `Infraestructura, sedes y tecnología` (nueva categoría rescatada del residual)
  6. `Eventos, cultura y actividades institucionales`
  7. `Felicitaciones y reconocimiento institucional`
  8. `Sin contenido temático suficiente (social/emoji/mención)` (comentarios `emoji_only` o con $\le 2$ palabras tras limpiar menciones)
  9. `Otros temas no identificados` (residual genuino)
- **Términos:** Frecuencias de unigramas y bigramas calculadas sobre la versión normalizada y filtradas de stopwords y marcadores de tokens técnicos.

## Resultados

En los **15.885** comentarios analizados, la distribución afectiva se mantuvo idéntica y reproducible:

### Sentimiento Estimado
| Sentimiento | Comentarios | Porcentaje |
|---|---:|---:|
| Neutral (NEU) | 9.250 | 58,2 % |
| Positivo (POS) | 4.312 | 27,1 % |
| Negativo (NEG) | 2.323 | 14,6 % |

### Emoción Estimada
| Salida del modelo | Significado mostrado | Comentarios | Porcentaje |
|---|---|---:|---:|
| `others` | Otros / sin emoción básica clara | 10.615 | 66,8 % |
| `joy` | Alegría | 3.916 | 24,7 % |
| `anger` | Enojo | 799 | 5,0 % |
| `sadness` | Tristeza | 466 | 2,9 % |
| `surprise` | Sorpresa | 79 | 0,5 % |
| `fear` | Miedo | 9 | 0,1 % |
| `disgust` | Disgusto | 1 | <0,1 % |

### Taxonomía Temática Refinada
| Tema asignado por reglas | Comentarios | Porcentaje |
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

### Comparación con el Esquema Inicial
En el esquema previo, el residual `"Otros / tema no identificado"` abarcaba **10.486 comentarios (66,0 %)** debido a la mezcla de comentarios sin contenido textual con temas no previstos. Con la refactorización:
- El residual genuino cayó a **5.469 comentarios (34,4 %)**.
- Se aislaron **4.090 comentarios (25,8 %)** de carácter puramente interaccional (emojis, menciones vacías a amigos, saludos de dos palabras).
- La cobertura de áreas temáticas sustantivas de la universidad aumentó con mayor precisión y sin colisiones léxicas.

## Salidas y uso

- `outputs/top_terms.csv`: frecuencias de 100 unigramas y 100 bigramas.
- `outputs/theme_counts.csv`: conteos temáticos agregados por plataforma ($N = 15.885$).
- `outputs/model_summary.json`: metadatos de modelos, parámetros y conteos globales consolidados.
- `data/processed/model_outputs/scored_comments.csv`: tabla analítica con todas las columnas afectivas originales y la columna `theme` actualizada ($N = 15.885$).

## Reproducibilidad

```powershell
python crisp_dm/04_modeling/analyze.py --themes-only
python crisp_dm/04_modeling/analyze.py --terms-only
```
