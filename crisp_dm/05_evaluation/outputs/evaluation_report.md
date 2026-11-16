# Evaluación del modelo

**Estado:** `evaluated_with_two_human_annotators`.

Comparación entre dos anotadores humanos que etiquetaron la muestra de forma independiente.

Las métricas se calculan solo sobre casos en que ambas anotaciones coinciden y excluyen los casos ambiguos. El subconjunto concordante puede favorecer casos más claros; interprete las métricas con cautela.

## Sentiment
- Acuerdo entre anotaciones: 0.817 (98/120)
- Casos concordantes no ambiguos: 78
- Accuracy: 0.744
- Macro-F1: 0.739
- Por clase: `{"POS": {"support": 46, "precision": 1.0, "recall": 0.6739130434782609, "f1": 0.8051948051948052}, "NEG": {"support": 15, "precision": 0.8461538461538461, "recall": 0.7333333333333333, "f1": 0.7857142857142856}, "NEU": {"support": 17, "precision": 0.47058823529411764, "recall": 0.9411764705882353, "f1": 0.627450980392157}}`

## Emotion
- Acuerdo entre anotaciones: 0.758 (91/120)
- Casos concordantes no ambiguos: 67
- Accuracy: 0.746
- Macro-F1: 0.429
- Por clase: `{"anger": {"support": 1, "precision": 0.5, "recall": 1.0, "f1": 0.6666666666666666}, "joy": {"support": 45, "precision": 1.0, "recall": 0.6888888888888889, "f1": 0.8157894736842105}, "sadness": {"support": 3, "precision": 0.75, "recall": 1.0, "f1": 0.8571428571428571}, "fear": {"support": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0}, "surprise": {"support": 0, "precision": 0.0, "recall": 0.0, "f1": 0.0}, "disgust": {"support": 3, "precision": 0.0, "recall": 0.0, "f1": 0.0}, "others": {"support": 15, "precision": 0.5, "recall": 1.0, "f1": 0.6666666666666666}}`

## Sentimiento con umbral de confianza (análisis exploratorio)

| Confianza mínima | Casos cubiertos | Cobertura del subconjunto evaluable | Accuracy |
|---:|---:|---:|---:|
| 0.6 | 63/78 | 80.8% | 84.1% |
| 0.7 | 56/78 | 71.8% | 92.9% |
| 0.8 | 43/78 | 55.1% | 93.0% |
| 0.9 | 26/78 | 33.3% | 96.2% |

El umbral no cambia las predicciones originales: describe el desempeño al abstenerse de interpretar los casos menos confiados. La muestra es pequeña, estratificada y filtrada a anotaciones humanas concordantes no ambiguas; estas cifras son indicativas, no una garantía de precisión para el corpus completo.
