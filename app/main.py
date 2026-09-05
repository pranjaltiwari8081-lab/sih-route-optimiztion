from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import (
    RouteRequest,
    BestRouteResponse
)

from app.route_optimizer import (
    find_best_route
)


app = FastAPI(

    title=
        "Farmer Direct Route Optimization API",

    description=
        "Google Routes + ML based route optimization",

    version="1.0.0"
)


# ----------------------------------------
# CORS
# ----------------------------------------

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ----------------------------------------
# HOME
# ----------------------------------------

@app.get("/")
def home():

    return {

        "message":
            "Farmer Direct Route Optimization API",

        "status":
            "running",

        "version":
            "1.0.0"
    }


# ----------------------------------------
# HEALTH
# ----------------------------------------

@app.get("/health")
def health():

    return {

        "status":
            "healthy",

        "service":
            "route-optimization"
    }


# ----------------------------------------
# BEST ROUTE
# ----------------------------------------

@app.post(
    "/find-best-route",
    response_model=BestRouteResponse
)
def find_route(
    request: RouteRequest
):

    try:

        result = find_best_route(

            start=
                request.start.model_dump(),

            destination=
                request.destination.model_dump(),

            waypoints=[
                waypoint.model_dump()
                for waypoint
                in request.waypoints
            ],

            request=request
        )


        return result


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=str(e)
        )