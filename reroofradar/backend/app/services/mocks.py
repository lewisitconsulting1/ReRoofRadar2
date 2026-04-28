from __future__ import annotations

import hashlib
import math
import random
from datetime import datetime, timedelta
from typing import Any

from app.services.protocols import GeocodingService, PropertyService, WeatherService


ZIP_CENTER_DATA: dict[str, tuple[float, float, str, str]] = {
    "75201": (-96.7970, 32.7877, "TX", "Dallas"),
    "77001": (-95.3633, 29.7589, "TX", "Houston"),
    "30303": (-84.3880, 33.7490, "GA", "Atlanta"),
    "33101": (-80.1918, 25.7743, "FL", "Miami"),
    "90210": (-118.4065, 34.0901, "CA", "Beverly Hills"),
    "10001": (-73.9967, 40.7505, "NY", "New York"),
    "80202": (-104.9903, 39.7525, "CO", "Denver"),
    "60601": (-87.6298, 41.8781, "IL", "Chicago"),
    "73301": (-97.7431, 30.2672, "TX", "Austin"),
    "78201": (-98.4936, 29.4241, "TX", "San Antonio"),
    "63101": (-90.1994, 38.6270, "MO", "St. Louis"),
    "37201": (-86.7816, 36.1627, "TN", "Nashville"),
    "28202": (-80.8431, 35.2271, "NC", "Charlotte"),
    "85001": (-112.0740, 33.4484, "AZ", "Phoenix"),
    "74101": (-95.9928, 36.1540, "OK", "Tulsa"),
    "67201": (-97.3301, 37.6872, "KS", "Wichita"),
    "80301": (-105.2705, 40.0150, "CO", "Boulder"),
    "76101": (-97.3307, 32.7555, "TX", "Fort Worth"),
    "66201": (-94.6708, 38.9717, "KS", "Overland Park"),
    "53201": (-87.9065, 43.0389, "WI", "Milwaukee"),
}

STREET_NAMES = [
    "Oak", "Maple", "Cedar", "Elm", "Pine", "Washington", "Lake", "Hill",
    "Park", "Main", "Sunset", "Ridge", "Valley", "Meadow", "Birch", "Willow",
    "Spring", "Forest", "Highland", "Creek", "Brook", "Stone", "Timber",
    "Sycamore", "Chestnut", "Walnut", "Hickory", "Ash", "Poplar", "Magnolia",
    "Dogwood", "Azalea", "Ivy", "Rosewood", "Juniper", "Cypress", "Sequoia",
    "Redwood", "Palm", "Acacia",
]
STREET_TYPES = ["St", "Ave", "Blvd", "Dr", "Ln", "Ct", "Way", "Pl", "Rd", "Ter"]
FIRST_NAMES = [
    "James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael",
    "Linda", "David", "Elizabeth", "William", "Barbara", "Richard", "Susan",
    "Joseph", "Jessica", "Thomas", "Sarah", "Christopher", "Karen", "Charles",
    "Lisa", "Daniel", "Nancy", "Matthew", "Betty", "Anthony", "Margaret",
    "Mark", "Sandra", "Donald", "Ashley", "Steven", "Kimberly", "Paul",
    "Emily", "Andrew", "Donna", "Joshua", "Michelle", "Kenneth", "Carol",
    "Kevin", "Amanda", "Brian", "Dorothy", "George", "Melissa", "Timothy",
    "Deborah",
]
LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
    "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
    "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
    "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
    "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
    "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts",
]
EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "aol.com", "icloud.com", "hotmail.com"]
PHONE_AREA_CODES = [
    "214", "469", "972", "713", "281", "832", "404", "678", "770", "305",
    "786", "954", "312", "773", "872", "212", "646", "917", "303", "720",
    "602", "480", "623", "704", "980", "702", "725", "512", "830", "210",
    "918", "913", "316", "414", "262", "615", "629", "314", "636", "573",
    "513", "567", "614", "740", "407", "321", "904", "813",
]


def _hash_seed(*args: Any) -> int:
    key = "|".join(str(a) for a in args)
    return int(hashlib.md5(key.encode()).hexdigest(), 16)


