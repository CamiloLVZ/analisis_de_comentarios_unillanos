
import os
import json
import requests

from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm

# --------------------------------------------------
# CONFIGURACIÓN
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("YOUTUBE_API_KEY")

BASE_URL = "https://www.googleapis.com/youtube/v3"

VIDEOS_FILE = PROJECT_ROOT / "data" / "raw" / "youtube" / "videos" / "videos.json"
OUTPUT_DIR = PROJECT_ROOT / "data" / "raw" / "youtube" / "comments"

COMMENTS_FILE = OUTPUT_DIR / "comments.json"
RAW_FILE = OUTPUT_DIR / "comments_api_raw.json"

if not API_KEY:
    raise ValueError("No se encontró YOUTUBE_API_KEY en .env")

if not VIDEOS_FILE.exists():
    raise FileNotFoundError(f"No existe el archivo: {VIDEOS_FILE}")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

session = requests.Session()

# --------------------------------------------------
# FUNCIONES AUXILIARES
# --------------------------------------------------

def save_results(comments, raw_responses):
    """Guarda los resultados y las respuestas originales."""

    with open(COMMENTS_FILE, "w", encoding="utf-8") as file:
        json.dump(
            list(comments.values()),
            file,
            ensure_ascii=False,
            indent=2
        )

    with open(RAW_FILE, "w", encoding="utf-8") as file:
        json.dump(
            raw_responses,
            file,
            ensure_ascii=False,
            indent=2
        )


def api_request(endpoint, params):
    """Realiza una solicitud a YouTube Data API."""

    params["key"] = API_KEY

    response = session.get(
        f"{BASE_URL}/{endpoint}",
        params=params,
        timeout=30
    )

    if not response.ok:
        try:
            error_data = response.json()
            errors = error_data.get("error", {}).get("errors", [])
            reason = errors[0].get("reason") if errors else None
        except ValueError:
            reason = None

        if reason == "quotaExceeded":
            raise RuntimeError(
                "Se agotó la cuota diaria de YouTube API."
            )

        if reason == "commentsDisabled":
            raise RuntimeError(
                "COMMENTS_DISABLED"
            )

        raise RuntimeError(
            f"Error API {response.status_code}: {response.text}"
        )

    return response.json()


def normalize_comment(comment, video_id, is_reply):
    """Convierte un comentario de YouTube a nuestra estructura."""

    snippet = comment.get("snippet", {})

    return {
        "comment_id": comment.get("id"),
        "video_id": video_id,
        "parent_comment_id": (
            snippet.get("parentId") if is_reply else None
        ),
        "is_reply": is_reply,
        "author": snippet.get("authorDisplayName"),
        "text": (
            snippet.get("textOriginal")
            or snippet.get("textDisplay")
        ),
        "published_at": snippet.get("publishedAt"),
        "updated_at": snippet.get("updatedAt"),
        "like_count": snippet.get("likeCount", 0),
        "total_reply_count": (
            None if is_reply else snippet.get("totalReplyCount", 0)
        )
    }


# --------------------------------------------------
# OBTENER RESPUESTAS DE UN COMENTARIO
# --------------------------------------------------

def get_all_replies(parent_id, video_id, comments, raw_responses):

    next_page_token = None

    while True:
        params = {
            "part": "snippet",
            "parentId": parent_id,
            "maxResults": 100
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        data = api_request("comments", params)

        raw_responses.append({
            "video_id": video_id,
            "endpoint": "comments",
            "response": data
        })

        for reply in data.get("items", []):
            normalized = normalize_comment(
                reply,
                video_id,
                True
            )

            comments[normalized["comment_id"]] = normalized

        next_page_token = data.get("nextPageToken")

        if not next_page_token:
            break


# --------------------------------------------------
# OBTENER COMENTARIOS DE UN VIDEO
# --------------------------------------------------

def get_video_comments(video_id, comments, raw_responses):

    next_page_token = None

    while True:
        params = {
            "part": "snippet,replies",
            "videoId": video_id,
            "maxResults": 100
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        data = api_request("commentThreads", params)

        raw_responses.append({
            "video_id": video_id,
            "endpoint": "commentThreads",
            "response": data
        })

        for thread in data.get("items", []):

            # Comentario principal
            top_comment = thread["snippet"]["topLevelComment"]

            normalized = normalize_comment(
                top_comment,
                video_id,
                False
            )

            comments[normalized["comment_id"]] = normalized

            # Respuestas que vienen incluidas en la respuesta
            embedded_replies = (
                thread.get("replies", {}).get("comments", [])
            )

            for reply in embedded_replies:
                normalized_reply = normalize_comment(
                    reply,
                    video_id,
                    True
                )

                comments[normalized_reply["comment_id"]] = (
                    normalized_reply
                )

            # Comprobar si faltan respuestas por recuperar
            total_replies = thread["snippet"].get(
                "totalReplyCount", 0
            )

            if total_replies > len(embedded_replies):
                get_all_replies(
                    top_comment["id"],
                    video_id,
                    comments,
                    raw_responses
                )

        next_page_token = data.get("nextPageToken")

        if not next_page_token:
            break


# --------------------------------------------------
# EJECUCIÓN PRINCIPAL
# --------------------------------------------------

def main():

    with open(VIDEOS_FILE, "r", encoding="utf-8") as file:
        videos = json.load(file)

    comments = {}
    raw_responses = []

    videos_without_comments = 0
    videos_with_errors = 0

    print(f"Videos por procesar: {len(videos)}\n")

    try:
        for video in tqdm(videos, desc="Extrayendo comentarios"):

            video_id = video["video_id"]

            try:
                previous_count = len(comments)

                get_video_comments(
                    video_id,
                    comments,
                    raw_responses
                )

                if len(comments) == previous_count:
                    videos_without_comments += 1

            except RuntimeError as error:

                if str(error) == "COMMENTS_DISABLED":
                    videos_without_comments += 1
                    continue

                if "cuota diaria" in str(error):
                    raise

                videos_with_errors += 1
                print(f"\nError en video {video_id}: {error}")

            # Guardar progreso después de cada video
            save_results(comments, raw_responses)

    except RuntimeError as error:
        print(f"\nProceso interrumpido: {error}")

    finally:
        save_results(comments, raw_responses)

        print("\nPROCESO FINALIZADO")
        print("-------------------------")
        print("Videos procesados:", len(videos))
        print("Comentarios y respuestas:", len(comments))
        print("Videos sin comentarios o desactivados:",
              videos_without_comments)
        print("Videos con errores:", videos_with_errors)
        print("Archivo:", COMMENTS_FILE)
        print("Respuestas originales:", RAW_FILE)


if __name__ == "__main__":
    main()
