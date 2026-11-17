"""Run Spanish sentiment/emotion inference and generate privacy-safe term counts."""
from __future__ import annotations

import json
import argparse
import hashlib
import re
import unicodedata
from collections import Counter
from pathlib import Path

import pandas as pd
from pysentimiento import create_analyzer

ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((ROOT / "config" / "analysis.json").read_text(encoding="utf-8"))
INPUT = ROOT / "data" / "preparados" / "prepared_comments.csv"
OUT = ROOT / "data" / "processed" / "model_outputs"
PHASE_OUT = Path(__file__).resolve().parent / "outputs"
SCORES = OUT / "scored_comments.csv"
TERMS = PHASE_OUT / "top_terms.csv"
THEME_RULES = Path(__file__).resolve().parent / "theme_rules.json"
SEED = 314159
CHUNK_SIZE = int(CONFIG["inference_chunk_size"])

STOPWORDS = set("a al algo algunas algunos ante antes como con contra cual cuando de del desde donde durante e el ella ellas ellos en entre era erais eran eras eres es esa esas ese eso esos esta estaba estaban estado estamos están estar estas este esto estos fue fueron fui fuimos ha había habian han hasta hay la las le les lo los mas más me mi mis mucha muchas mucho muchos muy nada ni no nos o os otra otras otro otros para pero poco por porque que quien se sea según si sin sobre son su sus te tiene todo todos tras tu tus un una unas uno unos y ya yo u universidad unillanos emoji hashtag usuario url tono piel claro medio oscuro".split())


def token_counts(texts: pd.Series) -> pd.DataFrame:
    unigrams: Counter[str] = Counter()
    bigrams: Counter[str] = Counter()
    for text in texts.fillna("").astype(str):
        tokens = [token.lower() for token in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]{2,}", text) if token.lower() not in STOPWORDS]
        unigrams.update(tokens)
        bigrams.update(f"{left} {right}" for left, right in zip(tokens, tokens[1:]) if left not in STOPWORDS and right not in STOPWORDS)
    rows = [(term, count, "unigram") for term, count in unigrams.most_common(100)]
    rows += [(term, count, "bigram") for term, count in bigrams.most_common(100)]
    return pd.DataFrame(rows, columns=["term", "frequency", "type"])


def analyzer_records(analyzer, texts: list[str], prefix: str) -> list[dict]:
    results: list[dict] = []
    for start in range(0, len(texts), CHUNK_SIZE):
        batch = texts[start : start + CHUNK_SIZE]
        predicted = analyzer.predict(batch)
        if not isinstance(predicted, list):
            predicted = [predicted]
        for result in predicted:
            row = {f"{prefix}_label": str(result.output), f"{prefix}_confidence": max(result.probas.values()) if result.probas else None}
            for label, probability in result.probas.items():
                row[f"{prefix}_p_{str(label).lower()}"] = float(probability)
            results.append(row)
        print(f"{prefix}: {min(start + len(batch), len(texts)):,}/{len(texts):,}", flush=True)
    return results


