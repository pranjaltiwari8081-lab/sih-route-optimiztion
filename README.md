# 🚚 Farmer Direct Route Optimization API

An ML-powered route optimization backend for a **Farmer-to-Consumer marketplace**. The system helps reduce transportation costs and delivery time by selecting the best route between a farmer and consumer using **Google Maps Routes API + Machine Learning**.

---

## 🎯 Project Objective

The main objective is to reduce unnecessary intermediaries and transportation costs by enabling products to move directly from:

**👨‍🌾 Farmer → 🚚 Transportation → 🛒 Consumer**

The route optimization module evaluates different possible routes and selects the most efficient route based on:

* Road distance
* Google Maps travel time
* Traffic conditions
* Weather
* Vehicle type
* Quantity of products
* Fuel price
* Vehicle capacity
* Product perishability
* ML-predicted travel time
* ML-predicted delivery cost

---

## 🧠 How It Works

For a route such as:

```text
A → D
```

the system can compare multiple candidate routes:

```text
A → B → D
A → C → D
```

The ML models predict the expected travel time and delivery cost for each candidate.

The system then calculates a route score and selects the route with the lowest score.

```text
Farmer
   │
   ▼
Start A
   │
   ├────────► B ────────┐
   │                    │
   └────────► C ────────┤
                        ▼
                  Consumer D
                        │
                        ▼
                 Best Route
```

---

## 🏗️ Architecture

```text
                    ┌───────────────────┐
                    │    Frontend       │
                    │ Web / Mobile App  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │    FastAPI        │
                    │     Backend       │
                    └─────────┬─────────┘
                              │
                 ┌────────────┴────────────┐
                 │                         │
                 ▼                         ▼
       ┌───────────────────┐     ┌───────────────────┐
       │ Google Routes API  │     │   ML Models       │
       │ Distance / Time    │     │ Travel Time       │
       │ Traffic / Polyline │     │ Delivery Cost     │
       └─────────┬─────────┘     └─────────┬─────────┘
                 │                         │
                 └────────────┬────────────┘
                              ▼
                    ┌───────────────────┐
                    │ Route Optimizer   │
                    │ Score & Compare   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │    Best Route     │
                    └───────────────────┘
```

---

## 📁 Project Structure

```text
RouteOptimization/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── schemas.py
│   ├── google_routes.py
│   ├── model_service.py
│   └── route_optimizer.py
│
├── models/
│   ├── travel_time_model.joblib
│   └── delivery_cost_model.joblib
│
├── .env
├── .gitignore
├── requirements.txt
├── test_api.py
└── README.md
```

---

## 🤖 Machine Learning Models

Two Random Forest regression models are used.

### 1. Travel Time Prediction

Predicts the expected delivery/travel time.

**Target:**

```text
travel_time_min
```

### 2. Delivery Cost Prediction

Predicts the estimated transportation cost.

**Target:**

```text
delivery_cost_inr
```

### Model Features

```text
distance_km
quantity_kg
hour
day_of_week
traffic_level
weather
road_type
vehicle_type
fuel_price_inr_litre
vehicle_capacity_kg
perishability_score
```

The models are saved using `joblib`.

---

## 🗺️ Google Maps Integration

The project uses the **Google Routes API** to obtain real road-based routing information.

Google provides:

* Road distance
* Estimated travel duration
* Traffic-aware routing
* Encoded route polyline

The API key is stored securely in an environment variable.

```env
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_API_KEY
```

**Never commit `.env` or expose your Google API key publicly.**

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/pranjaltiwari8081-lab/sih-route-optimiztion.git
cd sih-route-optimiztion
```

### 2. Create virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Check Scikit-learn version

The models were trained using Scikit-learn `1.6.1`.

```bash
python -c "import sklearn; print(sklearn.__version__)"
```

Expected:

```text
1.6.1
```

---

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_API_KEY
```

The `.env` file should **not** be uploaded to GitHub.

---

## ▶️ Run Locally

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

### Swagger API Documentation

Open:

```text
http://127.0.0.1:8000/docs
```

### Health Check

```text
http://127.0.0.1:8000/health
```

---

## 🔌 API Endpoint

### Find Best Route

```http
POST /find-best-route
```

### Example Request

```json
{
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
```

---

## 📤 Example Response

```json
{
  "best_route": {
    "route": [
      "A",
      "B",
      "D"
    ],
    "distance_km": 42.5,
    "google_duration_min": 68.4,
    "ml_travel_time_min": 72.1,
    "ml_delivery_cost_inr": 1850.5,
    "score": 1.046
  },
  "alternatives": [
    {
      "route": [
        "A",
        "B",
        "D"
      ],
      "distance_km": 42.5,
      "google_duration_min": 68.4,
      "ml_travel_time_min": 72.1,
      "ml_delivery_cost_inr": 1850.5,
      "score": 1.046
    }
  ]
}
```

---

## 📊 Route Scoring

Each candidate route receives a score based on predicted travel time and delivery cost.

```text
Time Score = ML Travel Time / 60

Cost Score = ML Delivery Cost / 1000

Final Score =
    0.5 × Time Score
    +
    0.5 × Cost Score
```

The route with the **lowest score** is selected as the best route.

---

## 🧪 Testing

Start the API:

```bash
uvicorn app.main:app --reload
```

In another terminal:

```bash
python test_api.py
```

Expected output:

```text
Status: 200

Response:
{
    "best_route": ...
}
```

---

## 🚀 Deployment on Render

Create a **Web Service** on Render and connect the GitHub repository.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables

Add:

```text
GOOGLE_MAPS_API_KEY=YOUR_GOOGLE_API_KEY
PYTHON_VERSION=3.13.5
```

After deployment:

```text
https://YOUR-SERVICE-NAME.onrender.com
```

Swagger:

```text
https://YOUR-SERVICE-NAME.onrender.com/docs
```

Health check:

```text
https://YOUR-SERVICE-NAME.onrender.com/health
```

---

## 🔒 Security

* Google API key is stored using environment variables.
* `.env` is excluded from Git.
* API keys should be restricted in Google Cloud.
* Production CORS should be restricted to the frontend domain instead of allowing all origins.

---

## 📌 Future Improvements

* Real-time traffic updates
* Weather API integration
* Live GPS tracking
* Dynamic fuel prices
* More advanced route scoring
* Route polyline visualization
* Database integration
* Delivery notifications
* Farmer and consumer authentication
* Real agricultural transportation data
* Integration with the main marketplace application

---

## 👨‍💻 Project

**SIH – Farmer-to-Consumer Direct Marketplace**

### Core Idea

```text
Reduce Intermediaries
        ↓
Reduce Transportation Cost
        ↓
Optimize Delivery Route
        ↓
Faster & Cheaper Delivery
        ↓
Better Deal for Farmer & Consumer
```

---

## 📄 License

This project is developed as part of an SIH-style academic/project implementation.
