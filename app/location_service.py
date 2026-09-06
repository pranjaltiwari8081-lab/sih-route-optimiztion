import os
from functools import lru_cache

import pandas as pd
import requests


BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

REAL_FILE = os.path.join(
    BASE_DIR,
    "data",
    "real_route_locations.csv"
)

SYNTHETIC_FILE = os.path.join(
    BASE_DIR,
    "data",
    "synthetic_route_locations.csv"
)


if os.path.exists(REAL_FILE):
    LOCATION_FILE = REAL_FILE
elif os.path.exists(SYNTHETIC_FILE):
    LOCATION_FILE = SYNTHETIC_FILE
else:
    LOCATION_FILE = None


if LOCATION_FILE:
    locations_df = pd.read_csv(
        LOCATION_FILE
    )
else:
    locations_df = pd.DataFrame()


session = requests.Session()

session.headers.update({
    "User-Agent": "SIH-RouteOptimization/1.0"
})


@lru_cache(maxsize=512)
def geocode_place(
    name: str
):
    """
    Convert a real place name into
    latitude and longitude using Nominatim.
    """

    params = {
        "q": name,
        "format": "json",
        "limit": 1,
        "countrycodes": "in"
    }

    try:
        response = session.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            return None

        return {
            "latitude": float(data[0]["lat"]),
            "longitude": float(data[0]["lon"])
        }

    except Exception as exc:
        raise RuntimeError(
            f"Unable to geocode location '{name}': {exc}"
        )


def resolve_location(location):
    """
    Resolve a Location object into real coordinates.
    """

    if (
        location.latitude is not None
        and
        location.longitude is not None
    ):
        return (
            location.name,
            float(location.latitude),
            float(location.longitude)
        )

    name = location.name.strip()

    # Try location catalog first
    if not locations_df.empty:

        search = name.lower()

        matches = locations_df[
            (
                locations_df["district"]
                .astype(str)
                .str.lower()
                == search
            )
            |
            (
                (
                    locations_df["district"]
                    .astype(str)
                    + ", "
                    +
                    locations_df["state"]
                    .astype(str)
                )
                .str.lower()
                == search
            )
        ]

        if not matches.empty:

            row = matches.iloc[0]

            # Only trust this file when it is the
            # real geocoded file.
            if os.path.abspath(
                LOCATION_FILE
            ) == os.path.abspath(
                REAL_FILE
            ):
                return (
                    name,
                    float(row["latitude"]),
                    float(row["longitude"])
                )

    # Otherwise geocode directly
    result = geocode_place(
        name
    )

    if result is None:
        raise ValueError(
            f"Location not found in India: {name}"
        )

    return (
        name,
        result["latitude"],
        result["longitude"]
    )


def search_locations(
    query: str = "",
    limit: int = 20
):

    if locations_df.empty:
        return []

    query = query.strip().lower()

    if query:
        mask = (
            locations_df["district"]
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                na=False
            )
            |
            locations_df["state"]
            .astype(str)
            .str.lower()
            .str.contains(
                query,
                na=False
            )
        )

        result = locations_df[
            mask
        ].head(limit)

    else:
        result = locations_df.head(
            limit
        )

    return [
        {
            "location_id": str(row["location_id"]),
            "district": str(row["district"]),
            "state": str(row["state"]),
            "name": (
                f"{row['district']}, "
                f"{row['state']}"
            )
        }
        for _, row in result.iterrows()
    ]