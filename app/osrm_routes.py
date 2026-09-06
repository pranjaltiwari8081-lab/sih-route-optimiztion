import requests


OSRM_URL = (
    "https://router.project-osrm.org"
    "/route/v1/driving"
)


def get_route(
    coordinates
):

    if len(coordinates) < 2:
        raise ValueError(
            "At least two coordinates are required"
        )

    coordinate_string = ";".join(
        f"{lon},{lat}"
        for lat, lon in coordinates
    )

    url = (
        f"{OSRM_URL}/"
        f"{coordinate_string}"
    )

    params = {
        "overview": "full",
        "geometries": "polyline",
        "steps": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if data.get("code") != "Ok":
        raise RuntimeError(
            f"OSRM error: "
            f"{data.get('message', data.get('code'))}"
        )

    routes = data.get(
        "routes",
        []
    )

    if not routes:
        raise RuntimeError(
            "OSRM returned no routes"
        )

    route = routes[0]

    distance_km = (
        float(route["distance"])
        / 1000
    )

    duration_min = (
        float(route["duration"])
        / 60
    )

    if distance_km <= 0:
        raise RuntimeError(
            "Invalid route distance"
        )

    if duration_min <= 0:
        raise RuntimeError(
            "Invalid route duration"
        )

    return {
        "distance_km": distance_km,
        "duration_min": duration_min,
        "geometry": route.get(
            "geometry"
        )
    }