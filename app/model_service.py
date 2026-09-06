import os

import joblib
import numpy as np
import pandas as pd


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

TIME_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "travel_time_model.joblib"
)

COST_MODEL_PATH = os.path.join(
    MODEL_DIR,
    "delivery_cost_model.joblib"
)


time_model = None
cost_model = None


FEATURES = [
    "distance_km",
    "quantity_kg",
    "hour",
    "traffic_level",
    "weather",
    "vehicle_type"
]


def load_models():

    global time_model
    global cost_model

    if not os.path.exists(TIME_MODEL_PATH):
        raise FileNotFoundError(
            f"Missing model: {TIME_MODEL_PATH}"
        )

    if not os.path.exists(COST_MODEL_PATH):
        raise FileNotFoundError(
            f"Missing model: {COST_MODEL_PATH}"
        )

    time_model = joblib.load(
        TIME_MODEL_PATH
    )

    cost_model = joblib.load(
        COST_MODEL_PATH
    )


def predict_route_metrics(
    distance_km,
    quantity_kg,
    hour,
    traffic_level,
    weather,
    vehicle_type
):

    if time_model is None or cost_model is None:
        load_models()

    # Validate numeric inputs
    if not np.isfinite(distance_km):
        raise ValueError(
            "distance_km must be finite"
        )

    if not np.isfinite(quantity_kg):
        raise ValueError(
            "quantity_kg must be finite"
        )

    if distance_km <= 0:
        raise ValueError(
            "distance_km must be positive"
        )

    if quantity_kg <= 0:
        raise ValueError(
            "quantity_kg must be positive"
        )

    # IMPORTANT:
    # Create a pandas DataFrame because the trained
    # sklearn pipeline uses named columns.
    row = pd.DataFrame([{
        "distance_km": float(distance_km),
        "quantity_kg": float(quantity_kg),
        "hour": int(hour),
        "traffic_level": str(traffic_level),
        "weather": str(weather),
        "vehicle_type": str(vehicle_type)
    }], columns=FEATURES)

    # ML travel-time prediction
    travel_time = float(
        time_model.predict(row)[0]
    )

    # ML delivery-cost prediction
    delivery_cost = float(
        cost_model.predict(row)[0]
    )

    # Validate predictions
    if not np.isfinite(travel_time):
        raise ValueError(
            "Invalid travel time prediction"
        )

    if not np.isfinite(delivery_cost):
        raise ValueError(
            "Invalid delivery cost prediction"
        )

    if travel_time <= 0:
        raise ValueError(
            "Travel time prediction must be positive"
        )

    if delivery_cost <= 0:
        raise ValueError(
            "Delivery cost prediction must be positive"
        )

    return {
        "travel_time_min": travel_time,
        "delivery_cost_inr": delivery_cost
    }