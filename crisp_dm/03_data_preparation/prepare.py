"""Prepare analysis data while retaining the raw comments locally."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "data" / "final" / "comments_unified.csv"
CONFIG = json.loads((ROOT / "config" / "analysis.json").read_text(encoding="utf-8"))
OUT_DIR = ROOT / "data" / "preparados"
OUT_FILE = OUT_DIR / "prepared_comments.csv"
SAMPLE_FILE = ROOT / "data" / "processed" / "model_outputs" / "evaluation_sample.csv"
THEME_SAMPLE_FILE = ROOT / "data" / "processed" / "model_outputs" / "theme_review_sample.csv"
REPORT = Path(__file__).resolve().parent / "outputs" / "preparation_summary.json"
SEED = int(CONFIG["random_seed"])
PLATFORM_SAMPLE_SIZE = max(1, int(CONFIG["max_manual_sample"]) // len(CONFIG["platforms"]))
MAX_THEME_SAMPLE = int(CONFIG["max_theme_sample"])


def normalize_text(text: str) -> str:
    """Normalize social text for term exploration, keeping emoji as text tags."""
    from pysentimiento.preprocessing import preprocess_tweet

    return preprocess_tweet(text, lang="es")


def truthy(value: object) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def has_emoji_or_symbol(text: str) -> bool:
    return any(
        unicodedata.category(char) == "So"
        or 0x1F1E6 <= ord(char) <= 0x1FAFF
        or 0x2600 <= ord(char) <= 0x27BF
        for char in text
    )


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(f"No se encontró el archivo fuente: {SOURCE}")
    df = pd.read_csv(SOURCE, encoding="utf-8-sig", low_memory=False)
    required = ["comment_id", "platform", "text", "post_id", "is_reply", "post_type"]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")
    before = len(df)
    duplicate_rows = int(df["comment_id"].duplicated(keep="first").sum())
    df = df.drop_duplicates(subset=["comment_id"], keep="first").copy()
    df["text"] = df["text"].fillna("").astype(str)
    empty_rows = int(df["text"].str.strip().eq("").sum())
    df = df[df["text"].str.strip().ne("")].copy()
    df["platform"] = df["platform"].fillna("unknown").astype(str).str.lower()
    df["post_type"] = df["post_type"].fillna("unknown").astype(str).str.lower()
    df["is_reply"] = df["is_reply"].map(truthy)
    df["has_emoji"] = df["text"].map(has_emoji_or_symbol)
    df["emoji_only"] = df["has_emoji"] & ~df["text"].str.contains(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]", regex=True, na=False)
    # The original `text` is retained. The normalized text is only for term exploration.
    df["text_normalized"] = df["text"].map(normalize_text)
    df["word_count"] = df["text_normalized"].fillna("").str.findall(r"\b[\wáéíóúüñÁÉÍÓÚÜÑ]+\b").str.len()

    analysis_cols = ["comment_id", "platform", "text", "text_normalized", "post_id", "post_type", "is_reply", "has_emoji", "emoji_only", "word_count"]
    prepared = df[analysis_cols].copy()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    SAMPLE_FILE.parent.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    prepared.to_csv(OUT_FILE, index=False, encoding="utf-8-sig")

    # Reproducible sample for manual annotation. Text and comment IDs are local only.
    sample_parts = []
    for platform, group in prepared.groupby("platform", sort=True):
        count = min(PLATFORM_SAMPLE_SIZE, len(group))
        sample_parts.append(group.sample(n=count, random_state=SEED))
    sample = pd.concat(sample_parts, ignore_index=True) if sample_parts else prepared.head(0).copy()
    for column in ["sentiment_gold_1", "sentiment_gold_2", "emotion_gold_1", "emotion_gold_2"]:
        sample[column] = ""
    sample.to_csv(SAMPLE_FILE, index=False, encoding="utf-8-sig")

    theme_parts = []
    theme_quota = max(1, MAX_THEME_SAMPLE // max(1, prepared["platform"].nunique()))
    for _, group in prepared.groupby("platform", sort=True):
        theme_parts.append(group.sample(n=min(theme_quota, len(group)), random_state=SEED))
    theme_sample = pd.concat(theme_parts, ignore_index=True) if theme_parts else prepared.head(0).copy()
    theme_sample["theme_gold_1"] = ""
    theme_sample["theme_gold_2"] = ""
    theme_sample.to_csv(THEME_SAMPLE_FILE, index=False, encoding="utf-8-sig")

    summary = {
        "input_rows": before,
        "duplicate_comment_id_rows_removed": duplicate_rows,
        "empty_text_rows_removed": empty_rows,
        "prepared_rows": int(len(prepared)),
        "prepared_by_platform": {str(k): int(v) for k, v in prepared.groupby("platform").size().items()},
        "prepared_replies_retained": int(prepared["is_reply"].sum()),
        "prepared_emoji_flagged": int(prepared["has_emoji"].sum()),
        "prepared_emoji_only_flagged": int(prepared["emoji_only"].sum()),
        "manual_sample_rows": int(len(sample)),
        "sample_by_platform": {str(k): int(v) for k, v in sample.groupby("platform").size().items()},
        "theme_review_sample_rows": int(len(theme_sample)),
        "theme_review_sample_by_platform": {str(k): int(v) for k, v in theme_sample.groupby("platform").size().items()},
        "sample_seed": SEED,
        "prepared_output": OUT_FILE.relative_to(ROOT).as_posix(),
        "manual_sample_output": SAMPLE_FILE.relative_to(ROOT).as_posix(),
        "theme_review_sample_output": THEME_SAMPLE_FILE.relative_to(ROOT).as_posix(),
        "privacy_note": "Both files include comment text and internal comment IDs. They are ignored by git and must not be deployed or shared publicly."
    }
    REPORT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Preparación lista: {len(prepared):,} filas; muestra para etiquetar: {len(sample):,}.")
    print(f"Salida local: {OUT_FILE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
