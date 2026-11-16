# Fase 2 — Comprensión de los datos

## Estado

**Completada.** Auditoría reproducible ejecutada con `audit.py`.

## Fuente y ejecución

Entrada: `data/final/comments_unified.csv`, CSV UTF-8 con BOM; una fila por comentario. Los JSON ya recolectados están en `data/raw/`. Si se necesita reconstruir el CSV canónico, la fase incluye `unify_raw_data.py`; este combina archivos locales y no llama a las APIs.

```powershell
# Opcional: reconstruir desde los JSON locales. Por defecto sobrescribe el CSV canónico.
python crisp_dm/02_data_understanding/unify_raw_data.py

# Para comprobar la reconstrucción sin tocar el archivo canónico:
python crisp_dm/02_data_understanding/unify_raw_data.py --output data/final/comments_unified.check.csv

# Auditar el CSV canónico:
python crisp_dm/02_data_understanding/audit.py
```

## Hallazgos

El archivo contiene **16.471 filas, 32 columnas, 16.471 IDs de comentario únicos y 3.252 publicaciones/videos asociados**. No hay IDs duplicados. Hay **586 textos vacíos** (560 Facebook, 26 Instagram), que se excluyen del modelado, pero se contabilizan. Quedan **15.885 comentarios con texto**.

Se identificaron **2.502 respuestas** (15,2 %) y se mantendrán. El conteo heurístico identifica **4.288 comentarios con emojis/símbolos** (26,0 %) y **1.307 aparentemente solo emojis/símbolos** (7,9 %). En Instagram 2.492/4.152 tienen al menos un carácter identificado como emoji/símbolo y 1.100 parecen ser solo símbolos. La diferencia de una fila respecto de conteos exploratorios anteriores se debe a la heurística Unicode; estas cifras no son una taxonomía semántica de emojis.

No se encontraron fechas de comentario vacías. El rango observado es 2020-01-21 a 2026-11-08 UTC; se registra exclusivamente como cobertura, sin análisis temporal. No puede asumirse extracción completa solo con el CSV.

YouTube tiene solo 230 comentarios; `post_like_count` está vacío para sus comentarios y `post_text` falta en 73 filas de YouTube. Estas faltas no se imputarán como cero. Los campos de autor, URLs y texto se excluyen de salidas compartibles.

## Salidas y explicación

- `outputs/quality_profile.json`: nombres de columnas, conteos de calidad y faltantes por columna/plataforma. No incluye textos, autores ni URLs.
- `outputs/quality_report.md`: resumen legible de las métricas y decisiones.
- `outputs/data_dictionary.md`: definición de los 32 campos, disponibilidad y uso/exclusión en el proyecto.

La auditoría no demostró cobertura exhaustiva de las redes; todos los resultados describen los datos capturados disponibles. Fechas se informan solo como cobertura.

## Decisiones que pasan a la fase 3

- Usar solo comentarios con texto no vacío para modelado; contabilizar los excluidos.
- Mantener respuestas y marcar su tipo.
- Mantener el original y evaluar la normalización en una copia.
- No usar autores, URLs o fechas en el análisis/app.

## Verificación

Ejecución completada: `python crisp_dm/02_data_understanding/audit.py`. Salidas verificadas: `outputs/quality_report.md` y `outputs/quality_profile.json`.
