# Flujo de trabajo del proyecto

## Para qué sirve este archivo

Esta es la guía de entrada para estudiantes, colaboradores y agentes IA. Explica el objetivo, la organización del repositorio, el orden de ejecución, las decisiones metodológicas y el estado verificable del proyecto. Actualizar la tabla de avance cada vez que una fase CRISP-DM termine o cambie de estado.

## Objetivo del proyecto

Identificar los temas, el sentimiento (positivo, negativo, neutral) y las emociones expresadas en los comentarios recolectados de Facebook, Instagram y YouTube de Unillanos. La aplicación final presenta resultados agregados en Streamlit. El alcance excluye análisis temporal, diferencias entre respuestas y comentarios principales, despliegue remoto por el agente y conclusiones representativas de toda la comunidad universitaria.

## Principios para trabajar en este repositorio

1. No modificar ni regenerar los datos originales de `data/raw/`.
2. No versionar secretos (`.env`), entorno virtual, ni copias de comentarios identificables. El texto completo y los identificadores se mantienen solo donde sean necesarios para el análisis local.
3. Registrar cada fase en `crisp_dm/NN_nombre/README.md`: qué se hizo, qué se encontró, decisiones, salidas, interpretación, limitaciones y uso de las salidas en la fase siguiente.
4. Mantener un proceso reproducible en archivos `.py`; no crear notebooks.
5. No ejecutar los modelos dentro de la aplicación. La inferencia se ejecuta una vez por script y la aplicación carga resultados agregados seguros.
6. Conservar emojis en el texto original y generar una versión de texto normalizado para el modelo cuando el preprocesador pueda describirlos adecuadamente. No borrar respuestas solo por estar anidadas; analizar su texto individual y no inferir el sentido del hilo.
7. Tratar predicciones como estimaciones. Evaluar una muestra manual y mostrar el volumen junto a los porcentajes.
8. Nunca mostrar identificadores/nombres de autor, URLs de perfiles o comentarios íntegros en la app pública.

## Arquitectura prevista

```text
.
├── FLUJO_DE_TRABAJO.md             # Esta guía y estado de avance
├── PLAN_MAESTRO.md                 # Objetivos, alcance, entregables y criterios de éxito
├── README.md                       # Inicio rápido para usuarios del proyecto
├── requirements.txt                # Dependencias de análisis y aplicación
├── config/
│   └── analysis.json               # Parámetros no secretos del análisis
├── crisp_dm/
│   ├── 01_business_understanding/  # Planteamiento, alcance, decisiones
│   ├── 02_data_understanding/      # README, auditoría y resultados
│   ├── 03_data_preparation/        # README, preparación y resumen
│   ├── 04_modeling/                # README, modelo, reglas y resultados
│   ├── 05_evaluation/              # README, evaluación y métricas
│   └── 06_deployment/              # README, generador y deploy_bundle/ con app + datos
├── scripts/legacy/                 # Extracción y unificación anteriores
└── data/
    ├── raw/                        # Entradas originales, solo lectura
    ├── preparados/                 # Datos de trabajo preparados, de acceso local
    └── processed/                  # Datos analíticos derivados
```

Cada fase guarda su README, su script si corresponde, sus parámetros y/o salidas en su propia carpeta. Los datos por comentario se conservan localmente bajo `data/`; solo `crisp_dm/06_deployment/deploy_bundle/data/app/` contiene agregados para despliegue. Los scripts antiguos de recolección permanecen archivados en `scripts/legacy/`.

## Orden de ejecución

1. **Comprensión del negocio:** fijar preguntas contestables, alcance y éxito.
2. **Comprensión de datos:** perfilar insumos, cobertura, campos, faltantes y riesgos.
3. **Preparación:** normalizar texto sin destruir el original y crear conjuntos analíticos.
4. **Modelado:** identificar temas y producir predicciones de sentimiento/emoción.
5. **Evaluación:** contrastar con etiquetas humanas, revisar errores y congelar resultados.
6. **Despliegue:** generar tablas agregadas, construir la app y documentar ejecución.
7. **Artículo final:** resumir el método y resultados verificables sin inventar evidencia.

Comandos planeados (se ajustan si la auditoría encuentra otra fuente unificada):

```powershell
python crisp_dm/02_data_understanding/audit.py
python crisp_dm/03_data_preparation/prepare.py
python crisp_dm/04_modeling/analyze.py
python crisp_dm/05_evaluation/evaluate.py
python crisp_dm/06_deployment/build_app_data.py
streamlit run crisp_dm/06_deployment/deploy_bundle/app.py
```

Si la inferencia de emoción o sentimiento no puede ejecutarse por limitaciones de instalación, descarga o recursos, el flujo debe fallar de forma explícita y no sustituir silenciosamente el modelo por reglas de palabras. Una ejecución sin red solo puede utilizar modelos cacheados.

## Registro de avance

Se usa **Pendiente**, **En curso**, **Completado** o **Bloqueado**, con evidencia/artefacto para evitar marcar como realizado algo que solo está planeado.

| Fase/actividad | Estado | Evidencia / próxima acción |
|---|---|---|
| Flujo de trabajo y plan maestro | Completado | `FLUJO_DE_TRABAJO.md` y `PLAN_MAESTRO.md` |
| 1. Comprensión del negocio | Completado | `crisp_dm/01_business_understanding/README.md` |
| 2. Comprensión de datos | Completado | `outputs/quality_profile.json`, reporte y diccionario resumido |
| 3. Preparación | Completado | 15.885 filas preparadas y plantilla local de 120 |
| 4. Modelado | Completado | 15.885 textos puntuados; reglas temáticas y resumen reproducibles |
| 5. Evaluación | Completado | 120 comentarios con anotación independiente por dos personas; acuerdo y métricas reproducibles en `crisp_dm/05_evaluation/outputs/` |
| 6. Despliegue | Paquete local preparado | Agregados actualizados con estado de evaluación humana; bundle aislado listo para publicar desde repositorio separado |
| Artículo final | Completado | `ARTICULO_FINAL.md`, incluye resultados y limita inferencias a lo observado |
| Entorno/dependencias | Completado | Entorno local instalado, `pip check` limpio, scripts compilan |

