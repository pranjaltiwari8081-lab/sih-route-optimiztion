from typing import List
from pydantic import BaseModel, Field


class Location(BaseModel):
    name: str
    latitude: float
    longitude: float


class RouteRequest(BaseModel):

    start: Location

    destination: Location

    waypoints: List[Location] = []

    quantity_kg: float = Field(
        ...,
        gt=0
    )

    vehicle_type: str = "Truck"

    traffic_level: str = "Medium"

    weather: str = "Clear"

    road_type: str = "Highway"

    hour: int = Field(
        10,
        ge=0,
        le=23
    )

    day_of_week: int = Field(
        1,
        ge=0,
        le=6
    )

    fuel_price_inr_litre: float = Field(
        95,
        gt=0
    )

    vehicle_capacity_kg: float = Field(
        1000,
        gt=0
    )

    perishability_score: float = Field(
        0.5,
        ge=0,
        le=1
    )


class RouteResult(BaseModel):

    route: List[str]

    distance_km: float

    google_duration_min: float

    ml_travel_time_min: float

    ml_delivery_cost_inr: float

    score: float

    polyline: str = ""
    
class BestRouteResponse(BaseModel):

    best_route: RouteResult

    alternatives: List[RouteResult]