def _seeded_rng(*args: Any) -> random.Random:
    return random.Random(_hash_seed(*args))


def _generate_polygon(
    center_lng: float, center_lat: float, radius_miles: float, seed: int
) -> list[tuple[float, float]]:
    rng = random.Random(seed)
    num_points = rng.randint(6, 10)
    radius_deg = radius_miles / 69.0
    angles = sorted([rng.uniform(0, 2 * math.pi) for _ in range(num_points)])
    polygon = []
    for angle in angles:
        r = radius_deg * rng.uniform(0.5, 1.0)
        lng = center_lng + r * math.cos(angle)
        lat = center_lat + r * math.sin(angle)
        polygon.append((round(lng, 6), round(lat, 6)))
    polygon.append(polygon[0])
    return polygon


class MockWeatherService(WeatherService):
    """Deterministic mock weather service returning realistic hail events."""

    async def get_hail_events(
        self,
        zip_code: str,
        radius_miles: float = 25.0,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
        min_severity: float = 0.75,
    ) -> list[dict[str, Any]]:
        now = datetime.now()
        if date_from is None:
            date_from = now - timedelta(days=730)
        if date_to is None:
            date_to = now

        base = _seeded_rng(zip_code)
        center_lng, center_lat, state, county = ZIP_CENTER_DATA.get(
            zip_code, (-96.7970, 32.7877, "TX", "Dallas County")
        )

        num_events = 5
        events = []
        for i in range(num_events):
            seed_val = _hash_seed(zip_code, "hail_event", i)
            rng = random.Random(seed_val)

            severity = round(rng.uniform(0.75, 3.0), 1)
            if severity < min_severity:
                severity = round(min_severity + rng.uniform(0, 1.5), 1)

            days_ago = rng.randint(0, int((date_to - date_from).days))
            event_date = date_to - timedelta(days=days_ago, hours=rng.randint(0, 23))

            event_center_lng = center_lng + rng.uniform(-radius_miles / 70, radius_miles / 70)
            event_center_lat = center_lat + rng.uniform(-radius_miles / 70, radius_miles / 70)

            polygon = _generate_polygon(
                event_center_lng, event_center_lat,
                rng.uniform(3, 12),
                seed_val,
            )

            centroid = (
                round(sum(p[0] for p in polygon[:-1]) / len(polygon[:-1]), 6),
                round(sum(p[1] for p in polygon[:-1]) / len(polygon[:-1]), 6),
            )

            event_id = f"mock-{zip_code}-{event_date.strftime('%Y%m%d')}-{i}"

            events.append({
                "id": event_id,
                "event_date": event_date,
                "severity": severity,
                "source": "mock",
                "source_event_id": event_id,
                "polygon": polygon,
                "centroid": centroid,
                "state": state,
                "county": county,
                "raw_payload": {
                    "mock": True,
                    "zip_code": zip_code,
                    "radius_miles": radius_miles,
                    "generated_at": now.isoformat(),
                },
            })

        events.sort(key=lambda e: e["severity"], reverse=True)
        return events


