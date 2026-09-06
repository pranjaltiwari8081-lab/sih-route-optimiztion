from .location_service import resolve_location
from .osrm_routes import get_route
from .model_service import predict_route_metrics


def normalize(
    value,
    minimum,
    maximum
):

    if maximum == minimum:
        return 0.0

    return (
        value - minimum
    ) / (
        maximum - minimum
    )


def optimize_route(request):

    start = resolve_location(
        request.start
    )

    destination = resolve_location(
        request.destination
    )

    waypoints = []

    for waypoint in request.waypoints:

        resolved = resolve_location(
            waypoint
        )

        waypoints.append(
            resolved
        )

    candidates = []

    # Always compare direct route
    candidate_paths = [
        [start, destination]
    ]

    # Compare each waypoint route
    for waypoint in waypoints:

        candidate_paths.append([
            start,
            waypoint,
            destination
        ])

    for path in candidate_paths:

        coordinates = [
            (
                item[1],
                item[2]
            )
            for item in path
        ]

        route_data = get_route(
            coordinates
        )

        ml_data = predict_route_metrics(
            distance_km=route_data[
                "distance_km"
            ],
            quantity_kg=request.quantity_kg,
            hour=request.hour,
            traffic_level=request.traffic_level,
            weather=request.weather,
            vehicle_type=request.vehicle_type
        )

        # Combine real-road routing time
        # with ML prediction.
        effective_time = (
            0.75
            * route_data["duration_min"]
            +
            0.25
            * ml_data["travel_time_min"]
        )

        candidates.append({
            "path": [
                item[0]
                for item in path
            ],
            "distance_km": route_data[
                "distance_km"
            ],
            "routing_duration_min":
                route_data[
                    "duration_min"
                ],
            "ml_travel_time_min":
                ml_data[
                    "travel_time_min"
                ],
            "delivery_cost_inr":
                ml_data[
                    "delivery_cost_inr"
                ],
            "geometry":
                route_data[
                    "geometry"
                ],
            "effective_time_min":
                effective_time
        })

    if not candidates:
        raise RuntimeError(
            "No valid routes found"
        )

    min_time = min(
        x["effective_time_min"]
        for x in candidates
    )

    max_time = max(
        x["effective_time_min"]
        for x in candidates
    )

    min_cost = min(
        x["delivery_cost_inr"]
        for x in candidates
    )

    max_cost = max(
        x["delivery_cost_inr"]
        for x in candidates
    )

    for candidate in candidates:

        time_score = normalize(
            candidate[
                "effective_time_min"
            ],
            min_time,
            max_time
        )

        cost_score = normalize(
            candidate[
                "delivery_cost_inr"
            ],
            min_cost,
            max_cost
        )

        # 60% travel time
        # 40% delivery cost
        score = (
            0.60 * time_score
            +
            0.40 * cost_score
        )

        candidate["score"] = score

    candidates.sort(
        key=lambda x: (
            x["score"],
            x["distance_km"]
        )
    )

    best = candidates[0]

    return {
        "best_route": best,
        "alternatives": candidates,
        "route_count": len(candidates)
    }