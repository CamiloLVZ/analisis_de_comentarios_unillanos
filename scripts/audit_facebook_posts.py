
import json
from pathlib import Path
from collections import defaultdict

import pandas as pd


# Directorios
BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data" / "raw" / "facebook" / "posts"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "facebook"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

files = sorted(DATA_DIR.glob("*.json"))

if not files:
    raise FileNotFoundError(f"No se encontraron archivos JSON en {DATA_DIR}")

all_posts = []
file_summary = []

for file_path in files:
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Admite tanto listas como objetos que contengan items
    if isinstance(data, dict):
        data = data.get("items", [])

    posts = [
        item for item in data
        if item.get("type") == "post"
    ]

    all_posts.extend(posts)

    file_summary.append({
        "archivo": file_path.name,
        "publicaciones": len(posts)
    })


# Consolidar y detectar duplicados
df = pd.DataFrame(all_posts)

if df.empty:
    raise ValueError("No se encontraron publicaciones de tipo 'post'.")

df["id"] = df["id"].astype(str)
df["createdAt"] = pd.to_datetime(df["createdAt"], errors="coerce", utc=True)
df["comments"] = pd.to_numeric(df["comments"], errors="coerce").fillna(0)

total_raw = len(df)
duplicates = df.duplicated(subset=["id"]).sum()

# Conservar una sola aparición de cada publicación
df = df.drop_duplicates(subset=["id"], keep="first").copy()

df["year"] = df["createdAt"].dt.year

# Resumen por año
yearly = (
    df.groupby("year")
    .agg(
        publicaciones=("id", "count"),
        comentarios_reportados=("comments", "sum"),
        publicaciones_con_comentarios=(
            "comments", lambda x: (x > 0).sum()
        ),
        promedio_comentarios=("comments", "mean")
    )
    .reset_index()
)

# Resumen por archivo
file_summary = pd.DataFrame(file_summary)

print("\n========== AUDITORÍA FACEBOOK ==========")
print(f"Archivos procesados:             {len(files)}")
print(f"Registros originales:            {total_raw}")
print(f"Publicaciones duplicadas:        {duplicates}")
print(f"Publicaciones únicas:            {len(df)}")
print(f"Comentarios reportados:          {int(df['comments'].sum())}")
print(f"Fecha más antigua:               {df['createdAt'].min()}")
print(f"Fecha más reciente:              {df['createdAt'].max()}")

print("\n========== POR ARCHIVO ==========")
print(file_summary.to_string(index=False))

print("\n========== POR AÑO ==========")
print(yearly.to_string(index=False))

# Guardar resultados
yearly.to_csv(
    OUTPUT_DIR / "facebook_posts_yearly_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

file_summary.to_csv(
    OUTPUT_DIR / "facebook_posts_file_summary.csv",
    index=False,
    encoding="utf-8-sig"
)

print("\nResúmenes guardados en:", OUTPUT_DIR)
