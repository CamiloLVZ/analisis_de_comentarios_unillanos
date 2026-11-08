
import os
import json
import requests

from pathlib import Path
from datetime import datetime, timezone
from dotenv import load_dotenv

# Configuración
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

API_KEY = os.getenv("YOUTUBE_API_KEY")

PLAYLIST_ID = "UUmhXbLrVeyotUiBsaPBcxcA"

START_DATE = datetime(2020, 1, 1, tzinfo=timezone.utc)
END_DATE = datetime(2026, 11, 2, 23, 59, 59, tzinfo=timezone.utc)

BASE_URL = "https://www.googleapis.com/youtube/v3/playlistItems"

if not API_KEY:
    raise ValueError("No se encontró YOUTUBE_API_KEY en .env")


def get_videos():
    videos = []
    raw_pages = []
    next_page_token = None
    page_number = 1
    stop_pagination = False

    print("Obteniendo publicaciones de Unillanos...\n")

    while True:
        params = {
            "part": "snippet,contentDetails",
            "playlistId": PLAYLIST_ID,
            "maxResults": 50,
            "key": API_KEY
        }

        if next_page_token:
            params["pageToken"] = next_page_token

        response = requests.get(
            BASE_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()
        data = response.json()

        raw_pages.append(data)

        items = data.get("items", [])

        print(f"Página {page_number}: {len(items)} videos")

        for item in items:
            snippet = item["snippet"]
            details = item.get("contentDetails", {})

            video_id = details.get("videoId")
            published_at = details.get("videoPublishedAt")

            if not video_id or not published_at:
                continue

            published_date = datetime.fromisoformat(
                published_at.replace("Z", "+00:00")
            )

            if published_date < START_DATE:
                stop_pagination = True
                continue

            if published_date <= END_DATE:
                videos.append({
                    "video_id": video_id,
                    "title": snippet.get("title"),
                    "description": snippet.get("description"),
                    "published_at": published_at,
                    "channel_title": snippet.get("channelTitle"),
                    "playlist_id": PLAYLIST_ID
                })

        if stop_pagination:
            break

        next_page_token = data.get("nextPageToken")

        if not next_page_token:
            break

        page_number += 1

    return videos, raw_pages


try:
    videos, raw_pages = get_videos()

    # Guardar respuestas originales de la API
    raw_dir = PROJECT_ROOT / "data" / "raw" / "youtube" / "videos"
    raw_dir.mkdir(parents=True, exist_ok=True)

    raw_file = raw_dir / "videos_api_raw.json"

    with open(raw_file, "w", encoding="utf-8") as file:
        json.dump(
            raw_pages,
            file,
            ensure_ascii=False,
            indent=2
        )

    # Guardar inventario de videos filtrados
    output_file = raw_dir / "videos.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(
            videos,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\nPROCESO COMPLETADO")
    print("-------------------------")
    print("Videos encontrados:", len(videos))
    print("Periodo:", START_DATE.date(), "a", END_DATE.date())
    print("Archivo:", output_file)

except requests.exceptions.HTTPError as error:
    print("Error HTTP:", error.response.status_code)
    print(error.response.text)

except requests.exceptions.RequestException as error:
    print("Error de conexión:", error)
