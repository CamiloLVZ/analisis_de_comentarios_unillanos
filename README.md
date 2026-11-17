# Temas y emociones en comentarios de Unillanos

Proyecto académico exploratorio implementado con CRISP-DM. Analiza los comentarios recolectados de Facebook, Instagram y YouTube para describir temas, polaridad de sentimiento y emociones; presenta agregados en una aplicación Streamlit.

## Requisitos

- Python 3.12 recomendado (la inferencia depende de PyTorch/Transformers).
- Conexión a internet la primera vez para descargar los modelos en español de `pysentimiento`.
- Espacio de disco para PyTorch, dependencias y pesos de modelos.

## Instalación en Windows PowerShell

```powershell
python -m venv .venv_project
.\.venv_project\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Si la política de PowerShell impide activar el entorno, invoque `\.venv_project\Scripts\python.exe` en los comandos siguientes.

## Ejecución en orden

El proyecto ya incluye el CSV unificado. Solo si necesitas reconstruirlo a partir de los JSON guardados en `data/raw/`, ejecuta primero el unificador de fase 2. Sin `--output`, este reemplaza `data/final/comments_unified.csv`; usa `--output` para escribir a otra ruta.

```powershell
python crisp_dm/02_data_understanding/unify_raw_data.py
```

```powershell
python crisp_dm/02_data_understanding/audit.py
python crisp_dm/03_data_preparation/prepare.py
python crisp_dm/04_modeling/analyze.py
python crisp_dm/05_evaluation/evaluate.py
python crisp_dm/06_deployment/build_app_data.py
streamlit run crisp_dm/06_deployment/deploy_bundle/app.py
```

La fase 5 compara anotaciones independientes de dos personas en una muestra de 120 comentarios y reporta su acuerdo y el desempeño exploratorio del modelo en los casos concordantes no ambiguos. La muestra contiene comentarios e IDs internos, permanece local y no se despliega. Para emoción, `others` significa “otros/sin emoción básica clara”.

**No ejecutes de nuevo `prepare.py` sin respaldar `evaluation_sample.csv`**, porque la preparación vuelve a crear la muestra y puede borrar las etiquetas humanas.

La primera ejecución de modelado descarga los analizadores de sentimiento y emoción de `pysentimiento`. La fase de modelado puede tomar varios minutos en CPU. Después la aplicación utiliza resultados agregados guardados y no ejecuta los modelos. La pestaña de sentimiento también muestra bandas de confianza; el umbral ≥0,7 es una referencia exploratoria basada en una muestra pequeña y no modifica las etiquetas.

## Estructura

- `crisp_dm/`: Metodología CRISP-DM estructurada en sus seis fases (01 a 06), con código fuente reproducible, auditorías de calidad y tablas agregadas.
- `crisp_dm/06_deployment/deploy_bundle/`: Aplicación web interactiva en Streamlit (`app.py`), empaquetada con sus dependencias y tablas agregadas seguras.
- `data/raw/`: Capturas originales de comentarios y publicaciones de Facebook, Instagram y YouTube.
- `data/final/comments_unified.csv`: Corpus canónico unificado y auditado (15.885 comentarios analizables).
- `docs/articulo/`: Artículo científico en formato IEEE (`articulo_unillanos.pdf`), código fuente LaTeX (`articulo_unillanos.tex`), figuras vectoriales y paquete de envío (`comentarios-unillanos.zip`).
- `docs/GUION_VIDEO_PRESENTACION_UNILLANOS.pdf`: Guion técnico del video de presentación (3 minutos) con interpretación analítica de las visualizaciones.
- `scripts/`: Utilidades del proyecto para la reproducción de figuras vectoriales del artículo (`generate_article_figures.py`).

## Privacidad y alcance

La aplicación Streamlit no expone textos individuales, nombres de usuario, identificadores ni enlaces. Opera exclusivamente sobre agregaciones precalculadas con supresión estricta de celdas con conteos reducidos ($n < 10$). Los datos de trabajo por comentario son de uso interno y están protegidos por `.gitignore`. No se realizan inferencias causales ni generalizaciones sobre la totalidad de la comunidad universitaria. Consulte la documentación técnica de cada fase CRISP-DM y el artículo científico para profundizar en los resultados.
