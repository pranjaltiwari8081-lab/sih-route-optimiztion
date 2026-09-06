from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class Location(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=120
    )

    latitude: Optional[float] = None
    longitude: Optional[float] = None

    location_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_coordinates(self):
        if (
            (self.latitude is None)
            !=
            (self.longitude is None)
        ):
            raise ValueError(
                "latitude and longitude must be provided together"
            )

        return self


class RouteRequest(BaseModel):

    start: Location

    destination: Location

    waypoints: List[Location] = Field(
        default_factory=list,
        max_length=5
    )

    quantity_kg: float = Field(
        ...,
        gt=0
    )

    traffic_level: str = Field(
        default="Medium"
    )

    weather: str = Field(
        default="Clear"
    )

    vehicle_type: str = Field(
        default="Truck"
    )

    hour: int = Field(
        default=10,
        ge=0,
        le=23
    )