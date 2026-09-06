import requests


URL = (
    "http://127.0.0.1:8000"
    "/find-best-route"
)


payload = {
    "start": {
        "name": "Gurgaon, Haryana"
    },

    "destination": {
        "name": "Faridabad, Haryana"
    },

    "waypoints": [
        {
            "name": "Sonipat, Haryana"
        },
        {
            "name": "Panipat, Haryana"
        }
    ],

    "quantity_kg": 500,

    "traffic_level": "Medium",

    "weather": "Clear",

    "vehicle_type": "Truck",

    "hour": 10
}


response = requests.post(
    URL,
    json=payload,
    timeout=120
)

print(
    "Status:",
    response.status_code
)

print(
    response.json()
)