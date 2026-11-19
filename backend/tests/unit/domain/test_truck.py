import pytest
from backend.app.core.domain.truck import Truck
from datetime import datetime

def test_truck_creation_minimal():
    t = Truck(
        id="truck-1",
        owner_id="user-1",
        vehicle_class="class-A",
        body_type="box",
        max_payload_kg=10000.0,
        location_lat=12.9716,
        location_lng=77.5946,
    )
    assert t.id == "truck-1"
    assert t.available_payload_kg is None

def test_truck_zero_payload_invalid():
    with pytest.raises(ValueError):
        Truck(
            id="truck-2",
            owner_id="user-2",
            vehicle_class="class-B",
            body_type="flatbed",
            max_payload_kg=15000.0,
            available_payload_kg=0,
            location_lat=12.0,
            location_lng=77.0,
        )
