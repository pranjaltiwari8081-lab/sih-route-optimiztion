from app.google_routes import get_google_route
from app.model_service import predict_route_metrics


def calculate_candidate_route(
    start,
    waypoint,
    destination,
    request
):
    # ----------------------------------------
    # First leg: Start → Waypoint
    # ----------------------------------------

    first_leg = get_google_route(
        start,
        waypoint
    )

    # ----------------------------------------
    # Second leg: Waypoint → Destination
    # ----------------------------------------

    second_leg = get_google_route(
        waypoint,
        destination
    )

    # ----------------------------------------
    # Total distance
    # ----------------------------------------

    total_distance = (
        first_leg["distance_km"]
        + second_leg["distance_km"]
    )

    # ----------------------------------------
    # Routing travel time
    # ----------------------------------------

    routing_time = (
        first_leg["duration_min"]
        + second_leg["duration_min"]
    )

    # ----------------------------------------
    # ML prediction
    # ----------------------------------------

    ml_result = predict_route_metrics(

        distance_km=total_distance,

        quantity_kg=request.quantity_kg,

        hour=request.hour,

        day_of_week=request.day_of_week,

        traffic_level=request.traffic_level,

        weather=request.weather,

        road_type=request.road_type,

        vehicle_type=request.vehicle_type,

        fuel_price_inr_litre=
            request.fuel_price_inr_litre,

        vehicle_capacity_kg=
            request.vehicle_capacity_kg,

        perishability_score=
            request.perishability_score
    )

    ml_time = ml_result["travel_time_min"]

    ml_cost = ml_result["delivery_cost_inr"]

    # ----------------------------------------
    # Route score
    # ----------------------------------------
    #
    # Lower score = better route
    #
    # 50% ML travel time
    # 50% ML delivery cost
    # ----------------------------------------

    time_score = ml_time / 60

    cost_score = ml_cost / 1000

    score = (
        0.5 * time_score
        +
        0.5 * cost_score
    )

    return {

        "route": [
            start["name"],
            waypoint["name"],
            destination["name"]
        ],

        "distance_km":
            round(
                total_distance,
                2
            ),

        "google_duration_min":
            round(
                routing_time,
                2
            ),

        "ml_travel_time_min":
            ml_time,

        "ml_delivery_cost_inr":
            ml_cost,

        "score":
            round(
                score,
                4
            ),

        "polyline": [
            first_leg["polyline"],
            second_leg["polyline"]
        ]
    }


def find_best_route(
    start,
    destination,
    waypoints,
    request
):

    candidates = []

    # ----------------------------------------
    # If no waypoint is provided
    # ----------------------------------------

    if not waypoints:

        direct_route = get_google_route(
            start,
            destination
        )

        ml_result = predict_route_metrics(

            distance_km=
                direct_route["distance_km"],

            quantity_kg=
                request.quantity_kg,

            hour=
                request.hour,

            day_of_week=
                request.day_of_week,

            traffic_level=
                request.traffic_level,

            weather=
                request.weather,

            road_type=
                request.road_type,

            vehicle_type=
                request.vehicle_type,

            fuel_price_inr_litre=
                request.fuel_price_inr_litre,

            vehicle_capacity_kg=
                request.vehicle_capacity_kg,

            perishability_score=
                request.perishability_score
        )

        # ----------------------------------------
        # Calculate direct route score
        # ----------------------------------------

        ml_time = ml_result["travel_time_min"]

        ml_cost = ml_result["delivery_cost_inr"]

        time_score = ml_time / 60

        cost_score = ml_cost / 1000

        score = (
            0.5 * time_score
            +
            0.5 * cost_score
        )

        return {

            "best_route": {

                "route": [
                    start["name"],
                    destination["name"]
                ],

                "distance_km":
                    direct_route["distance_km"],

                "google_duration_min":
                    direct_route["duration_min"],

                "ml_travel_time_min":
                    ml_time,

                "ml_delivery_cost_inr":
                    ml_cost,

                "score":
                    round(
                        score,
                        4
                    ),

                "polyline":
                    direct_route["polyline"]
            },

            "alternatives": []
        }

    # ----------------------------------------
    # Calculate all waypoint routes
    # ----------------------------------------

    for waypoint in waypoints:

        result = calculate_candidate_route(

            start,
            waypoint,
            destination,
            request
        )

        candidates.append(result)

    # ----------------------------------------
    # Find route with minimum score
    # ----------------------------------------

    best_route = min(
        candidates,
        key=lambda x: x["score"]
    )

    # ----------------------------------------
    # Return best route + alternatives
    # ----------------------------------------

    return {

        "best_route":
            best_route,

        "alternatives":
            candidates
    }