import os
import joblib
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


TRAVEL_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "travel_time_model.joblib"
)


COST_MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "delivery_cost_model.joblib"
)


if not os.path.exists(
    TRAVEL_MODEL_PATH
):
    raise FileNotFoundError(
        "Travel time model not found: "
        f"{TRAVEL_MODEL_PATH}"
    )


if not os.path.exists(
    COST_MODEL_PATH
):
    raise FileNotFoundError(
        "Delivery cost model not found: "
        f"{COST_MODEL_PATH}"
    )


print("Loading ML models...")

travel_time_model = joblib.load(
    TRAVEL_MODEL_PATH
)

delivery_cost_model = joblib.load(
    COST_MODEL_PATH
)

print("Travel time model loaded.")

print("Delivery cost model loaded.")


def predict_route_metrics(
    distance_km,
    quantity_kg,
    hour,
    day_of_week,
    traffic_level,
    weather,
    road_type,
    vehicle_type,
    fuel_price_inr_litre,
    vehicle_capacity_kg,
    perishability_score
):

    data = pd.DataFrame([{

        "distance_km":
            distance_km,

        "quantity_kg":
            quantity_kg,

        "hour":
            hour,

        "day_of_week":
            day_of_week,

        "traffic_level":
            traffic_level,

        "weather":
            weather,

        "road_type":
            road_type,

        "vehicle_type":
            vehicle_type,

        "fuel_price_inr_litre":
            fuel_price_inr_litre,

        "vehicle_capacity_kg":
            vehicle_capacity_kg,

        "perishability_score":
            perishability_score
    }])


    predicted_time = (
        travel_time_model
        .predict(data)[0]
    )


    predicted_cost = (
        delivery_cost_model
        .predict(data)[0]
    )


    return {

        "travel_time_min":
            round(
                float(predicted_time),
                2
            ),

        "delivery_cost_inr":
            round(
                float(predicted_cost),
                2
            )
    }