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

La primera ejecución de modelado descarga los analizadores de sentimiento y emoción de `pysentimiento`. La fase de modelado puede tomar varios minutos en CPU. Después la aplicación utiliza resultados agregados guardados y no ejecuta los modelos.

## Estructura

- `FLUJO_DE_TRABAJO.md`: guía para estudiantes/agentes y registro de avance.
- `PLAN_MAESTRO.md`: objetivo, preguntas, alcance, fases, riesgos y productos.
- `crisp_dm/01...06_*/`: cada fase contiene su documentación, scripts, salidas y decisiones.
- `data/raw/`: capturas originales; no modificar.
- `data/final/comments_unified.csv`: entrada canónica actual.
- `data/preparados/` y `data/processed/model_outputs/`: datos derivados locales con textos/IDs; no desplegar.
- `crisp_dm/06_deployment/deploy_bundle/`: app canónica y única copia de las tablas agregadas seguras, recomendado como raíz del despliegue público.
- `scripts/legacy/`: scripts históricos de extracción/unificación, no requeridos para ejecutar el análisis.
- `ARTICULO_FINAL.md`: artículo simplificado con resultados realmente producidos.

## Privacidad y alcance

La app no muestra texto, autor, ID, URLs o fechas. Los datos de trabajo por comentario son locales y están ignorados por Git. No se analiza evolución temporal, no se comparan respuestas con comentarios principales y los hallazgos no representan necesariamente a toda la comunidad universitaria. Consulte [plan maestro](PLAN_MAESTRO.md) y la documentación de cada fase antes de interpretar resultados.
