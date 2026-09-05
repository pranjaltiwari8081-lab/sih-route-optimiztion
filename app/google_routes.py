import os
import requests
from dotenv import load_dotenv


load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv(
    "GOOGLE_MAPS_API_KEY"
)

GOOGLE_ROUTES_URL = (
    "https://routes.googleapis.com/"
    "directions/v2:computeRoutes"
)


def get_google_route(
    origin,
    destination
):

    if not GOOGLE_MAPS_API_KEY:
        raise RuntimeError(
            "GOOGLE_MAPS_API_KEY is missing "
            "from .env"
        )

    headers = {
        "Content-Type": "application/json",

        "X-Goog-Api-Key":
            GOOGLE_MAPS_API_KEY,

        "X-Goog-FieldMask":
            "routes.distanceMeters,"
            "routes.duration,"
            "routes.polyline.encodedPolyline"
    }

    body = {

        "origin": {
            "location": {
                "latLng": {
                    "latitude":
                        origin["latitude"],

                    "longitude":
                        origin["longitude"]
                }
            }
        },

        "destination": {
            "location": {
                "latLng": {
                    "latitude":
                        destination["latitude"],

                    "longitude":
                        destination["longitude"]
                }
            }
        },

        "travelMode": "DRIVE",

        "routingPreference":
            "TRAFFIC_AWARE",

        "computeAlternativeRoutes": False
    }

    response = requests.post(
        GOOGLE_ROUTES_URL,
        headers=headers,
        json=body,
        timeout=30
    )

    if response.status_code != 200:

        raise RuntimeError(
            "Google Routes API failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    data = response.json()

    routes = data.get(
        "routes",
        []
    )

    if not routes:

        raise RuntimeError(
            "Google returned no route"
        )

    route = routes[0]

    distance_km = (
        route["distanceMeters"] / 1000
    )

    duration_seconds = float(
        route["duration"].replace("s", "")
    )

    duration_min = (
        duration_seconds / 60
    )

    polyline = (
        route["polyline"]
        ["encodedPolyline"]
    )

    return {
        "distance_km":
            round(distance_km, 2),

        "duration_min":
            round(duration_min, 2),

        "polyline":
            polyline
    }