def strip_accents(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKD", str(text)) if not unicodedata.combining(char))


def compile_theme_rules(rules: dict) -> list[tuple[str, list[re.Pattern]]]:
    compiled = []
    for category in rules["categories"]:
        patterns = []
        for kw in category["keywords"]:
            pat = strip_accents(kw)
            patterns.append(re.compile(pat, re.IGNORECASE))
        compiled.append((category["name"], patterns))
    return compiled


def assign_theme_row(
    text: str,
    text_normalized: str,
    emoji_only: bool,
    compiled_categories: list[tuple[str, list[re.Pattern]]],
    rules: dict,
) -> str:
    norm = strip_accents(str(text_normalized or "").lower())
    for category_name, patterns in compiled_categories:
        for pattern in patterns:
            if pattern.search(norm):
                return category_name

    insufficient_label = rules.get(
        "insufficient_content_label",
        "Sin contenido temático suficiente (social/emoji/mención)",
    )
    if emoji_only:
        return insufficient_label

    clean_text = re.sub(r"(@\w+|https?://\S+)", "", str(text or "")).strip()
    words = re.findall(r"\b\w+\b", clean_text)
    if len(words) <= 2:
        return insufficient_label

    return rules.get("fallback", "Otros temas no identificados")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--terms-only", action="store_true", help="Recalcula frecuencias sin volver a ejecutar modelos")
    parser.add_argument("--themes-only", action="store_true", help="Reasigna temas tras editar reglas, sin volver a ejecutar modelos")
    args = parser.parse_args()
    if not INPUT.exists():
        raise FileNotFoundError("Primero ejecute crisp_dm/03_data_preparation/prepare.py")
    df = pd.read_csv(INPUT, encoding="utf-8-sig", low_memory=False)
    if df.empty:
        raise ValueError("No hay comentarios para analizar")
    PHASE_OUT.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    theme_rules_bytes = THEME_RULES.read_bytes()
    theme_rules_sha = hashlib.sha256(theme_rules_bytes).hexdigest()
    theme_rules = json.loads(theme_rules_bytes.decode("utf-8"))
    compiled_cats = compile_theme_rules(theme_rules)

    if args.themes_only:
        if not SCORES.exists():
            raise FileNotFoundError("No existen scores; ejecute el modelado completo antes de reasignar temas")
        scores = pd.read_csv(SCORES, encoding="utf-8-sig", low_memory=False)
        if len(scores) != len(df):
            raise ValueError("La tabla de scores y la tabla preparada tienen tamaños distintos")

        new_themes = [
            assign_theme_row(
                row["text"],
                row["text_normalized"],
                bool(row["emoji_only"]),
                compiled_cats,
                theme_rules,
            )
            for _, row in df.iterrows()
        ]
        scores["theme"] = new_themes
        scores.to_csv(SCORES, index=False, encoding="utf-8-sig")
        scores.groupby(["theme", "platform"], dropna=False).size().rename("n").reset_index().to_csv(PHASE_OUT / "theme_counts.csv", index=False, encoding="utf-8-sig")
        summary_file = PHASE_OUT / "model_summary.json"
        if summary_file.exists():
            summary = json.loads(summary_file.read_text(encoding="utf-8"))
            summary["topic_method"] = theme_rules["method"]
            summary["theme_rules_sha256"] = theme_rules_sha
            summary["theme_counts"] = {str(k): int(v) for k, v in scores["theme"].value_counts().items()}
            summary_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Temas reasignados con las reglas actuales; SHA-256: {theme_rules_sha}")
        return

    if df["comment_id"].duplicated().any():
        raise ValueError("Hay comment_id duplicados en los datos preparados")

    token_counts(df["text_normalized"]).to_csv(TERMS, index=False, encoding="utf-8-sig")
    if args.terms_only:
        print(f"Frecuencias recalculadas: {TERMS.relative_to(ROOT)}")
        return

    texts = df["text"].fillna("").astype(str).tolist()
    themes = [
        assign_theme_row(
            row["text"],
            row["text_normalized"],
            bool(row["emoji_only"]),
            compiled_cats,
            theme_rules,
        )
        for _, row in df.iterrows()
    ]
    print("Cargando modelo de sentimiento español…", flush=True)
    sentiment = create_analyzer(task="sentiment", lang="es")
    sentiment_rows = analyzer_records(sentiment, texts, "sentiment")
    del sentiment
    print("Cargando modelo de emoción español…", flush=True)
    emotion = create_analyzer(task="emotion", lang="es")
    emotion_rows = analyzer_records(emotion, texts, "emotion")
    scores = pd.concat([df[["comment_id", "platform", "post_id", "post_type", "is_reply", "has_emoji", "emoji_only"]].reset_index(drop=True), pd.Series(themes, name="theme"), pd.DataFrame(sentiment_rows), pd.DataFrame(emotion_rows)], axis=1)
    scores.to_csv(SCORES, index=False, encoding="utf-8-sig")
    scores.groupby(["theme", "platform"], dropna=False).size().rename("n").reset_index().to_csv(PHASE_OUT / "theme_counts.csv", index=False, encoding="utf-8-sig")
    summary = {
        "n_comments_scored": int(len(scores)),
        "sentiment_counts": {str(k): int(v) for k, v in scores["sentiment_label"].value_counts(dropna=False).items()},
        "emotion_counts": {str(k): int(v) for k, v in scores["emotion_label"].value_counts(dropna=False).items()},
        "sentiment_model": "pysentimiento robertuito-sentiment-analysis (Spanish default)",
        "emotion_model": "pysentimiento robertuito-emotion-analysis (Spanish default)",
        "input_text": "Original comment text; pysentimiento applies its own social-media preprocessing.",
        "topic_method": theme_rules["method"],
        "theme_rules": THEME_RULES.relative_to(ROOT).as_posix(),
        "theme_rules_sha256": theme_rules_sha,
        "model_outputs": SCORES.relative_to(ROOT).as_posix(),
        "topic_terms": TERMS.relative_to(ROOT).as_posix(),
        "theme_counts": {str(k): int(v) for k, v in scores["theme"].value_counts().items()},
    }
    (PHASE_OUT / "model_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Modelo listo: {len(scores):,} comentarios; salidas detalladas en {SCORES.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
