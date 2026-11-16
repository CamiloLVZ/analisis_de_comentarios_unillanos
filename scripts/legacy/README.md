# Scripts heredados de recolección

Estos scripts se conservaron como archivo del proceso de recolección: incluyen descargas de publicaciones y comentarios, auditorías auxiliares y generación de lotes. El unificador de los JSON ya recolectados se trasladó a `crisp_dm/02_data_understanding/unify_raw_data.py`, donde forma parte de la comprensión de datos.

No son necesarios para ejecutar el análisis: la entrada canónica es `data/final/comments_unified.csv`. Los scripts de extracción contactan servicios externos y pueden requerir credenciales/dependencias que no forman parte de este proyecto. No se versionan credenciales ni se vuelven a contactar las plataformas durante el análisis.

