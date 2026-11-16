# Fase 6 — Despliegue y comunicación

## Estado

**Completada para ejecución local y entrega del paquete.** Los agregados se generaron desde la salida del modelo y la app fue verificada localmente. La publicación remota queda a cargo del usuario.

## Productos

- `app.py`: aplicación interactiva sin modelos, sin filas individuales y sin conexión a APIs.
- `build_app_data.py`: genera únicamente conteos agrupados por plataforma, tipo, tema, sentimiento y emoción. No exporta texto, IDs o URLs.
- `data/app/`: archivos agregados consumidos por la app.
- `deploy_bundle/`: paquete autocontenido para subir como raíz de un repositorio de despliegue; incluye solo Streamlit, pandas y tablas agregadas.
- `outputs/deployment_manifest.json`: esquema y tamaño de los artefactos de despliegue y declaración de control de privacidad.

## Construcción y ejecución local

```powershell
python crisp_dm/06_deployment/build_app_data.py
streamlit run crisp_dm/06_deployment/app.py
```

Para desplegar públicamente, usar `deploy_bundle/` como raíz del proyecto de la app. Esto evita subir los archivos crudos que siguen en el repositorio de análisis y evita instalar PyTorch/Transformers en el servicio. Ejecutar `build_app_data.py` para refrescar el paquete después de regenerar resultados.

## Contenido de la interfaz

Resumen, temas sugeridos por reglas léxicas, sentimiento, emociones y una explicación del método/limitaciones. La app informa que la evaluación humana usa una muestra pequeña y solo casos concordantes no ambiguos. No hay evolución temporal, ni comentarios completos, perfiles o IDs. Los grupos con menos de 10 casos se combinan en el gráfico.

## Cierre de fase

Verificado: el paquete autocontenido contiene únicamente app, dependencias ligeras y datos agrupados; los datos agregados reflejan la evaluación humana actualizada. El usuario puede desplegar el directorio `deploy_bundle/` como raíz de un repositorio independiente. No desplegar desde la raíz del repositorio analítico, que conserva archivos de comentarios originales.
