"""Compare two blinded annotators with model predictions using only stdlib."""
from __future__ import annotations

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SAMPLE = ROOT / "data" / "processed" / "model_outputs" / "evaluation_sample.csv"
SCORES = ROOT / "data" / "processed" / "model_outputs" / "scored_comments.csv"
OUT = Path(__file__).resolve().parent / "outputs"

SENTIMENT_MAP = {
    "pos": "POS", "positive": "POS", "positivo": "POS",
    "neg": "NEG", "negative": "NEG", "negativo": "NEG",
    "neu": "NEU", "neutral": "NEU", "neutro": "NEU",
    "ambiguous": "AMBIGUO", "ambiguo": "AMBIGUO", "no clasificable": "AMBIGUO",
}
EMOTION_MAP = {
    "joy": "joy", "alegria": "joy", "alegría": "joy",
    "anger": "anger", "enojo": "anger", "ira": "anger",
    "sadness": "sadness", "tristeza": "sadness",
    "fear": "fear", "miedo": "fear", "surprise": "surprise", "sorpresa": "surprise",
    "disgust": "disgust", "disgusto": "disgust", "neutral": "others", "neutro": "others",
    "others": "others", "other": "others", "otros": "others",
    "sin emoción básica clara": "others", "ambiguous": "ambiguous", "ambiguo": "ambiguous",
    "no clasificable": "ambiguous",
}


def normalize(value: object, mapping: dict[str, str]) -> str:
    text = str(value or "").strip().lower()
    return mapping.get(text, text.upper() if mapping is SENTIMENT_MAP else text)


def score(y_true: list[str], y_pred: list[str], expected_labels: list[str]) -> dict:
    labels = list(expected_labels)
    labels.extend(sorted((set(y_true) | set(y_pred)) - set(labels)))
    matrix = {actual: {pred: 0 for pred in labels} for actual in labels}
    for actual, pred in zip(y_true, y_pred):
        matrix[actual][pred] += 1
    per_class = {}
    f1_values = []
    for label in labels:
        tp = matrix[label][label]
        fp = sum(matrix[other][label] for other in labels if other != label)
        fn = sum(matrix[label][other] for other in labels if other != label)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {"support": sum(matrix[label].values()), "precision": precision, "recall": recall, "f1": f1}
        f1_values.append(f1)
    return {
        "n": len(y_true),
        "accuracy": sum(actual == predicted for actual, predicted in zip(y_true, y_pred)) / len(y_true) if y_true else None,
        "macro_f1": sum(f1_values) / len(f1_values) if f1_values else None,
        "per_class": per_class,
        "confusion_matrix": matrix,
    }


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if not SAMPLE.exists() or not SCORES.exists():
        report = {"status": "pending", "message": "Ejecute las fases 3 y 4 y complete la muestra de evaluación."}
    else:
        sample = read_rows(SAMPLE)
        scores = read_rows(SCORES)
        score_by_id = {row["comment_id"]: row for row in scores}
        missing_score_ids = [row.get("comment_id", "") for row in sample if row.get("comment_id", "") not in score_by_id]
        if missing_score_ids:
            raise ValueError(f"Hay {len(missing_score_ids)} filas de la muestra sin predicción asociada.")
        required = ["sentiment_gold_1", "sentiment_gold_2", "emotion_gold_1", "emotion_gold_2"]
        absent = [column for column in required if column not in sample[0]]
        if absent:
            raise ValueError(f"Faltan columnas de anotación: {absent}")

        report = {
            "status": "pending_labels",
            "sample_rows": len(sample),
            "annotation_note": "Comparación entre dos anotadores humanos que etiquetaron la muestra de forma independiente.",
            "sentiment": {},
            "emotion": {},
            "annotator_agreement": {},
        }
        for task, mapping in (("sentiment", SENTIMENT_MAP), ("emotion", EMOTION_MAP)):
            coder1 = [normalize(row.get(f"{task}_gold_1"), mapping) for row in sample]
            coder2 = [normalize(row.get(f"{task}_gold_2"), mapping) for row in sample]
            model = [normalize(score_by_id[row["comment_id"]].get(f"{task}_label"), mapping) for row in sample]
            paired = [bool(first and second) for first, second in zip(coder1, coder2)]
            agreed = [both and first == second for both, first, second in zip(paired, coder1, coder2)]
            agreement_n = sum(paired)
            agreement_count = sum(agreed)
            report["annotator_agreement"][task] = {
                "both_labeled": agreement_n,
                "agreed": agreement_count,
                "agreement": agreement_count / agreement_n if agreement_n else None,
            }
            excluded_labels = {"AMBIGUO", "ambiguous"}
            valid = [
                idx for idx, is_agreed in enumerate(agreed)
                if is_agreed and model[idx] and coder1[idx] not in excluded_labels
            ]
            expected = ["POS", "NEG", "NEU"] if task == "sentiment" else ["anger", "joy", "sadness", "fear", "surprise", "disgust", "others"]
            report[task] = {
                "agreed_usable_annotations": len(valid),
                "unresolved_or_ambiguous": sum(both and not is_agreed for both, is_agreed in zip(paired, agreed)),
                "metrics": score([coder1[i] for i in valid], [model[i] for i in valid], expected),
            }

        evaluated = [task for task in ("sentiment", "emotion") if report[task]["metrics"]["n"]]
        if len(evaluated) == 2:
            report["status"] = "evaluated_with_two_human_annotators"
        elif evaluated:
            report["status"] = "partially_evaluated_with_two_human_annotators"

    (OUT / "evaluation_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# Evaluación del modelo", "", f"**Estado:** `{report['status']}`.", ""]
    if report["status"] == "pending":
        lines.append(report["message"])
    else:
        lines += [report.get("annotation_note", ""), "", "Las métricas se calculan solo sobre casos en que ambas anotaciones coinciden y excluyen los casos ambiguos. El subconjunto concordante puede favorecer casos más claros; interprete las métricas con cautela."]
        for task in ("sentiment", "emotion"):
            details = report[task]
            metrics = details["metrics"]
            agreement = report["annotator_agreement"][task]
            lines += ["", f"## {task.title()}", f"- Acuerdo entre anotaciones: {agreement['agreement']:.3f} ({agreement['agreed']}/{agreement['both_labeled']})" if agreement["agreement"] is not None else "- No hay pares etiquetados."]
            if metrics["n"]:
                lines += [f"- Casos concordantes no ambiguos: {metrics['n']}", f"- Accuracy: {metrics['accuracy']:.3f}", f"- Macro-F1: {metrics['macro_f1']:.3f}", f"- Por clase: `{json.dumps(metrics['per_class'], ensure_ascii=False)}`"]
            else:
                lines.append("- No hay suficientes etiquetas concordantes y no ambiguas para calcular métricas.")
    (OUT / "evaluation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Evaluación: {report['status']}")


if __name__ == "__main__":
    main()
