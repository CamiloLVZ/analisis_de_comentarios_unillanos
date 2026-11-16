"""Aggregate, privacy-preserving audit of the unified comments CSV."""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
INPUT = ROOT / "data" / "final" / "comments_unified.csv"
OUT = Path(__file__).resolve().parent / "outputs"
REPORT_JSON = OUT / "quality_profile.json"
REPORT_MD = OUT / "quality_report.md"


def has_emoji_or_symbol(value: object) -> bool:
    text = "" if pd.isna(value) else str(value)
    for char in text:
        cp = ord(char)
        if unicodedata.category(char) == "So" or 0x1F1E6 <= cp <= 0x1FAFF or 0x2600 <= cp <= 0x27BF:
            return True
    return False


def seems_emoji_only(value: object) -> bool:
    text = "" if pd.isna(value) else str(value)
    return bool(text.strip()) and not re.search(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ0-9]", text)


def safe_count(series: pd.Series) -> int:
    return int(series.fillna("").astype(str).str.strip().ne("").sum())


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"No se encontró el CSV unificado: {INPUT}")
    df = pd.read_csv(INPUT, encoding="utf-8-sig", dtype={"comment_id": "string", "post_id": "string"}, low_memory=False)
    required = {"comment_id", "platform", "text", "created_at", "post_id", "is_reply"}
    missing_required = sorted(required - set(df.columns))
    if missing_required:
        raise ValueError(f"Faltan campos requeridos: {missing_required}")

    df["platform"] = df["platform"].fillna("missing").astype(str).str.lower()
    text = df["text"].fillna("").astype(str)
    emoji = text.map(has_emoji_or_symbol)
    emoji_only = text.map(seems_emoji_only)
    reply = df["is_reply"].astype(str).str.lower().isin({"true", "1", "yes"})

    platforms: dict[str, dict] = {}
    for platform, part in df.groupby("platform", dropna=False, sort=True):
        mask = df["platform"].eq(platform)
        sub_text = text[mask]
        platforms[str(platform)] = {
            "comments": int(len(part)),
            "unique_comment_ids": int(part["comment_id"].nunique(dropna=True)),
            "duplicate_comment_id_rows": int(part["comment_id"].duplicated(keep=False).sum()),
            "unique_posts": int(part["post_id"].nunique(dropna=True)),
            "empty_text": int(sub_text.str.strip().eq("").sum()),
            "replies": int(reply[mask].sum()),
            "with_emoji_or_symbol_heuristic": int(emoji[mask].sum()),
            "emoji_only_heuristic": int(emoji_only[mask].sum()),
            "missing_comment_date": int(part["created_at"].isna().sum() + part["created_at"].astype(str).str.strip().eq("").sum()),
            "missing_post_text": int(part.get("post_text", pd.Series([""] * len(part), index=part.index)).fillna("").astype(str).str.strip().eq("").sum()),
        }

    dates = pd.to_datetime(df["created_at"], utc=True, errors="coerce")
    missingness = {
        col: {"missing": int(df[col].isna().sum()), "empty_string": int(df[col].astype("string").str.strip().eq("").sum())}
        for col in df.columns
    }
    global_duplicates = int(df["comment_id"].duplicated(keep=False).sum())
    data = {
        "source": INPUT.relative_to(ROOT).as_posix(),
        "rows": int(len(df)),
        "columns": list(df.columns),
        "unique_comment_ids": int(df["comment_id"].nunique(dropna=True)),
        "duplicate_comment_id_rows_global": global_duplicates,
        "unique_posts": int(df["post_id"].nunique(dropna=True)),
        "empty_text": int(text.str.strip().eq("").sum()),
        "reply_rows": int(reply.sum()),
        "with_emoji_or_symbol_heuristic": int(emoji.sum()),
        "emoji_only_heuristic": int(emoji_only.sum()),
        "comment_date_min_utc": dates.min().isoformat() if dates.notna().any() else None,
        "comment_date_max_utc": dates.max().isoformat() if dates.notna().any() else None,
        "platforms": platforms,
        "missingness": missingness,
        "caveats": [
            "Emoji detection is a Unicode heuristic and may include symbols or miss multi-codepoint graphemes.",
            "Collection completeness cannot be inferred from this CSV alone.",
            "Dates are profiled only to document coverage; temporal analysis is out of project scope.",
            "No comment text, author name, author ID, or URL is written to this profile."
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Perfil de calidad de los datos", "", f"- Archivo: `{data['source']}`", f"- Filas: **{data['rows']:,}**", f"- Columnas: **{len(df.columns)}**", f"- Comentarios únicos: **{data['unique_comment_ids']:,}**", f"- Filas con IDs duplicados: **{global_duplicates:,}**", f"- Publicaciones únicas: **{data['unique_posts']:,}**", f"- Texto vacío: **{data['empty_text']:,}**", f"- Respuestas: **{data['reply_rows']:,}**", f"- Emoji/símbolo (heurística): **{data['with_emoji_or_symbol_heuristic']:,}**", f"- Solo emoji/símbolo (heurística): **{data['emoji_only_heuristic']:,}**", f"- Fechas disponibles: {data['comment_date_min_utc']} a {data['comment_date_max_utc']} (perfil de cobertura, no análisis temporal)", "", "## Por plataforma", "", "| Plataforma | Comentarios | Publicaciones | Respuestas | Texto vacío | Emoji/símbolo* | Solo emoji/símbolo* |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, values in platforms.items():
        lines.append(f"| {name} | {values['comments']:,} | {values['unique_posts']:,} | {values['replies']:,} | {values['empty_text']:,} | {values['with_emoji_or_symbol_heuristic']:,} | {values['emoji_only_heuristic']:,} |")
    lines += ["", "*Conteos aproximados; ver limitaciones en `quality_profile.json`.", "", "## Ausencia de datos en campos", "", "Se guardaron conteos, no valores de texto. Consulte `quality_profile.json` para el resumen de campos.", "", "## Hallazgos y uso", "", "El perfil confirma el denominador que utilizarán la preparación y el análisis. Se conservarán respuestas. Los emojis se mantendrán en el original; la fase 3 probará una normalización y solo la usará si los ejemplos inspeccionados no degradan el texto. Filas sin texto se excluirán del modelado y quedarán contabilizadas.", "", "## Limitaciones", "", "- El perfil no prueba que la extracción de comentarios esté completa.", "- El conteo de emoji/símbolo es heurístico y no identifica semántica.", "- La ausencia por plataforma puede ser estructural; no equivale a cero.", "- Fechas se reportan solo como metadato de cobertura.", ""]
    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")
    print(f"Auditoría lista: {REPORT_MD.relative_to(ROOT)} ({len(df):,} filas)")


if __name__ == "__main__":
    main()
