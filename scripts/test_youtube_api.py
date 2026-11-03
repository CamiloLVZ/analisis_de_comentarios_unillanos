
import os
import requests

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

if not API_KEY:
    raise ValueError("No se encontró YOUTUBE_API_KEY en el archivo .env")

BASE_URL = "https://www.googleapis.com/youtube/v3/channels"

params = {
    "part": "snippet,contentDetails",
    "forHandle": "@UnillanosTV",
    "key": API_KEY
}

try:
    response = requests.get(
        BASE_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if not data.get("items"):
        print("No se encontró el canal.")
    else:
        channel = data["items"][0]

        channel_id = channel["id"]
        channel_name = channel["snippet"]["title"]

        uploads_playlist = (
            channel["contentDetails"]
            ["relatedPlaylists"]["uploads"]
        )

        print("CONEXIÓN EXITOSA")
        print("-------------------------")
        print("Nombre:", channel_name)
        print("Channel ID:", channel_id)
        print("Uploads Playlist ID:", uploads_playlist)

except requests.exceptions.HTTPError:
    print("Error HTTP:", response.status_code)
    print(response.text)

except requests.exceptions.RequestException as error:
    print("Error de conexión:", error)
