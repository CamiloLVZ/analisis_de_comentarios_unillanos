# Fase 6 — Despliegue y comunicación

## Estado

**Completada para ejecución local y entrega del paquete.** Los agregados se generaron desde la salida del modelado refinado y la aplicación fue actualizada y verificada localmente. La publicación remota queda a cargo del usuario.

## Productos

- `deploy_bundle/app.py`: aplicación interactiva canónica en Streamlit con visualizaciones por plataforma, temas refinados, sentimiento condicionado por tema institucional, polaridad global, emociones y notas de alcance.
- `build_app_data.py`: genera tablas agrupadas anónimas y actualiza los datos del bundle. No exporta texto, IDs, autores ni URLs.
- `deploy_bundle/data/app/`: directorio canónico de los agregados consumidos por la app:
  - `themes.csv`: conteos temáticos agrupados.
  - `theme_sentiment.csv`: cruce de temas por polaridad afectiva.
  - `sentiment.csv`: sentimiento global por plataforma y formato.
  - `emotions.csv`: emociones por plataforma y formato.
  - `sentiment_confidence.csv`: diagnóstico de confianza.
  - `overview.json`: metadatos y configuración general.
- `deploy_bundle/`: paquete autocontenido para subir como raíz de un repositorio de despliegue; incluye solo Streamlit, pandas y tablas agregadas.
- `outputs/deployment_manifest.json`: esquema y tamaño de los artefactos de despliegue y declaración de control de privacidad.

## Construcción y ejecución local

```powershell
python crisp_dm/06_deployment/build_app_data.py
streamlit run crisp_dm/06_deployment/deploy_bundle/app.py
```

Para desplegar públicamente, usar `deploy_bundle/` como raíz del proyecto de la app. Esto evita subir los archivos crudos que siguen en el repositorio de análisis y evita instalar PyTorch/Transformers en el servicio.

## Contenido de la interfaz

Streamlit ejecuta únicamente `deploy_bundle/app.py` y lee los archivos agregados en `data/app/`. Contiene:
1. **Resumen:** Volumen por plataforma y filtros globales.
2. **Temas:** Distribución de las 7 áreas sustantivas, la clase funcional "Sin contenido temático suficiente" y el residual "Otros temas no identificados".
3. **Sentimiento por tema:** Vista condicional que permite explorar cómo se distribuye la polaridad (POS/NEG/NEU) dentro de cada área temática de la universidad.
4. **Sentimiento global:** Polaridad general y bandas de confianza diagnósticas.
5. **Emociones:** Estimación global de emociones básicas.
6. **Método y límites:** Explicación técnica de la taxonomía, conservación de emojis, independencia del texto del post y limitaciones éticas de evaluación.

## Cierre de fase

Verificado: el paquete autocontenido contiene únicamente app, dependencias ligeras y datos agrupados; la suma de comentarios cierra de forma exacta en 15.885 sin exponer datos sensibles.
