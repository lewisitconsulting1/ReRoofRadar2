import pytest
from app.services.mocks import MockWeatherService, MockPropertyService, MockGeocodingService
from app.services.protocols import WeatherService, PropertyService, GeocodingService


@pytest.fixture
def weather_service():
    return MockWeatherService()


@pytest.fixture
def property_service():
    return MockPropertyService()


@pytest.fixture
def geocoding_service():
    return MockGeocodingService()


@pytest.mark.asyncio
class TestMockWeatherService:
    async def test_returns_5_events(self, weather_service):
        events = await weather_service.get_hail_events(zip_code="75201")
        assert len(events) == 5

    async def test_events_have_required_fields(self, weather_service):
        events = await weather_service.get_hail_events(zip_code="75201")
        required_fields = {
            "id", "event_date", "severity", "source", "source_event_id",
            "polygon", "centroid", "state", "county", "raw_payload",
        }
        for event in events:
            assert required_fields.issubset(event.keys())

    async def test_events_have_polygons(self, weather_service):
        events = await weather_service.get_hail_events(zip_code="75201")
        for event in events:
            assert len(event["polygon"]) >= 4
            assert event["polygon"][0] == event["polygon"][-1]
            for coord in event["polygon"]:
                assert len(coord) == 2

    async def test_events_have_centroids(self, weather_service):
        events = await weather_service.get_hail_events(zip_code="75201")
        for event in events:
            lng, lat = event["centroid"]
            assert -180 <= lng <= 180
            assert -90 <= lat <= 90

    async def test_severity_respects_min_severity(self, weather_service):
        events = await weather_service.get_hail_events(zip_code="75201", min_severity=2.0)
        for event in events:
            assert event["severity"] >= 2.0

    async def test_deterministic_output(self, weather_service):
        events1 = await weather_service.get_hail_events(zip_code="75201")
        events2 = await weather_service.get_hail_events(zip_code="75201")
        for e1, e2 in zip(events1, events2):
            assert e1["id"] == e2["id"]
            assert e1["severity"] == e2["severity"]
            assert e1["polygon"] == e2["polygon"]

    async def test_different_zip_different_events(self, weather_service):
        events_a = await weather_service.get_hail_events(zip_code="75201")
        events_b = await weather_service.get_hail_events(zip_code="30303")
        ids_a = {e["id"] for e in events_a}
        ids_b = {e["id"] for e in events_b}
        assert ids_a != ids_b

    async def test_source_is_mock(self, weather_service):
        events = await weather_service.get_hail_events(zip_code="75201")
        for event in events:
            assert event["source"] == "mock"

    async def test_sorted_by_severity_desc(self, weather_service):
        events = await weather_service.get_hail_events(zip_code="75201")
        severities = [e["severity"] for e in events]
        assert severities == sorted(severities, reverse=True)

    async def test_implements_protocol(self, weather_service):
        assert isinstance(weather_service, WeatherService)

    async def test_unknown_zip_returns_events(self, weather_service):
        events = await weather_service.get_hail_events(zip_code="00000")
        assert len(events) == 5


@pytest.mark.asyncio
class TestMockPropertyService:
    async def test_returns_50_properties(self, property_service, geocoding_service):
        bbox = await geocoding_service.zip_to_bbox("75201")
        properties = await property_service.get_properties_in_polygon(bbox, zip_code="75201")
        assert len(properties) == 50

    async def test_properties_have_required_fields(self, property_service, geocoding_service):
        bbox = await geocoding_service.zip_to_bbox("75201")
        properties = await property_service.get_properties_in_polygon(bbox, zip_code="75201")
        required_fields = {
            "id", "address", "city", "state", "zip_code", "latitude", "longitude",
            "owner_name", "owner_email", "owner_phone", "year_built",
            "last_known_roof_year", "property_value", "data_source",
        }
        for prop in properties:
            assert required_fields.issubset(prop.keys())

    async def test_properties_have_realistic_values(self, property_service, geocoding_service):
        bbox = await geocoding_service.zip_to_bbox("75201")
        properties = await property_service.get_properties_in_polygon(bbox, zip_code="75201")
        for prop in properties:
            assert prop["year_built"] >= 1950
            assert prop["year_built"] <= 2023
            assert prop["property_value"] >= 100000
            assert "@" in prop["owner_email"]
            assert "(" in prop["owner_phone"]

    async def test_deterministic_output(self, property_service, geocoding_service):
        bbox = await geocoding_service.zip_to_bbox("75201")
        props1 = await property_service.get_properties_in_polygon(bbox, zip_code="75201")
        props2 = await property_service.get_properties_in_polygon(bbox, zip_code="75201")
        for p1, p2 in zip(props1, props2):
            assert p1["id"] == p2["id"]
            assert p1["address"] == p2["address"]

    async def test_no_duplicate_addresses(self, property_service, geocoding_service):
        bbox = await geocoding_service.zip_to_bbox("75201")
        properties = await property_service.get_properties_in_polygon(bbox, zip_code="75201")
        addresses = [p["address"] for p in properties]
        assert len(addresses) == len(set(addresses))

    async def test_implements_protocol(self, property_service):
        assert isinstance(property_service, PropertyService)


@pytest.mark.asyncio
class TestMockGeocodingService:
    async def test_known_zip_bbox(self, geocoding_service):
        bbox = await geocoding_service.zip_to_bbox("75201")
        assert len(bbox) == 5
        assert bbox[0] == bbox[-1]

    async def test_unknown_zip_bbox(self, geocoding_service):
        bbox = await geocoding_service.zip_to_bbox("00000")
        assert len(bbox) == 5
        assert bbox[0] == bbox[-1]

    async def test_address_to_coords(self, geocoding_service):
        result = await geocoding_service.address_to_coords("123 Main St, Dallas, TX")
        assert "latitude" in result
        assert "longitude" in result
        assert -90 <= result["latitude"] <= 90
        assert -180 <= result["longitude"] <= 180

    async def test_all_fallback_zips(self, geocoding_service):
        for zip_code in MockGeocodingService.FALLBACK_BBOX:
            bbox = await geocoding_service.zip_to_bbox(zip_code)
            assert len(bbox) == 5

    async def test_implements_protocol(self, geocoding_service):
        assert isinstance(geocoding_service, GeocodingService)
