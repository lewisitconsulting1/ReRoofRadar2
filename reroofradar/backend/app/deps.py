from __future__ import annotations

from typing import Annotated

from fastapi import Depends

from app.core.config import settings
from app.services.mocks import MockGeocodingService, MockPropertyService, MockWeatherService
from app.services.protocols import GeocodingService, PropertyService, WeatherService

_weather_service: WeatherService = MockWeatherService()
_property_service: PropertyService = MockPropertyService()
_geocoding_service: GeocodingService = MockGeocodingService()


def _use_mocks() -> bool:
    return settings.mock_services or settings.app_env == "development"


async def get_weather_service() -> WeatherService:
    return _weather_service


async def get_property_service() -> PropertyService:
    return _property_service


async def get_geocoding_service() -> GeocodingService:
    return _geocoding_service


WeatherServiceDep = Annotated[WeatherService, Depends(get_weather_service)]
PropertyServiceDep = Annotated[PropertyService, Depends(get_property_service)]
GeocodingServiceDep = Annotated[GeocodingService, Depends(get_geocoding_service)]


def set_weather_service(service: WeatherService) -> None:
    global _weather_service
    _weather_service = service


def set_property_service(service: PropertyService) -> None:
    global _property_service
    _property_service = service


def set_geocoding_service(service: GeocodingService) -> None:
    global _geocoding_service
    _geocoding_service = service


def init_services() -> None:
    if not _use_mocks():
        try:
            from app.services.geocoding_service import RealMapboxGeocodingService
            set_geocoding_service(RealMapboxGeocodingService())
        except ImportError:
            pass
        try:
            from app.services.weather_service import NOAAWeatherService
            set_weather_service(NOAAWeatherService())
        except ImportError:
            pass


def init_services() -> None:
    if not _use_mocks():
        try:
            from app.services.geocoding_service import RealMapboxGeocodingService
            set_geocoding_service(RealMapboxGeocodingService())
        except ImportError:
            pass
        try:
            from app.services.weather_service import NOAAWeatherService
            set_weather_service(NOAAWeatherService())
        except ImportError:
            pass
