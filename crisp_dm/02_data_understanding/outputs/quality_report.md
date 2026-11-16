# Perfil de calidad de los datos

- Archivo: `data/final/comments_unified.csv`
- Filas: **16,471**
- Columnas: **32**
- Comentarios únicos: **16,471**
- Filas con IDs duplicados: **0**
- Publicaciones únicas: **3,252**
- Texto vacío: **586**
- Respuestas: **2,502**
- Emoji/símbolo (heurística): **4,288**
- Solo emoji/símbolo (heurística): **1,307**
- Fechas disponibles: 2020-01-21T21:13:18+00:00 a 2026-11-08T14:37:53+00:00 (perfil de cobertura, no análisis temporal)

## Por plataforma

| Plataforma | Comentarios | Publicaciones | Respuestas | Texto vacío | Emoji/símbolo* | Solo emoji/símbolo* |
|---|---:|---:|---:|---:|---:|---:|
| facebook | 12,089 | 2,038 | 2,111 | 560 | 1,741 | 193 |
| instagram | 4,152 | 1,109 | 364 | 26 | 2,492 | 1,100 |
| youtube | 230 | 105 | 27 | 0 | 55 | 14 |

*Conteos aproximados; ver limitaciones en `quality_profile.json`.

## Ausencia de datos en campos

Se guardaron conteos, no valores de texto. Consulte `quality_profile.json` para el resumen de campos.

## Hallazgos y uso

El perfil confirma el denominador que utilizarán la preparación y el análisis. Se conservarán respuestas. Los emojis se mantendrán en el original; la fase 3 probará una normalización y solo la usará si los ejemplos inspeccionados no degradan el texto. Filas sin texto se excluirán del modelado y quedarán contabilizadas.

## Limitaciones

- El perfil no prueba que la extracción de comentarios esté completa.
- El conteo de emoji/símbolo es heurístico y no identifica semántica.
- La ausencia por plataforma puede ser estructural; no equivale a cero.
- Fechas se reportan solo como metadato de cobertura.
