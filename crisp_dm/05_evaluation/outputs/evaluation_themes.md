# Reporte de Evaluación Temática Formal (CRISP-DM Fase 5)

**Hash de Reglas Congeladas (SHA-256):** `a69292d738828d2bbd1c8569b5dea235b404e7cd59708e811868bf0f969f3266`
- **Muestra de Revisión:** 198 comentarios estratificados (66 por plataforma).
- **Casos Marcados como Ambiguos:** 54
- **Casos con Dependencia de Contexto (`necesita_contexto`):** 93
- **Desacuerdos entre Anotadores:** 80 filas registradas en `desacuerdos_para_resolver.csv`.

## 1. Acuerdo Inter-Anotador
- **Todas las filas (N=198):** Acuerdo Observado = 60.6%, Kappa de Cohen = 0.515
- **Excluyendo casos ambiguos (N=144):** Acuerdo Observado = 71.5%, Kappa de Cohen = 0.623

## 2. Comparación contra Reglas Léxicas (Consenso Humano)
- **Casos evaluados:** 194

| Categoría | Soporte | Precisión (IC 95%) | Recall (IC 95%) | Precisión Pond. | Recall Pond. |
|---|---:|---|---|---:|---:|
| Protesta y movilización | 12 | 100.0% ([51.0%, 100.0%]) | 33.3% ([13.8%, 60.9%]) | 100.0% | 46.9% |
| Programas de acceso y bienestar | 4 | 0.0% (n<10: no interpretable) | 0.0% (n<10: no interpretable) | 0.0% | 0.0% |
| Admisiones, inscripciones y matrículas | 6 | 33.3% (n<10: no interpretable) | 33.3% (n<10: no interpretable) | 49.1% | 49.5% |
| Información, trámites y certificados | 19 | 80.0% ([37.5%, 96.4%]) | 21.1% ([8.5%, 43.3%]) | 99.3% | 32.8% |
| Oferta académica e investigación | 13 | 38.1% ([20.8%, 59.1%]) | 61.5% ([35.5%, 82.3%]) | 69.0% | 86.8% |
| Infraestructura, sedes y tecnología | 6 | 25.0% (n<10: no interpretable) | 16.7% (n<10: no interpretable) | 1.0% | 4.4% |
| Eventos, cultura y actividades institucionales | 9 | 66.7% (n<10: no interpretable) | 22.2% (n<10: no interpretable) | 27.4% | 31.7% |
| Felicitaciones y expresiones de aprecio | 50 | 86.1% ([72.7%, 93.4%]) | 74.0% ([60.5%, 84.1%]) | 93.1% | 77.8% |
| Otros temas no identificados | 14 | 20.3% ([12.0%, 32.3%]) | 85.7% ([60.1%, 96.0%]) | 18.8% | 93.9% |
| Sin contenido temático suficiente (social/emoji/mención) | 61 | 81.2% ([68.1%, 89.8%]) | 63.9% ([51.4%, 74.8%]) | 76.4% | 44.5% |

## 3. Cobertura Real y Fuga hacia Residuales
- **Casos específicos etiquetados por humanos (sin ponderar):** 119
  - Dejados en 'Otros temas no identificados': 28 (23.5%)
  - Dejados en 'Sin contenido temático suficiente': 8 (6.7%)
- **Casos específicos etiquetados por humanos (ponderados por plataforma):** 8590.71
  - Dejados en 'Otros temas no identificados': 1425.8 (16.6%)
  - Dejados en 'Sin contenido temático suficiente': 718.56 (8.4%)

## 4. Matriz de Confusión (Filas: Consenso Humano; Columnas: Reglas Léxicas)

### A. Sin Ponderar (Conteos Muestrales)

| Humano \ Regla | Protesta | Bienestar | Admisiones | Trámites | Oferta | Infraestr. | Eventos | Felicit. | Otros | SinContenido | Total |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Protesta** | 4 | 0 | 0 | 0 | 2 | 0 | 0 | 0 | 4 | 2 | **12** |
| **Bienestar** | 0 | 0 | 1 | 0 | 0 | 2 | 0 | 0 | 0 | 1 | **4** |
| **Admisiones** | 0 | 0 | 2 | 0 | 1 | 0 | 0 | 1 | 2 | 0 | **6** |
| **Trámites** | 0 | 1 | 2 | 4 | 1 | 1 | 1 | 1 | 8 | 0 | **19** |
| **Oferta** | 0 | 0 | 1 | 0 | 8 | 0 | 0 | 0 | 4 | 0 | **13** |
| **Infraestr.** | 0 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 3 | 0 | **6** |
| **Eventos** | 0 | 0 | 0 | 1 | 1 | 0 | 2 | 1 | 4 | 0 | **9** |
| **Felicit.** | 0 | 0 | 0 | 0 | 5 | 0 | 0 | 37 | 3 | 5 | **50** |
| **Otros** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 12 | 1 | **14** |
| **SinContenido** | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 2 | 19 | 39 | **61** |
| **Total Regla** | 4 | 1 | 6 | 5 | 21 | 4 | 3 | 43 | 59 | 48 | **194** |

### B. Ponderada por Plataforma (Estimación Poblacional N=15.885)

| Humano \ Regla | Protesta | Bienestar | Admisiones | Trámites | Oferta | Infraestr. | Eventos | Felicit. | Otros | SinContenido | Total |
|:---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Protesta** | 586.6 | 0.0 | 0.0 | 0.0 | 66.0 | 0.0 | 0.0 | 0.0 | 362.2 | 237.2 | **1252.0** |
| **Bienestar** | 0.0 | 0.0 | 174.7 | 0.0 | 0.0 | 178.2 | 0.0 | 0.0 | 0.0 | 174.7 | **527.5** |
| **Admisiones** | 0.0 | 0.0 | 349.4 | 0.0 | 3.5 | 0.0 | 0.0 | 3.5 | 349.4 | 0.0 | **705.7** |
| **Trámites** | 0.0 | 174.7 | 125.0 | 474.4 | 62.5 | 174.7 | 174.7 | 3.5 | 258.1 | 0.0 | **1447.6** |
| **Oferta** | 0.0 | 0.0 | 62.5 | 0.0 | 889.8 | 0.0 | 0.0 | 0.0 | 73.0 | 0.0 | **1025.2** |
| **Infraestr.** | 0.0 | 0.0 | 0.0 | 0.0 | 7.0 | 3.5 | 0.0 | 0.0 | 69.5 | 0.0 | **79.9** |
| **Eventos** | 0.0 | 0.0 | 0.0 | 3.5 | 62.5 | 0.0 | 66.0 | 3.5 | 73.0 | 0.0 | **208.4** |
| **Felicit.** | 0.0 | 0.0 | 0.0 | 0.0 | 194.5 | 0.0 | 0.0 | 2602.4 | 240.7 | 306.7 | **3344.2** |
| **Otros** | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 0.0 | 3.5 | 1015.8 | 62.5 | **1081.8** |
| **SinContenido** | 0.0 | 0.0 | 0.0 | 0.0 | 3.5 | 0.0 | 0.0 | 178.2 | 2976.5 | 2526.8 | **5684.9** |
| **Total Regla** | 586.6 | 174.7 | 711.6 | 477.9 | 1289.2 | 356.3 | 240.7 | 2794.4 | 5418.1 | 3307.8 | **15357.4** |
