from fastapi import status
from fastapi.testclient import TestClient


def test_create_property_as_landlord(client: TestClient, landlord_auth_headers: dict):
    payload = {
        "title": "Modern Sunny Flat in Dhanmondi",
        "description": "Lovely 2-bedroom apartment with generator and elevator.",
        "property_type": "APARTMENT",
        "address": "House 15, Road 27, Dhanmondi",
        "city": "Dhaka",
        "state": "Dhaka Division",
        "postal_code": "1209",
        "country": "Bangladesh",
        "total_bedrooms": 2,
        "total_bathrooms": 2,
        "furnished_status": "FURNISHED",
        "is_pet_friendly": True,
        "is_smoking_allowed": False,
        "parking_available": True,
        "amenities": "WIFI,GENERATOR_BACKUP,ELEVATOR",
        "base_monthly_rent": 22000.0,
        "security_deposit": 22000.0,
        "lease_duration_months": 12
    }
    response = client.post("/api/v1/properties", json=payload, headers=landlord_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["title"] == "Modern Sunny Flat in Dhanmondi"


def test_create_property_forbidden_for_seeker(client: TestClient, seeker_auth_headers: dict):
    payload = {
        "title": "Unauthorized Listing",
        "description": "Should fail creation.",
        "address": "House 1, Road 2, Dhanmondi",
        "city": "Dhaka",
        "base_monthly_rent": 15000.0
    }
    response = client.post("/api/v1/properties", json=payload, headers=seeker_auth_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_extended_property_listing_search_and_filter(client: TestClient):
    response = client.get("/api/v1/properties?city=Dhaka&min_rent=10000&max_rent=35000&sort_by=base_monthly_rent&sort_order=asc&page=1&limit=5")
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert "pagination" in json_data
    assert json_data["pagination"]["page"] == 1
    assert isinstance(json_data["data"], list)


def test_get_property_detail(client: TestClient, landlord_auth_headers: dict):
    list_response = client.get("/api/v1/properties")
    items = list_response.json()["data"]
    assert len(items) > 0
    property_id = items[0]["id"]

    detail_response = client.get(f"/api/v1/properties/{property_id}")
    assert detail_response.status_code == status.HTTP_200_OK
    assert detail_response.json()["data"]["id"] == property_id


def test_add_room_to_property(client: TestClient, landlord_auth_headers: dict):
    list_response = client.get("/api/v1/properties/my-listings", headers=landlord_auth_headers)
    property_id = list_response.json()["data"][0]["id"]

    room_payload = {
        "room_name": "Private Master Bedroom",
        "room_type": "MASTER_WITH_BATH",
        "monthly_rent": 1100.0,
        "security_deposit": 550.0,
        "is_available": True,
        "private_bathroom": True,
        "square_feet": 220
    }
    response = client.post(f"/api/v1/properties/{property_id}/rooms", json=room_payload, headers=landlord_auth_headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["data"]["room_name"] == "Private Master Bedroom"


def test_update_and_delete_property(client: TestClient, landlord_auth_headers: dict):
    create_payload = {
        "title": "Property To Delete",
        "description": "Short lived property listing for test.",
        "address": "15 CDA Avenue",
        "city": "Chittagong",
        "base_monthly_rent": 12000.0
    }
    created = client.post("/api/v1/properties", json=create_payload, headers=landlord_auth_headers)
    prop_id = created.json()["data"]["id"]

    update_payload = {"title": "Updated Property Title"}
    updated = client.put(f"/api/v1/properties/{prop_id}", json=update_payload, headers=landlord_auth_headers)
    assert updated.status_code == status.HTTP_200_OK
    assert updated.json()["data"]["title"] == "Updated Property Title"

    deleted = client.delete(f"/api/v1/properties/{prop_id}", headers=landlord_auth_headers)
    assert deleted.status_code == status.HTTP_200_OK

    re_check = client.get(f"/api/v1/properties/{prop_id}")
    assert re_check.status_code == status.HTTP_404_NOT_FOUND
