# Diccionario de datos del CSV unificado

Los significados se derivan de `scripts/legacy/unify_comments.py` y de los nombres de campos fuente. La disponibilidad varía por plataforma; vacío significa no disponible/no extraído y no se interpreta como cero. Campos con datos personales o enlaces se excluyen del análisis compartible.

| Campo | Descripción | Uso en este proyecto |
|---|---|---|
| `comment_id` | ID prefijado por plataforma para identificar una fila de comentario. | Llave interna para deduplicar y asociar predicciones; nunca mostrar. |
| `platform` | Facebook, Instagram o YouTube. | Filtro y agrupación. |
| `parent_comment_id` | Identificador del comentario padre cuando existe. | No analizar estructura de hilos; excluir de la app. |
| `is_reply` | Indica si la fila es respuesta. | Mantener y describir solo como bandera técnica, sin comparar grupos. |
| `depth` | Nivel de anidamiento disponible. | Fuera del modelado. |
| `text` | Texto del comentario, incluidos emojis. | Entrada a modelo; datos privados. |
| `created_at` | Fecha de publicación del comentario, normalizada a UTC por el unificador. | Auditoría de presencia/cobertura solamente; sin análisis temporal. |
| `like_count` | Me gusta del comentario, cuando la plataforma lo devuelve. | Fuera del alcance. |
| `reply_count` | Número de respuestas al comentario. | Fuera del alcance. |
| `author_id` | Identificador de cuenta/autor según fuente. | No usar ni publicar. |
| `author_name` | Nombre/usuario público asociado. | No usar ni publicar. |
| `mentions` | Menciones encontradas en el comentario. | No usar en la app; normalización social puede reemplazarlas. |
| `has_attachment` | Indicador de adjunto, principalmente Facebook. | Fuera del análisis principal. |
| `comment_url` | URL del comentario. | No publicar. |
| `react_like` | Conteo de reacción “me gusta” en Facebook. | Fuera del alcance. |
| `react_love` | Conteo de reacción “me encanta” en Facebook. | Fuera del alcance. |
| `react_care` | Conteo de reacción “me importa” en Facebook. | Fuera del alcance. |
| `react_haha` | Conteo de reacción “me divierte” en Facebook. | Fuera del alcance. |
| `react_wow` | Conteo de reacción “me asombra” en Facebook. | Fuera del alcance. |
| `react_sad` | Conteo de reacción “me entristece” en Facebook. | Fuera del alcance. |
| `react_angry` | Conteo de reacción “me enoja” en Facebook. | Fuera del alcance. |
| `post_id` | ID prefijado de publicación/video relacionado. | Llave interna para contar publicaciones; no mostrar. |
| `post_url` | Enlace a publicación/video. | No publicar. |
| `post_title` | Título de video de YouTube cuando está disponible. | No se usa en texto del comentario ni se publica. |
| `post_text` | Descripción/caption de la publicación o video. | No clasificar como si fuera comentario; contexto incompleto, fuera de alcance. |
| `post_created_at` | Fecha de la publicación/video. | Fuera del análisis temporal. |
| `post_type` | Tipo de contenido informado por plataforma, por ejemplo foto/video/texto. | Agrupación opcional si cobertura suficiente. |
| `post_like_count` | Conteo de me gusta/reacciones de la publicación. | Fuera del alcance; no comparable entre plataformas. |
| `post_comment_count` | Conteo de comentarios de la publicación. | Fuera del alcance; no normalizar métricas. |
| `post_share_count` | Conteo de compartidos de la publicación. | Fuera del alcance. |
| `post_hashtags` | Etiquetas/hashtags de la publicación. | No se usa como comentario; fuera de la app. |
| `post_author` | Nombre de canal/cuenta que publica. | No se usa en este análisis. |

