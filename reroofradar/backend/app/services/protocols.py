from __future__ import annotations

from typing import Any, Protocol, runtime_checkable
from datetime import datetime


@runtime_checkable
class WeatherService(Protocol):
    """Protocol for weather/hail data providers."""

    async def get_hail_events(
        self,
        zip_code: str,
        radius_miles: float = 25.0,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        min_severity: float = 0.75,
    ) -> list[dict[str, Any]]:
        """Return hail events for a ZIP code within a radius and date range.

        Each hail event dict contains:
            - id: str (unique identifier)
            - event_date: datetime
            - severity: float (hail size in inches)
            - source: str (e.g. "mock", "noaa")
            - source_event_id: str
            - polygon: list[tuple[float, float]] (lng/lat coords forming polygon)
            - centroid: tuple[float, float] (lng/lat)
            - state: str
            - county: str
        """
        ...


@runtime_checkable
class PropertyService(Protocol):
    """Protocol for property data providers."""

    async def get_properties_in_polygon(
        self,
        polygon_coords: list[tuple[float, float]],
        zip_code: str = "",
    ) -> list[dict[str, Any]]:
        """Return properties located within the given polygon.

        Each property dict contains:
            - id: str (unique identifier)
            - address: str
            - city: str
            - state: str
            - zip_code: str
            - latitude: float
            - longitude: float
            - owner_name: str
            - owner_email: str
            - owner_phone: str
            - year_built: int
            - last_known_roof_year: int | None
            - property_value: float
            - data_source: str
        """
        ...


@runtime_checkable
class GeocodingService(Protocol):
    """Protocol for geocoding providers."""

    async def zip_to_bbox(self, zip_code: str) -> list[tuple[float, float]]:
        """Return a bounding-box polygon (list of 5 lng/lat tuples) for a ZIP code."""
        ...

    async def address_to_coords(
        self, address: str
    ) -> dict[str, Any] | None:
        """Return latitude/longitude for a full address string."""
        ...
