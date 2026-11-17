# Fase 4 — Modelado y análisis

## Estado

**Completada y actualizada.** Sentimiento y emoción se conservan intactos calculados mediante `pysentimiento` para los 15.885 comentarios analizados. Las reglas temáticas fueron refactorizadas integralmente: se sustituyó la búsqueda ingenua de subcadenas por expresiones regulares con delimitadores de palabra (`\b`), se eliminaron falsos positivos por palabras funcionales genéricas, se incorporó la categoría de infraestructura/sedes y se desacopló el ruido social/emojis del residual temático.

## Métodos ejecutados

- **Sentimiento:** `pysentimiento.create_analyzer(task="sentiment", lang="es")`, modelo español `robertuito-sentiment-analysis`.
- **Emoción:** `pysentimiento.create_analyzer(task="emotion", lang="es")`, modelo español `robertuito-emotion-analysis`.
- **Entrada del clasificador afectivo:** Texto original intacto (el modelo procesa internamente emojis y menciones).
- **Temas Refinados:** Reglas léxicas definidas manualmente compiladas con patrones regex (`\b`) en `theme_rules.json`, integrando 8 áreas sustantivas, una categoría funcional de contenido mínimo y un residual genuino:
  1. `Protesta y movilización` (captura movilizaciones y hashtags recurrentes de protesta)
  2. `Programas de acceso y bienestar`
  3. `Admisiones, inscripciones y matrículas`
  4. `Información, trámites y certificados` (sin palabras funcionales aisladas como "cuando" o "donde")
  5. `Oferta académica e investigación` (sin el término suelto "educación", evitando capturar lemas de protesta)
  6. `Infraestructura, sedes y tecnología` (categoría rescatada del residual)
  7. `Eventos, cultura y actividades institucionales`
  8. `Felicitaciones y expresiones de aprecio` (renombrada; expresiones de elogio, bendiciones y agradecimiento)
  9. `Sin contenido temático suficiente (social/emoji/mención)` (comentarios `emoji_only` o con $\le 2$ palabras tras limpiar menciones)
  10. `Otros temas no identificados` (residual genuino)
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

### Taxonomía Temática Refinada y Congelada (SHA-256: `a69292d738828d2bbd1c8569b5dea235b404e7cd59708e811868bf0f969f3266`)
| Tema asignado por reglas | Comentarios | Porcentaje |
|---|---:|---:|
| Otros temas no identificados (residual sustantivo) | 5.501 | 34,6 % |
| Sin contenido temático suficiente (social/emoji/mención) | 4.004 | 25,2 % |
| Felicitaciones y expresiones de aprecio | 2.405 | 15,1 % |
| Oferta académica e investigación | 1.426 | 9,0 % |
| Admisiones, inscripciones y matrículas | 678 | 4,3 % |
| Protesta y movilización | 603 | 3,8 % |
| Información, trámites y certificados | 460 | 2,9 % |
| Programas de acceso y bienestar | 421 | 2,7 % |
| Infraestructura, sedes y tecnología | 234 | 1,5 % |
| Eventos, cultura y actividades institucionales | 153 | 1,0 % |

### Patrones de "Protesta y movilización" (orden de evaluación 1)
Se definieron 8 patrones estrechos sobre texto normalizado y sin acentos, capturando un total de 603 comentarios (3,80 % del corpus):
1. `hambre de educacion`: 432 comentarios (eslogan y hashtag recurrente de movilización estudiantil).
2. `habre de educacion`: 22 comentarios (variante con errata frecuente en redes).
3. `hambredeeducacion`: 118 comentarios (variante compacta sin espacios).
4. `huelga\w*`: 34 comentarios.
5. `\bprotest\w*`: 6 comentarios.
6. `\bmovilizaci\w*`: 4 comentarios.
7. `\bmanifestaci\w*`: 2 comentarios.
8. `\bplanton\b`: 2 comentarios.

Total con coincidencia en la categoría: 603 comentarios únicos. De ellos, 467 contenían el término "educación" que antes caía erróneamente en "Oferta académica e investigación".

### Comparación con el Esquema Inicial
En el esquema previo, el residual `"Otros / tema no identificado"` abarcaba **10.486 comentarios (66,0 %)** debido a la mezcla de comentarios sin contenido textual con temas no previstos. Con la refactorización:
- El residual genuino cayó a **5.501 comentarios (34,6 %)**.
- Se aislaron **4.004 comentarios (25,2 %)** de carácter puramente interaccional (emojis, menciones vacías a amigos, saludos de dos palabras).
- La cobertura de áreas temáticas sustantivas de la universidad aumentó con mayor precisión y sin colisiones léxicas.

## Salidas y uso

- `outputs/top_terms.csv`: frecuencias de 100 unigramas y 100 bigramas.
- `outputs/theme_counts.csv`: conteos temáticos agregados por plataforma ($N = 15.885$).
- `outputs/model_summary.json`: metadatos de modelos, parámetros, conteos globales consolidados y `theme_rules_sha256`.
- `data/processed/model_outputs/scored_comments.csv`: tabla analítica con todas las columnas afectivas originales y la columna `theme` actualizada ($N = 15.885$).

## Reproducibilidad

```powershell
python crisp_dm/04_modeling/analyze.py --themes-only
python crisp_dm/04_modeling/analyze.py --terms-only
```
