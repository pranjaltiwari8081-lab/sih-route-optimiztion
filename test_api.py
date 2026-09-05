import requests


URL = (
    "http://127.0.0.1:8000/"
    "find-best-route"
)


data = {

    "start": {

        "name": "A",

        "latitude": 28.6139,

        "longitude": 77.2090
    },


    "destination": {

        "name": "D",

        "latitude": 28.4595,

        "longitude": 77.0266
    },


    "waypoints": [

        {

            "name": "B",

            "latitude": 28.5355,

            "longitude": 77.3910
        },

        {

            "name": "C",

            "latitude": 28.4089,

            "longitude": 77.3178
        }
    ],


    "quantity_kg": 500,

    "vehicle_type": "Truck",

    "traffic_level": "Medium",

    "weather": "Clear",

    "road_type": "Highway",

    "hour": 10,

    "day_of_week": 1,

    "fuel_price_inr_litre": 95,

    "vehicle_capacity_kg": 1000,

    "perishability_score": 0.7
}


response = requests.post(

    URL,

    json=data,

    timeout=60
)


print(
    "Status:",
    response.status_code
)


print("\nResponse:")

print(
    response.json()
)