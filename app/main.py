from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import RouteRequest
from app.model_service import load_models
from app.location_service import search_locations
from app.route_optimizer import optimize_route


# --------------------------------------------------
# Application Lifespan
# --------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load ML models once when the server starts
    load_models()

    print("[startup] ML models loaded successfully")

    yield


# --------------------------------------------------
# FastAPI Application
# --------------------------------------------------

app = FastAPI(
    title="SIH Route Optimization API",
    description=(
        "Farmer-to-consumer route optimization "
        "using OSRM/OpenStreetMap and Machine Learning"
    ),
    version="3.0.0",
    lifespan=lifespan
)


# --------------------------------------------------
# CORS
# --------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# --------------------------------------------------
# Root Endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "SIH Route Optimization API",
        "status": "running",
        "routing": "OSRM / OpenStreetMap",
        "google_billing": False
    }


# --------------------------------------------------
# Health Check
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "models": "loaded",
        "routing": "OSRM",
        "google_billing": False
    }


# --------------------------------------------------
# Search Locations
# --------------------------------------------------

@app.get("/locations")
def locations(
    query: str = "",
    limit: int = 20
):
    # Keep limit between 1 and 100
    limit = max(1, min(limit, 100))

    result = search_locations(
        query,
        limit
    )

    return {
        "count": len(result),
        "locations": result
    }


# --------------------------------------------------
# Find Best Route
# --------------------------------------------------

@app.post("/find-best-route")
def find_best_route(request: RouteRequest):

    # ------------------------------
    # Validate Traffic
    # ------------------------------

    allowed_traffic = {
        "Low",
        "Medium",
        "High"
    }

    if request.traffic_level not in allowed_traffic:
        raise HTTPException(
            status_code=422,
            detail="traffic_level must be Low, Medium or High"
        )

    # ------------------------------
    # Validate Weather
    # ------------------------------

    allowed_weather = {
        "Clear",
        "Cloudy",
        "Rain",
        "Hot"
    }

    if request.weather not in allowed_weather:
        raise HTTPException(
            status_code=422,
            detail="weather must be Clear, Cloudy, Rain or Hot"
        )

    # ------------------------------
    # Validate Vehicle
    # ------------------------------

    allowed_vehicle = {
        "Truck",
        "Mini_Truck",
        "Van"
    }

    if request.vehicle_type not in allowed_vehicle:
        raise HTTPException(
            status_code=422,
            detail="vehicle_type must be Truck, Mini_Truck or Van"
        )

    try:
        # Run complete route optimization
        result = optimize_route(request)

        # Extract only the best route
        best = result["best_route"]

        # Return clean response for frontend
        return {
            "best_route": " → ".join(best["path"]),
            "reason": "Lowest combined travel time and delivery cost",
            "estimated_cost_inr": round(
                best["delivery_cost_inr"],
                2
            ),
            "estimated_time_min": round(
                best["effective_time_min"],
                2
            )
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail=str(exc)
        )

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Route optimization failed: {exc}"
        )