class MockPropertyService(PropertyService):
    """Deterministic mock property service returning ~50 properties per polygon."""

    async def get_properties_in_polygon(
        self,
        polygon_coords: list[tuple[float, float]],
        zip_code: str = "",
    ) -> list[dict[str, Any]]:
        polygon_key = "|".join(f"{c[0]:.4f},{c[1]:.4f}" for c in polygon_coords[:3])
        seed_val = _hash_seed(polygon_key, zip_code or "default")
        rng = random.Random(seed_val)

        min_lng = min(c[0] for c in polygon_coords)
        max_lng = max(c[0] for c in polygon_coords)
        min_lat = min(c[1] for c in polygon_coords)
        max_lat = max(c[1] for c in polygon_coords)

        num_properties = 50
        properties = []

        used_addresses: set[str] = set()

        for i in range(num_properties):
            prop_seed = _hash_seed(polygon_key, zip_code, i)
            prng = random.Random(prop_seed)

            lng = round(prng.uniform(min_lng, max_lng), 6)
            lat = round(prng.uniform(min_lat, max_lat), 6)

            house_num = prng.randint(100, 9999)
            street = prng.choice(STREET_NAMES)
            st_type = prng.choice(STREET_TYPES)
            address = f"{house_num} {street} {st_type}"

            if address in used_addresses:
                address = f"{house_num} {street} {st_type} {prng.choice(['N', 'S', 'E', 'W'])}"
            used_addresses.add(address)

            first = prng.choice(FIRST_NAMES)
            last = prng.choice(LAST_NAMES)
            owner_name = f"{first} {last}"

            domain = prng.choice(EMAIL_DOMAINS)
            owner_email = f"{first.lower()}.{last.lower()}{prng.randint(0, 99)}@{domain}"

            area = prng.choice(PHONE_AREA_CODES)
            phone = f"({area}) {prng.randint(200, 999)}-{prng.randint(1000, 9999)}"

            year_built = prng.randint(1950, 2023)
            last_roof_year = None
            if year_built < 2020 and prng.random() < 0.6:
                roof_age = prng.randint(3, 25)
                last_roof_year = max(year_built, 2023 - roof_age)
                if last_roof_year >= 2024:
                    last_roof_year = None

            property_value = round(prng.gauss(350000, 150000), 2)
            property_value = max(100000, min(property_value, 1500000))

            city = ZIP_CENTER_DATA.get(zip_code, (-96.7970, 32.7877, "Dallas", "TX"))[2]
            state = ZIP_CENTER_DATA.get(zip_code, (-96.7970, 32.7877, "Dallas", "TX"))[3]

            properties.append({
                "id": f"mock-prop-{zip_code}-{i:03d}",
                "address": address,
                "city": city,
                "state": state,
                "zip_code": zip_code or "75201",
                "latitude": lat,
                "longitude": lng,
                "owner_name": owner_name,
                "owner_email": owner_email,
                "owner_phone": phone,
                "year_built": year_built,
                "last_known_roof_year": last_roof_year,
                "property_value": property_value,
                "data_source": "mock",
            })

        return properties


class MockGeocodingService(GeocodingService):
    """Deterministic mock geocoding service with hardcoded ZIP bounding boxes."""

    FALLBACK_BBOX: dict[str, tuple[float, float, float, float]] = {
        "75201": (-96.8150, 32.7700, -96.7800, 32.8050),
        "77001": (-95.3800, 29.7400, -95.3450, 29.7750),
        "30303": (-84.4100, 33.7300, -84.3650, 33.7650),
        "33101": (-80.2100, 25.7600, -80.1700, 25.7900),
        "90210": (-118.4300, 34.0700, -118.3800, 34.1100),
        "10001": (-74.0050, 40.7400, -73.9850, 40.7600),
        "80202": (-105.0100, 39.7400, -104.9700, 39.7650),
        "60601": (-87.6400, 41.8700, -87.6200, 41.8900),
        "73301": (-97.7600, 30.2500, -97.7200, 30.2850),
        "78201": (-98.5200, 29.4050, -98.4700, 29.4400),
    }

    async def zip_to_bbox(self, zip_code: str) -> list[tuple[float, float]]:
        if zip_code in self.FALLBACK_BBOX:
            w, s, e, n = self.FALLBACK_BBOX[zip_code]
        else:
            rng = random.Random(_hash_seed("bbox", zip_code))
            center_lng = -96.8 + rng.uniform(-2, 2)
            center_lat = 32.8 + rng.uniform(-2, 2)
            delta = 0.02
            w, s, e, n = (
                round(center_lng - delta, 4),
                round(center_lat - delta, 4),
                round(center_lng + delta, 4),
                round(center_lat + delta, 4),
            )
        return [(w, s), (e, s), (e, n), (w, n), (w, s)]

    async def address_to_coords(
        self, address: str
    ) -> dict[str, Any] | None:
        seed_val = _hash_seed("addr", address)
        rng = random.Random(seed_val)
        return {
            "latitude": round(rng.uniform(25.0, 48.0), 6),
            "longitude": round(rng.uniform(-122.0, -70.0), 6),
            "formatted_address": address,
        }
