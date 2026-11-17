"""Evaluación formal de la taxonomía temática contra anotaciones humanas (CRISP-DM Fase 5).

Uso:
    python crisp_dm/05_evaluation/evaluate_themes.py \\
        --anotador-a data/processed/model_outputs/theme_labeling_anotador_A.csv \\
        --anotador-b data/processed/model_outputs/theme_labeling_anotador_B.csv \\
        --clave data/processed/model_outputs/theme_labeling_clave.csv \\
        --scores data/processed/model_outputs/scored_comments.csv
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
THEME_RULES = ROOT / "crisp_dm" / "04_modeling" / "theme_rules.json"
OUT_DIR = Path(__file__).resolve().parent / "outputs"

# Pesos poblacionales por plataforma (N / n)
POPULATION_N = {"facebook": 11529, "instagram": 4126, "youtube": 230}

# Mapeo de categorías humanas a categorías de reglas
HUMAN_TO_RULE_MAP = {
    "Protesta y movilización": "Protesta y movilización",
    "Programas de acceso y bienestar": "Programas de acceso y bienestar",
    "Admisiones, inscripciones y matrículas": "Admisiones, inscripciones y matrículas",
    "Información, trámites y certificados": "Información, trámites y certificados",
    "Oferta académica e investigación": "Oferta académica e investigación",
    "Infraestructura, sedes y tecnología": "Infraestructura, sedes y tecnología",
    "Eventos, cultura y actividades institucionales": "Eventos, cultura y actividades institucionales",
    "Felicitaciones y expresiones de aprecio": "Felicitaciones y expresiones de aprecio",
    "Otro tema identificable": "Otros temas no identificados",
    "Sin contenido temático": "Sin contenido temático suficiente (social/emoji/mención)",
}


def wilson_interval(successes: float, n: float, z: float = 1.96) -> Tuple[Optional[float], Optional[float]]:
    if n <= 0:
        return None, None
    p = float(successes) / float(n)
    denom = 1.0 + (z**2) / float(n)
    center = (p + (z**2) / (2.0 * float(n))) / denom
    half_width = (z * math.sqrt((p * (1.0 - p) + (z**2) / (4.0 * float(n))) / float(n))) / denom
    lower = max(0.0, center - half_width)
    upper = min(1.0, center + half_width)
    return round(float(lower), 4), round(float(upper), 4)


def cohen_kappa(y1: List[str], y2: List[str]) -> Tuple[float, float]:
    """Calcula acuerdo observado y kappa de Cohen entre dos listas de etiquetas."""
    if len(y1) != len(y2) or len(y1) == 0:
        return 0.0, 0.0
    n = len(y1)
    labels = sorted(list(set(y1) | set(y2)))
    matrix = {l1: {l2: 0 for l2 in labels} for l1 in labels}
    for a, b in zip(y1, y2):
        matrix[a][b] += 1

    po = sum(matrix[l][l] for l in labels) / n
    pe = 0.0
    for l in labels:
        row_sum = sum(matrix[l][c] for c in labels)
        col_sum = sum(matrix[r][l] for r in labels)
        pe += (row_sum * col_sum) / (n * n)

    if pe == 1.0:
        kappa = 1.0
    else:
        kappa = (po - pe) / (1.0 - pe)
    return round(po, 4), round(kappa, 4)


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluación formal de temas contra anotación humana.")
    parser.add_argument("--anotador-a", type=Path, required=True, help="Ruta al CSV de anotador A")
    parser.add_argument("--anotador-b", type=Path, required=True, help="Ruta al CSV de anotador B")
    parser.add_argument("--clave", type=Path, required=True, help="Ruta a theme_labeling_clave.csv")
    parser.add_argument("--scores", type=Path, required=True, help="Ruta a scored_comments.csv")
    parser.add_argument("--consenso", type=Path, default=None, help="Ruta a desacuerdos_para_resolver.csv con tema_final")
    args = parser.parse_args()

    for p in [args.anotador_a, args.anotador_b, args.clave, args.scores]:
        if not p.exists():
            raise FileNotFoundError(f"Archivo requerido no encontrado: {p}")

    df_a = pd.read_csv(args.anotador_a, encoding="utf-8-sig")
    df_b = pd.read_csv(args.anotador_b, encoding="utf-8-sig")
    df_clave = pd.read_csv(args.clave, encoding="utf-8-sig")
    df_scores = pd.read_csv(args.scores, encoding="utf-8-sig")

    theme_a = df_a["tema"].fillna("").astype(str).str.strip()
    theme_b = df_b["tema"].fillna("").astype(str).str.strip()

    # Si las columnas de tema están vacías, terminar limpiamente
    if theme_a.eq("").all() and theme_b.eq("").all():
        print("Las columnas 'tema' de ambos anotadores están vacías. No hay etiquetas humanas para evaluar.")
        return

    # Validar consistencia de filas
    n_rows = len(df_clave)
    if len(df_a) != n_rows or len(df_b) != n_rows:
        raise ValueError("El número de filas de los anotadores no coincide con la clave.")

    # Hash SHA-256 de theme_rules.json
    rules_sha = hashlib.sha256(THEME_RULES.read_bytes()).hexdigest() if THEME_RULES.exists() else "desconocido"

    # Conteos de ambiguos y necesita_contexto
    amb_a = df_a["ambiguo"].fillna("").astype(str).str.lower().eq("si")
    amb_b = df_b["ambiguo"].fillna("").astype(str).str.lower().eq("si")
    ctx_a = df_a["necesita_contexto"].fillna("").astype(str).str.lower().eq("si")
    ctx_b = df_b["necesita_contexto"].fillna("").astype(str).str.lower().eq("si")

    total_ambiguos = int((amb_a | amb_b | theme_a.eq("Ambiguo") | theme_b.eq("Ambiguo")).sum())
    total_necesita_ctx = int((ctx_a | ctx_b).sum())

    # Paso 1: Acuerdo entre anotadores
    # Caso 1: Todas las filas
    po_all, kappa_all = cohen_kappa(theme_a.tolist(), theme_b.tolist())

    # Caso 2: Excluyendo filas ambiguas
    no_amb_mask = ~(amb_a | amb_b | theme_a.eq("Ambiguo") | theme_b.eq("Ambiguo"))
    theme_a_noamb = theme_a[no_amb_mask].tolist()
    theme_b_noamb = theme_b[no_amb_mask].tolist()
    po_noamb, kappa_noamb = cohen_kappa(theme_a_noamb, theme_b_noamb)

    print(f"Acuerdo global: P_o = {po_all:.1%}, Kappa = {kappa_all:.3f} (N={n_rows})")
    print(f"Acuerdo sin ambiguos: P_o = {po_noamb:.1%}, Kappa = {kappa_noamb:.3f} (N={len(theme_a_noamb)})")

    # Generar desacuerdos_para_resolver.csv
    desacuerdos = []
    scores_dict = dict(zip(df_scores["comment_id"], df_scores["theme"]))
    for i in range(n_rows):
        cid = df_clave.loc[i, "comment_id"]
        plat = df_clave.loc[i, "plataforma"]
        ta = theme_a.iloc[i]
        tb = theme_b.iloc[i]
        txt = df_a.loc[i, "texto"]
        es_desacuerdo = (ta != tb) or (ta == "Ambiguo") or (tb == "Ambiguo")
        if es_desacuerdo:
            desacuerdos.append({
                "id_fila": i + 1,
                "comment_id": cid,
                "plataforma": plat,
                "texto": txt,
                "tema_anotador_A": ta,
                "tema_anotador_B": tb,
                "ambiguo_A": "si" if amb_a.iloc[i] else "no",
                "ambiguo_B": "si" if amb_b.iloc[i] else "no",
                "tema_final": ""  # Para ser completado por consenso
            })

    desacuerdos_df = pd.DataFrame(desacuerdos)
    desacuerdos_path = args.clave.parent / "desacuerdos_para_resolver.csv"
    if desacuerdos_path.exists():
        existing_cons = pd.read_csv(desacuerdos_path, encoding="utf-8-sig")
        if "tema_final" in existing_cons and (existing_cons["tema_final"].fillna("").astype(str).str.strip() != "").any():
            print(f"Archivo existente de desacuerdos con tema_final detectado: {desacuerdos_path.name} (se conserva sin sobrescribir).")
        else:
            desacuerdos_df.to_csv(desacuerdos_path, index=False, encoding="utf-8-sig")
            print(f"Desacuerdos exportados ({len(desacuerdos_df)} filas) a: {desacuerdos_path.name}")
    else:
        desacuerdos_df.to_csv(desacuerdos_path, index=False, encoding="utf-8-sig")
        print(f"Desacuerdos exportados ({len(desacuerdos_df)} filas) a: {desacuerdos_path.name}")

    # Paso 2: Solo si existe tema_final completo
    consenso_file = args.consenso or desacuerdos_path
    eval_metricas = False
    gold_final = []

    if consenso_file.exists():
        cons_df = pd.read_csv(consenso_file, encoding="utf-8-sig")
        if "tema_final" in cons_df and not cons_df["tema_final"].fillna("").eq("").any():
            # Crear mapa de consensos
            cons_dict = dict(zip(cons_df["id_fila"], cons_df["tema_final"]))
            for i in range(n_rows):
                row_id = i + 1
                if row_id in cons_dict:
                    gold_final.append(cons_dict[row_id])
                else:
                    gold_final.append(theme_a.iloc[i])
            eval_metricas = True
            print("Archivo de consenso completo detectado. Calculando métricas formales...")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "theme_rules_sha256": rules_sha,
        "n_sample": n_rows,
        "inter_annotator_agreement": {
            "all_rows": {"n": n_rows, "po": po_all, "kappa": kappa_all},
            "excluding_ambiguous": {"n": len(theme_a_noamb), "po": po_noamb, "kappa": kappa_noamb}
        },
        "ambiguous_count": total_ambiguos,
        "needs_context_count": total_necesita_ctx,
        "disagreements_count": len(desacuerdos),
        "evaluation_against_rules": None
    }

    if eval_metricas:
        # Mapear y comparar contra reglas congeladas
        sample_eval = []
        for i in range(n_rows):
            cid = df_clave.loc[i, "comment_id"]
            plat = df_clave.loc[i, "plataforma"]
            h_label = gold_final[i]
            if h_label == "Ambiguo":
                continue  # Se excluye de las métricas pero se cuenta
            rule_label = scores_dict.get(cid, "Otros temas no identificados")
            target_rule = HUMAN_TO_RULE_MAP.get(h_label, "Otros temas no identificados")
            sample_eval.append({
                "comment_id": cid,
                "platform": plat,
                "human_theme": h_label,
                "target_rule": target_rule,
                "assigned_rule": rule_label,
                "weight": POPULATION_N[plat] / 66.0
            })

        ev_df = pd.DataFrame(sample_eval)
        n_eval = len(ev_df)

        categories = [
            "Protesta y movilización",
            "Programas de acceso y bienestar",
            "Admisiones, inscripciones y matrículas",
            "Información, trámites y certificados",
            "Oferta académica e investigación",
            "Infraestructura, sedes y tecnología",
            "Eventos, cultura y actividades institucionales",
            "Felicitaciones y expresiones de aprecio",
            "Otros temas no identificados",
            "Sin contenido temático suficiente (social/emoji/mención)"
        ]

        # Métricas por categoría
        cat_metrics = {}
        for cat in categories:
            tp_unw = ((ev_df["target_rule"] == cat) & (ev_df["assigned_rule"] == cat)).sum()
            fp_unw = ((ev_df["target_rule"] != cat) & (ev_df["assigned_rule"] == cat)).sum()
            fn_unw = ((ev_df["target_rule"] == cat) & (ev_df["assigned_rule"] != cat)).sum()
            support_unw = int((ev_df["target_rule"] == cat).sum())

            # Ponderados
            tp_w = ev_df.loc[(ev_df["target_rule"] == cat) & (ev_df["assigned_rule"] == cat), "weight"].sum()
            fp_w = ev_df.loc[(ev_df["target_rule"] != cat) & (ev_df["assigned_rule"] == cat), "weight"].sum()
            fn_w = ev_df.loc[(ev_df["target_rule"] == cat) & (ev_df["assigned_rule"] != cat), "weight"].sum()

            prec_unw = tp_unw / (tp_unw + fp_unw) if (tp_unw + fp_unw) > 0 else 0.0
            rec_unw = tp_unw / (tp_unw + fn_unw) if (tp_unw + fn_unw) > 0 else 0.0
            p_low, p_high = wilson_interval(tp_unw, tp_unw + fp_unw)
            r_low, r_high = wilson_interval(tp_unw, tp_unw + fn_unw)

            prec_w = tp_w / (tp_w + fp_w) if (tp_w + fp_w) > 0 else 0.0
            rec_w = tp_w / (tp_w + fn_w) if (tp_w + fn_w) > 0 else 0.0

            cat_metrics[cat] = {
                "support_unweighted": support_unw,
                "precision_unweighted": round(prec_unw, 4),
                "precision_ci95": [p_low, p_high] if support_unw >= 10 else "n<10: no interpretable",
                "recall_unweighted": round(rec_unw, 4),
                "recall_ci95": [r_low, r_high] if support_unw >= 10 else "n<10: no interpretable",
                "precision_weighted": round(prec_w, 4),
                "recall_weighted": round(rec_w, 4),
                "status": "interpretable" if support_unw >= 10 else "n<10: no interpretable"
            }

        # Matriz de confusión (sin ponderar y ponderada)
        conf_matrix_unw = {t: {p: 0 for p in categories} for t in categories}
        conf_matrix_w = {t: {p: 0.0 for p in categories} for t in categories}
        for _, row in ev_df.iterrows():
            t = row["target_rule"]
            p = row["assigned_rule"]
            w = row["weight"]
            if t in categories and p in categories:
                conf_matrix_unw[t][p] += 1
                conf_matrix_w[t][p] = round(conf_matrix_w[t][p] + w, 2)

        # Cobertura real (sin ponderar y ponderada)
        spec_human = ev_df[~ev_df["human_theme"].isin(["Otro tema identificable", "Sin contenido temático", "Ambiguo"])]
        left_in_other_unw = int((spec_human["assigned_rule"] == "Otros temas no identificados").sum())
        left_in_sin_unw = int((spec_human["assigned_rule"] == "Sin contenido temático suficiente (social/emoji/mención)").sum())
        spec_total_unw = len(spec_human)

        left_in_other_w = float(spec_human.loc[spec_human["assigned_rule"] == "Otros temas no identificados", "weight"].sum())
        left_in_sin_w = float(spec_human.loc[spec_human["assigned_rule"] == "Sin contenido temático suficiente (social/emoji/mención)", "weight"].sum())
        spec_total_w = float(spec_human["weight"].sum())

        report["evaluation_against_rules"] = {
            "n_evaluated": n_eval,
            "metrics_by_category": cat_metrics,
            "confusion_matrix_unweighted": conf_matrix_unw,
            "confusion_matrix_weighted": conf_matrix_w,
            "coverage_leakage": {
                "specific_human_cases_unweighted": spec_total_unw,
                "left_in_otros_unweighted": left_in_other_unw,
                "left_in_sin_contenido_unweighted": left_in_sin_unw,
                "pct_left_in_otros_unweighted": round(left_in_other_unw / spec_total_unw, 4) if spec_total_unw else 0.0,
                "pct_left_in_sin_contenido_unweighted": round(left_in_sin_unw / spec_total_unw, 4) if spec_total_unw else 0.0,
                "specific_human_cases_weighted": round(spec_total_w, 2),
                "left_in_otros_weighted": round(left_in_other_w, 2),
                "left_in_sin_contenido_weighted": round(left_in_sin_w, 2),
                "pct_left_in_otros_weighted": round(left_in_other_w / spec_total_w, 4) if spec_total_w else 0.0,
                "pct_left_in_sin_contenido_weighted": round(left_in_sin_w / spec_total_w, 4) if spec_total_w else 0.0
            }
        }

    # Guardar reporte JSON y Markdown (solo agregados, sin IDs ni textos)
    json_path = OUT_DIR / "evaluation_themes.json"
    md_path = OUT_DIR / "evaluation_themes.md"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Reporte de Evaluación Temática Formal (CRISP-DM Fase 5)",
        "",
        f"**Hash de Reglas Congeladas (SHA-256):** `{rules_sha}`",
        f"- **Muestra de Revisión:** {n_rows} comentarios estratificados (66 por plataforma).",
        f"- **Casos Marcados como Ambiguos:** {total_ambiguos}",
        f"- **Casos con Dependencia de Contexto (`necesita_contexto`):** {total_necesita_ctx}",
        f"- **Desacuerdos entre Anotadores:** {len(desacuerdos)} filas registradas en `desacuerdos_para_resolver.csv`.",
        "",
        "## 1. Acuerdo Inter-Anotador",
        f"- **Todas las filas (N={n_rows}):** Acuerdo Observado = {po_all:.1%}, Kappa de Cohen = {kappa_all:.3f}",
        f"- **Excluyendo casos ambiguos (N={len(theme_a_noamb)}):** Acuerdo Observado = {po_noamb:.1%}, Kappa de Cohen = {kappa_noamb:.3f}",
        ""
    ]

    if eval_metricas:
        md_lines.extend([
            "## 2. Comparación contra Reglas Léxicas (Consenso Humano)",
            f"- **Casos evaluados:** {report['evaluation_against_rules']['n_evaluated']}",
            "",
            "| Categoría | Soporte | Precisión (IC 95%) | Recall (IC 95%) | Precisión Pond. | Recall Pond. |",
            "|---|---:|---|---|---:|---:|"
        ])
        for cat, d in report["evaluation_against_rules"]["metrics_by_category"].items():
            if isinstance(d['precision_ci95'], (list, tuple)):
                p_ci = f"[{d['precision_ci95'][0]:.1%}, {d['precision_ci95'][1]:.1%}]"
            else:
                p_ci = d['precision_ci95']
            if isinstance(d['recall_ci95'], (list, tuple)):
                r_ci = f"[{d['recall_ci95'][0]:.1%}, {d['recall_ci95'][1]:.1%}]"
            else:
                r_ci = d['recall_ci95']
            md_lines.append(f"| {cat} | {d['support_unweighted']} | {d['precision_unweighted']:.1%} ({p_ci}) | {d['recall_unweighted']:.1%} ({r_ci}) | {d['precision_weighted']:.1%} | {d['recall_weighted']:.1%} |")

        cov = report["evaluation_against_rules"]["coverage_leakage"]
        md_lines.extend([
            "",
            "## 3. Cobertura Real y Fuga hacia Residuales",
            "- **Casos específicos etiquetados por humanos (sin ponderar):** " f"{cov['specific_human_cases_unweighted']}",
            f"  - Dejados en 'Otros temas no identificados': {cov['left_in_otros_unweighted']} ({cov['pct_left_in_otros_unweighted']:.1%})",
            f"  - Dejados en 'Sin contenido temático suficiente': {cov['left_in_sin_contenido_unweighted']} ({cov['pct_left_in_sin_contenido_unweighted']:.1%})",
            "- **Casos específicos etiquetados por humanos (ponderados por plataforma):** " f"{cov['specific_human_cases_weighted']}",
            f"  - Dejados en 'Otros temas no identificados': {cov['left_in_otros_weighted']} ({cov['pct_left_in_otros_weighted']:.1%})",
            f"  - Dejados en 'Sin contenido temático suficiente': {cov['left_in_sin_contenido_weighted']} ({cov['pct_left_in_sin_contenido_weighted']:.1%})",
            "",
            "## 4. Matriz de Confusión (Filas: Consenso Humano; Columnas: Reglas Léxicas)",
            "",
            "### A. Sin Ponderar (Conteos Muestrales)",
            ""
        ])

        # Tabla de matriz de confusión sin ponderar
        short_names = {
            "Protesta y movilización": "Protesta",
            "Programas de acceso y bienestar": "Bienestar",
            "Admisiones, inscripciones y matrículas": "Admisiones",
            "Información, trámites y certificados": "Trámites",
            "Oferta académica e investigación": "Oferta",
            "Infraestructura, sedes y tecnología": "Infraestr.",
            "Eventos, cultura y actividades institucionales": "Eventos",
            "Felicitaciones y expresiones de aprecio": "Felicit.",
            "Otros temas no identificados": "Otros",
            "Sin contenido temático suficiente (social/emoji/mención)": "SinContenido"
        }
        header_cols = [short_names.get(c, c) for c in categories]
        md_lines.append("| Humano \\ Regla | " + " | ".join(header_cols) + " | Total |")
        md_lines.append("|:---|" + "---:|" * len(categories) + "---:|")
        for r_cat in categories:
            r_label = short_names.get(r_cat, r_cat)
            row_vals = [str(conf_matrix_unw[r_cat][c_cat]) for c_cat in categories]
            r_tot = sum(conf_matrix_unw[r_cat][c_cat] for c_cat in categories)
            md_lines.append(f"| **{r_label}** | " + " | ".join(row_vals) + f" | **{r_tot}** |")
        pred_tot = [str(sum(conf_matrix_unw[r_cat][c_cat] for r_cat in categories)) for c_cat in categories]
        md_lines.append("| **Total Regla** | " + " | ".join(pred_tot) + f" | **{n_eval}** |")

        md_lines.extend([
            "",
            "### B. Ponderada por Plataforma (Estimación Poblacional N=15.885)",
            ""
        ])
        md_lines.append("| Humano \\ Regla | " + " | ".join(header_cols) + " | Total |")
        md_lines.append("|:---|" + "---:|" * len(categories) + "---:|")
        for r_cat in categories:
            r_label = short_names.get(r_cat, r_cat)
            row_vals = [f"{conf_matrix_w[r_cat][c_cat]:.1f}" for c_cat in categories]
            r_tot = sum(conf_matrix_w[r_cat][c_cat] for c_cat in categories)
            md_lines.append(f"| **{r_label}** | " + " | ".join(row_vals) + f" | **{r_tot:.1f}** |")
        pred_tot_w = [f"{sum(conf_matrix_w[r_cat][c_cat] for r_cat in categories):.1f}" for c_cat in categories]
        tot_w_all = sum(sum(conf_matrix_w[r_cat][c_cat] for r_cat in categories) for c_cat in categories)
        md_lines.append("| **Total Regla** | " + " | ".join(pred_tot_w) + f" | **{tot_w_all:.1f}** |")
    else:
        md_lines.extend([
            "## 2. Comparación contra Reglas Léxicas",
            "*Pendiente de resolución de consenso humano en `desacuerdos_para_resolver.csv` (columna `tema_final`).*"
        ])

    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    print(f"Reportes agregados generados en {json_path.name} y {md_path.name}")


if __name__ == "__main__":
    main()
