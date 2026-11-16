"""Create only grouped, non-identifying data products for the Streamlit app."""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "config" / "analysis.json").read_text(encoding="utf-8"))
SCORES = ROOT / "data" / "processed" / "model_outputs" / "scored_comments.csv"
AUDIT = ROOT / "crisp_dm" / "02_data_understanding" / "outputs" / "quality_profile.json"
EVALUATION = ROOT / "crisp_dm" / "05_evaluation" / "outputs" / "evaluation_report.json"
BUNDLE = Path(__file__).resolve().parent / "deploy_bundle"
OUT = BUNDLE / "data" / "app"
APP_FILE = BUNDLE / "app.py"
MIN_GROUP = int(CONFIG["minimum_group_size_for_app"])


def main() -> None:
    if not SCORES.exists():
        raise FileNotFoundError("Ejecute primero crisp_dm/04_modeling/analyze.py")
    scores = pd.read_csv(SCORES, encoding="utf-8-sig", low_memory=False)
    for column in ["platform", "post_type", "theme", "sentiment_label", "emotion_label"]:
        if column not in scores:
            raise ValueError(f"Falta la columna {column}; revise la salida del modelado")
    scores["post_type"] = scores["post_type"].fillna("unknown").astype(str)
    scores["platform"] = scores["platform"].fillna("unknown").astype(str)
    scores["emotion_label"] = scores["emotion_label"].replace({"others": "Otros / sin emoción básica clara"})
    OUT.mkdir(parents=True, exist_ok=True)
    products = {
        "themes.csv": ["platform", "post_type", "theme"],
        "sentiment.csv": ["platform", "post_type", "sentiment_label"],
        "emotions.csv": ["platform", "post_type", "emotion_label"],
    }
    for filename, groups in products.items():
        result = scores.groupby(groups, dropna=False).size().rename("n").reset_index()
        label = groups[-1]
        result.loc[result["n"] < MIN_GROUP, label] = "Otros grupos de baja frecuencia"
        result = result.groupby(groups, dropna=False)["n"].sum().reset_index()
        result.to_csv(OUT / filename, index=False, encoding="utf-8-sig")

    # Confidence is reported as a separate diagnostic, never as a replacement
    # for the original sentiment label. The 0.7 reference is exploratory.
    confidence = pd.to_numeric(scores["sentiment_confidence"], errors="coerce").fillna(0)
    scores["confidence_band"] = pd.cut(
        confidence,
        bins=[-float("inf"), 0.6, 0.7, float("inf")],
        labels=["Menor a 0,6", "0,6 a menor de 0,7", "0,7 o más"],
        right=False,
    ).astype(str)
    confidence_counts = (
        scores.groupby(["platform", "post_type", "confidence_band"], observed=False)
        .size().rename("n").reset_index()
    )
    confidence_counts.to_csv(OUT / "sentiment_confidence.csv", index=False, encoding="utf-8-sig")

    audit = json.loads(AUDIT.read_text(encoding="utf-8")) if AUDIT.exists() else {}
    evaluation = json.loads(EVALUATION.read_text(encoding="utf-8")) if EVALUATION.exists() else {"status": "not_run"}
    overview = {
        "title": "Temas, sentimiento y emociones en comentarios de Unillanos",
        "comments_scored": int(len(scores)),
        "platforms": {str(k): int(v) for k, v in scores.groupby("platform").size().items()},
        "post_types": sorted(scores["post_type"].dropna().astype(str).unique().tolist()),
        "themes": sorted(scores["theme"].dropna().astype(str).unique().tolist()),
        "sentiment_classes": sorted(scores["sentiment_label"].dropna().astype(str).unique().tolist()),
        "emotion_classes": sorted(scores["emotion_label"].dropna().astype(str).unique().tolist()),
        "source_rows": int(audit.get("rows", len(scores))),
        "empty_text_excluded": int(audit.get("empty_text", 0)),
        "aggregation_note": "Only grouped counts are exported. No comment text, author, comment ID, post ID, URL, or date is included.",
        "small_group_suppression_threshold": MIN_GROUP,
        "evaluation_status": evaluation.get("status", "not_run"),
    }
    (OUT / "overview.json").write_text(json.dumps(overview, ensure_ascii=False, indent=2), encoding="utf-8")
    output_inventory = {
        "overview.json": {"bytes": int((OUT / "overview.json").stat().st_size), "format": "json"}
    }
    for name in ["themes.csv", "sentiment.csv", "emotions.csv", "sentiment_confidence.csv"]:
        output_inventory[name] = {
            "bytes": int((OUT / name).stat().st_size),
            "format": "csv",
            "columns": list(pd.read_csv(OUT / name, encoding="utf-8-sig", nrows=0).columns),
        }
    manifest = {
        "outputs": output_inventory,
        "comments_aggregated": int(len(scores)),
        "threshold": MIN_GROUP,
        "privacy_check": "No text, personal identifiers, IDs, URLs, or dates are exported."
    }
    manifest_path = Path(__file__).resolve().parent / "outputs" / "deployment_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    # A small, self-contained folder for deployment. It intentionally excludes
    # the original dataset, model scores, IDs, and all analysis dependencies.
    if not APP_FILE.exists():
        raise FileNotFoundError(f"Falta la aplicación canónica: {APP_FILE}")
    BUNDLE.mkdir(parents=True, exist_ok=True)
    (BUNDLE / "requirements.txt").write_text("pandas==3.1.1\nstreamlit==1.67.0\n", encoding="utf-8")
    (BUNDLE / "README.md").write_text(
        "# Paquete de despliegue Streamlit\n\n"
        "Este directorio contiene únicamente la aplicación y datos agregados anonimizados. "
        "No incluye CSV de comentarios, autores, IDs, URLs, archivos crudos ni modelos.\n\n"
        "Instale `requirements.txt` y ejecute `streamlit run app.py`. Para desplegar, use este directorio como raíz del repositorio de la app.\n",
        encoding="utf-8",
    )
    manifest["deployment_bundle"] = "crisp_dm/06_deployment/deploy_bundle"
    manifest["bundle_contents"] = ["app.py", "requirements.txt", "README.md", "data/app/overview.json", "data/app/themes.csv", "data/app/sentiment.csv", "data/app/emotions.csv", "data/app/sentiment_confidence.csv"]
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Datos agregados para Streamlit: {len(scores):,} comentarios; sin campos identificables.")


if __name__ == "__main__":
    main()
