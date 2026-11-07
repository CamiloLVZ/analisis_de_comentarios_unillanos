
import json
import pandas as pd
from pathlib import Path

# ==================================================
# CONFIGURACIÓN
# ==================================================

# Cambia esta ruta por la ubicación de tu archivo.
INPUT_FILE = Path("data/raw/instagram/posts/posts.json")

# Nombre de la columna que contiene el número de comentarios.
COMMENTS_COLUMN = "commentsCount"


# ==================================================
# CARGA DE DATOS
# ==================================================

if not INPUT_FILE.exists():
    raise FileNotFoundError(f"No se encontró el archivo: {INPUT_FILE}")

if INPUT_FILE.suffix.lower() == ".json":
    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Si el JSON contiene una lista de publicaciones.
    if isinstance(data, list):
        df = pd.DataFrame(data)

    # Si contiene un objeto con una lista dentro.
    elif isinstance(data, dict):
        # Ajusta esta sección si tu JSON tiene otra estructura.
        df = pd.DataFrame(data.get("data", data.get("posts", [])))

    else:
        raise ValueError("Estructura JSON no reconocida.")

elif INPUT_FILE.suffix.lower() == ".csv":
    df = pd.read_csv(INPUT_FILE)

else:
    raise ValueError("Formato no soportado. Usa JSON o CSV.")


# ==================================================
# VALIDACIÓN Y PREPARACIÓN
# ==================================================

if COMMENTS_COLUMN not in df.columns:
    raise ValueError(
        f"No existe la columna '{COMMENTS_COLUMN}'.\n"
        f"Columnas disponibles: {list(df.columns)}"
    )

df[COMMENTS_COLUMN] = pd.to_numeric(
    df[COMMENTS_COLUMN],
    errors="coerce"
).fillna(0)

# ==================================================
# MÉTRICAS
# ==================================================

total_posts = len(df)

posts_without_comments = (df[COMMENTS_COLUMN] == 0).sum()
posts_with_comments = (df[COMMENTS_COLUMN] > 0).sum()

total_comments = df[COMMENTS_COLUMN].sum()

average_comments = (
    total_comments / total_posts if total_posts > 0 else 0
)

# Distribución por rangos
distribution = {
    "0 comentarios": (df[COMMENTS_COLUMN] == 0).sum(),
    "1-5 comentarios": df[COMMENTS_COLUMN].between(1, 5).sum(),
    "6-10 comentarios": df[COMMENTS_COLUMN].between(6, 10).sum(),
    "11-20 comentarios": df[COMMENTS_COLUMN].between(11, 20).sum(),
    "21-50 comentarios": df[COMMENTS_COLUMN].between(21, 50).sum(),
    "Más de 50 comentarios": (df[COMMENTS_COLUMN] > 50).sum()
}


# ==================================================
# RESULTADOS
# ==================================================

print("\n========== ANÁLISIS DE PUBLICACIONES ==========\n")

print(f"Total de publicaciones:          {total_posts}")
print(f"Publicaciones sin comentarios:  {posts_without_comments}")
print(f"Publicaciones con comentarios:  {posts_with_comments}")
print(f"Total de comentarios estimados: {int(total_comments)}")
print(f"Promedio por publicación:       {average_comments:.2f}")

print("\n========== DISTRIBUCIÓN ==========\n")

for category, count in distribution.items():
    percentage = count / total_posts * 100 if total_posts else 0
    print(f"{category:25} {count:5} ({percentage:.2f}%)")

print("\n==============================================")


# Guardar distribución en CSV
output_file = Path("data/processed/instagram_post_distribution.csv")

pd.DataFrame(
    [
        {
            "category": category,
            "posts": count,
            "percentage": round(count / total_posts * 100, 2)
            if total_posts else 0
        }
        for category, count in distribution.items()
    ]
).to_csv(output_file, index=False, encoding="utf-8-sig")

print(f"\nDistribución guardada en: {output_file}")
