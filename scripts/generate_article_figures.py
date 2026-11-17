"""Generación de figuras científicas para el artículo en docs/articulo/.

Genera:
  - fig_temas_plataforma.pdf: Distribución porcentual de temas por plataforma
  - fig_confusion_temas.pdf: Matriz de confusión entre consenso humano y reglas léxicas
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

ROOT = Path.cwd()
OUT_DIR = ROOT / "docs/articulo"
OUT_DIR.mkdir(parents=True, exist_ok=True)

# Configuración de estilo editorial para IEEE
plt.rcParams.update({
    "font.family": "serif",
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "xtick.labelsize": 7.5,
    "ytick.labelsize": 7.5,
    "legend.fontsize": 7.5,
    "figure.titlesize": 10,
    "pdf.fonttype": 42,
    "ps.fonttype": 42
})

# -------------------------------------------------------------------------
# 1. FIGURA 1: fig_temas_plataforma.pdf
# -------------------------------------------------------------------------
df_counts = pd.read_csv(ROOT / "crisp_dm/04_modeling/outputs/theme_counts.csv")

totals = {"facebook": 11529, "instagram": 4126, "youtube": 230}
df_counts["total"] = df_counts["platform"].map(totals)
df_counts["pct"] = (df_counts["n"] / df_counts["total"]) * 100.0

theme_order = [
    "Protesta y movilización",
    "Programas de acceso y bienestar",
    "Admisiones, inscripciones y matrículas",
    "Información, trámites y certificados",
    "Oferta académica e investigación",
    "Infraestructura, sedes y tecnología",
    "Eventos, cultura y actividades institucionales",
    "Felicitaciones y expresiones de aprecio",
    "Sin contenido temático suficiente (social/emoji/mención)",
    "Otros temas no identificados"
]

short_theme_names = [
    "Protesta y movilización",
    "Acceso y bienestar",
    "Admisiones y matrículas",
    "Información y trámites",
    "Oferta acad. e investig.",
    "Infraestruc. y tecnología",
    "Eventos y cultura",
    "Felicitaciones y aprecio",
    "Sin contenido suficiente",
    "Otros temas (residual)"
]

piv = df_counts.pivot(index="theme", columns="platform", values="pct").reindex(theme_order).fillna(0)

fig, ax = plt.subplots(figsize=(3.45, 3.8), dpi=300)
y = np.arange(len(theme_order))
height = 0.26

colors = ["#1f77b4", "#e377c2", "#d62728"]  # Facebook (azul), Instagram (magenta/rosa), YouTube (rojo)
labels = ["Facebook (N=11.529)", "Instagram (N=4.126)", "YouTube (N=230)"]

rects_fb = ax.barh(y + height, piv["facebook"], height, label=labels[0], color="#2b5c8f", edgecolor="none")
rects_ig = ax.barh(y, piv["instagram"], height, label=labels[1], color="#d95f02", edgecolor="none")
rects_yt = ax.barh(y - height, piv["youtube"], height, label=labels[2], color="#7570b3", edgecolor="none")

ax.set_yticks(y)
ax.set_yticklabels(short_theme_names)
ax.invert_yaxis()  # Primer tema arriba
ax.set_xlabel("Proporción del volumen de la plataforma (%)")
ax.xaxis.set_major_formatter(ticker.PercentFormatter(xmax=100, decimals=0))
ax.set_xlim(0, 48)
ax.grid(axis="x", linestyle="--", alpha=0.5)
ax.set_axisbelow(True)
ax.legend(loc="lower right", frameon=True, framealpha=0.9, edgecolor="none", bbox_to_anchor=(1.0, 0.05))

plt.tight_layout()
fig_path_1 = OUT_DIR / "fig_temas_plataforma.pdf"
fig.savefig(fig_path_1, bbox_inches="tight")
plt.close(fig)
print(f"Generado: {fig_path_1.name}")

# -------------------------------------------------------------------------
# 2. FIGURA 2: fig_confusion_temas.pdf
# -------------------------------------------------------------------------
eval_json = json.loads((ROOT / "crisp_dm/05_evaluation/outputs/evaluation_themes.json").read_text(encoding="utf-8"))
cm_dict = eval_json["evaluation_against_rules"]["confusion_matrix_unweighted"]

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

short_matrix_names = [
    "Protesta",
    "Bienestar",
    "Admisiones",
    "Trámites",
    "Oferta",
    "Infraestr.",
    "Eventos",
    "Felicit.",
    "Otros",
    "SinCont."
]

matrix_data = np.zeros((len(categories), len(categories)), dtype=int)
for i, r_cat in enumerate(categories):
    for j, c_cat in enumerate(categories):
        matrix_data[i, j] = cm_dict[r_cat][c_cat]

fig, ax = plt.subplots(figsize=(3.45, 3.45), dpi=300)
im = ax.imshow(matrix_data, cmap="Blues", interpolation="nearest")

ax.set_xticks(np.arange(len(categories)))
ax.set_yticks(np.arange(len(categories)))
ax.set_xticklabels(short_matrix_names, rotation=45, ha="right", rotation_mode="anchor")
ax.set_yticklabels(short_matrix_names)

# Anotaciones numéricas en cada celda
thresh = matrix_data.max() / 2.0
for i in range(len(categories)):
    for j in range(len(categories)):
        val = matrix_data[i, j]
        if val > 0:
            color = "white" if val > thresh else "black"
            fontweight = "bold" if i == j else "normal"
            ax.text(j, i, f"{val}", ha="center", va="center", color=color, fontsize=7, fontweight=fontweight)

ax.set_xlabel("Asignación por Reglas Léxicas")
ax.set_ylabel("Consenso Humano Independiente")
ax.tick_params(top=False, bottom=True, left=True, right=False)

cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
cbar.ax.tick_params(labelsize=7)

plt.tight_layout()
fig_path_2 = OUT_DIR / "fig_confusion_temas.pdf"
fig.savefig(fig_path_2, bbox_inches="tight")
plt.close(fig)
print(f"Generado: {fig_path_2.name}")
