# Guión Técnico y de Locución para Presentación de Proyecto
## Análisis Descriptivo de Comentarios Institucionales de la Universidad de los Llanos

* **Duración estimada:** Máximo 3 minutos (180 segundos / ~410 palabras)
* **Autores:** Juan Camilo Londoño Velásquez y Juan David Burgos Atuesta
* **Metodología:** CRISP-DM
* **Corpus analizado:** 15.885 comentarios (Facebook, Instagram, YouTube)
* **Documento PDF oficial:** [GUION_VIDEO_PRESENTACION_UNILLANOS.pdf](file:///c:/Users/camil/Documents/Projects/Analisis%20de%20Datos/analisis_de_comentarios_unillanos/docs/GUION_VIDEO_PRESENTACION_UNILLANOS.pdf)

---

### BLOQUE 1: Introducción, Alcance y Métricas Generales (0:00 – 0:30 | 30 seg)

* **Visual en pantalla (Acción en la app):**  
  Abrir la aplicación en la pestaña **Resumen**. Mostrar la barra lateral de filtros (Facebook, Instagram, YouTube) y las 4 tarjetas de métricas superiores (*15.885 comentarios analizados*).
* **Guión de voz en off (Locución exacta):**  
  > *"Hola a todos. En este proyecto desarrollamos un marco de análisis descriptivo bajo el estándar CRISP-DM para auditar y comprender la conversación digital en las cuentas institucionales de la Universidad de los Llanos en Facebook, Instagram y YouTube. Recopilamos 16.471 registros que, tras una estricta auditoría de calidad y remoción de filas sin texto, consolidaron un corpus de 15.885 comentarios analizables. La aplicación que observan permite explorar tres dimensiones articuladas: las temáticas institucionales, la polaridad de sentimiento y las emociones expresadas por la comunidad."*
* **Claves de interpretación de los datos:**  
  *Lectura de la distribución por plataforma:* Facebook concentra el 72,6 % del volumen (11.529 comentarios), mientras Instagram aporta el 26,0 % (4.126) y YouTube el 1,4 % (230). Esto refleja que los conteos absolutos no deben compararse como tasas de éxito o alcance relativo, sino como el nivel de actividad y hábitos de participación capturados en cada canal.

---

### BLOQUE 2: Taxonomía Temática y Desarticulación del Residual (0:30 – 1:15 | 45 seg)

* **Visual en pantalla (Acción en la app):**  
  Pasar a la pestaña **Temas**. Resaltar la gráfica horizontal con porcentajes por tema y la gráfica de pastel de macro-categorías (*Temas específicos: 40,2 %, Otros residual: 34,6 %, Sin contenido: 25,2 %*). Hacer hover sobre *Protesta y movilización* y *Felicitaciones*.
* **Guión de voz en off (Locución exacta):**  
  > *"Estructuramos una taxonomía de reglas léxicas compiladas con límites de palabra (`\b`) y orden de precedencia fija, congelada formalmente mediante hash SHA-256 antes de la evaluación. A diferencia de enfoques clásicos donde el residual absorbe dos tercios del corpus, nuestra estrategia aisló un 25,2 % de mensajes sin contenido proposicional (solo emojis o saludos) y elevó la cobertura de temas específicos al 40,2 %. Sobresale la incorporación de Protesta y movilización en primer orden con 603 comentarios, corrigiendo 467 falsos positivos que antes caían erróneamente en temas académicos."*
* **Claves de interpretación de los datos:**  
  * *Instagram vs. Facebook:* En Instagram, el 41,4 % de los comentarios es "Sin contenido suficiente" (comunidad altamente visual que reacciona con emojis o menciones limpias). En contraste, Facebook concentra el 98,3 % de toda la protesta estudiantil (`#hambredeeducacion`), operando como el ágora de debate y reclamo político.  
  * *Residual genuino:* El 34,6 % en "Otros" representa un residual sustantivo real: preguntas atípicas y reflexiones que no caben en un catálogo cerrado.

---

### BLOQUE 3: Sentimiento por Tema y Advertencia Metodológica (1:15 – 1:55 | 40 seg)

* **Visual en pantalla (Acción en la app):**  
  Pasar a **Sentimiento por tema**. Seleccionar en el menú *Protesta y movilización* (mostrar la dona con 22,7 % negativo y 75 % neutral) y luego *Felicitaciones y aprecio* (mostrar 82,5 % positivo). Bajar al gráfico de barras apiladas al 100 % que compara todas las áreas temáticas.
* **Guión de voz en off (Locución exacta):**  
  > *"Procesamos el afecto con modelos RoBERTuito preentrenados en español. Al cruzar temática con sentimiento surgen hallazgos cruciales: mientras Protesta exhibe un 22,7 % negativo y 75 % neutro por consignas informativas, Felicitaciones alcanza un 82,5 % de positividad. Sin embargo, aplicamos un principio de honestidad científica: la categoría de felicitaciones se define por palabras de elogio que el modelo asocia de inmediato con polaridad positiva. Por tanto, parte sustancial de esa correlación es por diseño de construcción de la regla y no un descubrimiento empírico independiente."*
* **Claves de interpretación de los datos:**  
  *Interpretación de la barra apilada 100 %:* Permite diagnosticar la "temperatura afectiva" de cada área. *Admisiones e inscripciones* presenta una alta tasa de fricción negativa (25,8 %), revelando inquietudes y reclamos sobre fechas y cupos. En cambio, *Oferta académica* muestra un balance constructivo (38,6 % positivo frente a 25,9 % negativo), donde las dudas curriculares conviven con el aprecio hacia programas y grados.

---

### BLOQUE 4: Validación Humana y Visualizaciones Avanzadas (1:55 – 2:35 | 40 seg)

* **Visual en pantalla (Acción en la app):**  
  Pasar a la pestaña **Visualizaciones avanzadas**. Mostrar primero el **Cuadrante de Impacto (Scatter Plot)** apuntando a las burbujas de Protesta, Admisiones e Infraestructura. Bajar enseguida al **Diagrama de Sankey** y pasar el cursor sobre los flujos entre plataformas y temas.
* **Guión de voz en off (Locución exacta):**  
  > *"Para validar las reglas, ambos autores evaluamos a ciegas una muestra estratificada independiente de 198 comentarios. Obtuvimos un acuerdo inter-anotador sustancial de $\kappa = 0,623$ y una coincidencia de categoría exacta del 56,2 % frente a las reglas. En esta sección avanzada, el Cuadrante de Impacto cruza el volumen frente a la negatividad: la línea horizontal marca el promedio del corpus (14,6 %). Temas como Admisiones e Infraestructura se sitúan en el cuadrante superior de puntos de dolor focalizados. Abajo, el Diagrama de Sankey mapea visualmente cómo el tráfico fluye desde cada red hacia los tópicos y la polaridad final."*
* **Claves de interpretación de los datos:**  
  * *Cuadrante:* Separa dos tipos de problemas: *Protesta* es un evento de alto volumen y alta visibilidad; mientras que *Infraestructura* (23,5 %) y *Admisiones* (25,8 %) son temas de menor volumen pero con tasas de quejas que casi duplican la media institucional (14,6 % negativo), señalando cuellos de botella operativos en sedes y matrículas.  
  * *Sankey:* Demuestra que la negatividad institucional se origina mayoritariamente en Facebook hacia trámites y admisiones, mientras Instagram drena hacia positividad en felicitaciones.

---

### BLOQUE 5: Perfil Emocional, Privacidad y Conclusión (2:35 – 3:00 | 25 seg)

* **Visual en pantalla (Acción en la app):**  
  Mostrar brevemente el **Radar Emocional** por plataforma en la misma pestaña avanzada. Finalizar en la pestaña **Método y límites** mostrando el texto de privacidad y el enlace a GitHub.
* **Guión de voz en off (Locución exacta):**  
  > *"Finalmente, el gráfico de Radar evidencia que la huella emocional de Instagram se expande fuertemente hacia la alegría (32 %), mientras Facebook abarca mayor tensión con picos en enojo y tristeza. Respecto a la ética, la aplicación opera exclusivamente con datos agregados y supresión de celdas menores a 10 comentarios, garantizando que ningún texto privado ni usuario sea expuesto. Este proyecto aporta una herramienta analítica auditable, reproducible y transparente para la comunidad académica. ¡Muchas gracias!"*
* **Claves de interpretación de los datos:**  
  *Interpretación del Radar de Emociones:* Dos tercios del corpus (66,8 %) caen en la categoría "Otros", lo que demuestra que los comentarios universitarios son primordialmente informativos, transaccionales y sin desborde emocional. Instagram amplifica la alegría y el reconocimiento estético, mientras Facebook canaliza las demandas ciudadanas y estudiantiles.

---

### Recomendaciones clave para la grabación del video:
1. **Ritmo de locución:** Mantener una velocidad moderada (~130 palabras por minuto). El texto de voz suma exactamente 410 palabras (unos 2 minutos y 45 segundos de habla natural).
2. **Zoom de pantalla:** Grabar la ventana de Streamlit a un 90 % de escala para que las gráficas interactivas de Plotly se aprecien íntegras sin desplazamiento brusco.
3. **Interacción suave:** Desplazar el cursor pausadamente sobre las barras y burbujas clave para activar las etiquetas flotantes (*tooltips*) justo cuando se mencionen en el audio.
