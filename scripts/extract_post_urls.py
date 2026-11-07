
import json
from pathlib import Path


# ==================================================
# CONFIGURACIÓN
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[1]

SOURCES = {
    "facebook": BASE_DIR / "data" / "raw" / "facebook" / "posts",
    "instagram": BASE_DIR / "data" / "raw" / "instagram" / "posts",
}

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "post_urls"


# ==================================================
# FUNCIONES
# ==================================================

def load_posts(platform, directory):
    """Carga publicaciones desde los archivos JSON de una plataforma."""

    if not directory.exists():
        print(f"[AVISO] No existe el directorio: {directory}")
        return []

    posts = []

    for file_path in sorted(directory.glob("*.json")):

        # Evitar procesar archivos que no sean de publicaciones
        if "post" not in file_path.stem.lower():
            continue

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Admitir listas u objetos que contengan items
        if isinstance(data, dict):
            data = data.get("items", [])

        if not isinstance(data, list):
            print(f"[AVISO] Formato inesperado: {file_path.name}")
            continue

        valid_posts = [
            post for post in data
            if isinstance(post, dict)
            and post.get("type") == "post"
            and post.get("url")
        ]

        posts.extend(valid_posts)

        print(
            f"[{platform.upper()}] "
            f"{file_path.name}: {len(valid_posts)} publicaciones"
        )

    return posts


def extract_urls(posts):
    """Extrae URLs y elimina duplicados conservando el orden."""

    urls = []
    seen = set()

    for post in posts:
        url = post.get("url")

        if url and url not in seen:
            seen.add(url)
            urls.append(url)

    return urls


def save_json(data, path):
    """Guarda una lista como archivo JSON."""

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


# ==================================================
# PROCESAMIENTO
# ==================================================

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

for platform, directory in SOURCES.items():

    print(f"\n========== {platform.upper()} ==========")

    posts = load_posts(platform, directory)

    # Todos los posts
    all_urls = extract_urls(posts)

    # Solo publicaciones que reportan comentarios
    posts_with_comments = [
        post for post in posts
        if (post.get("comments") or 0) > 0
    ]

    comment_urls = extract_urls(posts_with_comments)

    # Guardar archivos
    save_json(
        all_urls,
        OUTPUT_DIR / f"{platform}_all_post_urls.json"
    )

    save_json(
        comment_urls,
        OUTPUT_DIR / f"{platform}_post_urls_with_comments.json"
    )

    print(f"\nPublicaciones encontradas: {len(posts)}")
    print(f"URLs únicas: {len(all_urls)}")
    print(f"URLs con comentarios: {len(comment_urls)}")
    print(f"URLs sin comentarios: {len(all_urls) - len(comment_urls)}")


print("\n========== PROCESO FINALIZADO ==========")
print(f"Archivos generados en: {OUTPUT_DIR}")
