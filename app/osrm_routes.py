import requests

OSRM_URL = "https://router.project-osrm.org/route/v1/driving"


def get_route(origin, destination):

    url = (
        f"{OSRM_URL}/"
        f"{origin['longitude']},{origin['latitude']};"
        f"{destination['longitude']},{destination['latitude']}"
    )

    params = {
        "overview": "full",
        "geometries": "polyline"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"OSRM routing failed: "
            f"{response.status_code} "
            f"{response.text}"
        )

    data = response.json()

    if data.get("code") != "Ok":
        raise RuntimeError(
            f"OSRM returned no route: {data}"
        )

    route = data["routes"][0]

    return {
        "distance_km": round(
            route["distance"] / 1000,
            2
        ),
        "duration_min": round(
            route["duration"] / 60,
            2
        ),
        "polyline": route.get(
            "geometry",
            ""
        )
    }