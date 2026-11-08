import json
from pathlib import Path
from urllib.parse import urlparse
from math import ceil

# Ejecutar desde la raíz del proyecto.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

INPUT_FILES = {
    "facebook": PROJECT_ROOT / "data" / "processed" / "post_urls" / "facebook_post_urls_with_comments.json",
    "instagram": PROJECT_ROOT / "data" / "processed" / "post_urls" / "instagram_post_urls_with_comments.json",
}

OUTPUT_ROOT = PROJECT_ROOT / "data" / "processed" / "comment_batches"
BATCH_SIZE = 100

ALLOWED_HOSTS = {
    "facebook": {"facebook.com", "www.facebook.com", "m.facebook.com", "web.facebook.com"},
    "instagram": {"instagram.com", "www.instagram.com"},
}


def load_urls(platform: str, file_path: Path) -> list[str]:
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de entrada: {file_path}")

    with file_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(f"El archivo {file_path.name} no contiene un array JSON.")

    urls = []
    seen = set()
    invalid = 0

    for item in data:
        if not isinstance(item, str):
            invalid += 1
            continue

        url = item.strip()
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()

        if parsed.scheme not in {"http", "https"} or host not in ALLOWED_HOSTS[platform]:
            invalid += 1
            continue

        if url not in seen:
            seen.add(url)
            urls.append(url)

    if invalid:
        print(f"  Aviso: se omitieron {invalid} elementos inválidos o de otro dominio.")

    return urls


def write_batches(platform: str, urls: list[str]) -> None:
    output_dir = OUTPUT_ROOT / platform
    output_dir.mkdir(parents=True, exist_ok=True)

    # Elimina únicamente los TXT de lotes anteriores de esta plataforma,
    # para evitar que queden archivos obsoletos si ahora hay menos lotes.
    for old_file in output_dir.glob("batch_*.txt"):
        old_file.unlink()

    total_batches = ceil(len(urls) / BATCH_SIZE)

    for batch_index in range(total_batches):
        start = batch_index * BATCH_SIZE
        end = start + BATCH_SIZE
        batch_urls = urls[start:end]

        output_file = output_dir / f"batch_{batch_index + 1:03d}.txt"
        output_file.write_text("\n".join(batch_urls) + "\n", encoding="utf-8")

        print(
            f"  {output_file.relative_to(PROJECT_ROOT)}: "
            f"{len(batch_urls)} URLs"
        )

    print(f"  Total: {len(urls)} URLs en {total_batches} lotes.")


def main() -> None:
    print(f"Tamaño de lote: {BATCH_SIZE} URLs")
    print(f"Carpeta de salida: {OUTPUT_ROOT.relative_to(PROJECT_ROOT)}\n")

    for platform, input_file in INPUT_FILES.items():
        print(f"[{platform.upper()}]")
        urls = load_urls(platform, input_file)
        write_batches(platform, urls)
        print()

    print("Proceso terminado. Los archivos JSON originales no fueron modificados.")


if __name__ == "__main__":
    main()
