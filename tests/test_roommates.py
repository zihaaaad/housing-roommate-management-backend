from datetime import datetime, timedelta, timezone
from fastapi import status
from fastapi.testclient import TestClient
from app.models.user import User


def test_roommate_matches_scoring(client: TestClient, seeker_auth_headers: dict, candidate_seeker_user: User):
    response = client.get("/api/v1/roommates/matches", headers=seeker_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    matches = json_data["data"]
    assert len(matches) > 0
    first_match = matches[0]
    assert "compatibility" in first_match
    assert first_match["compatibility"]["overall_score"] > 80.0
    assert first_match["compatibility"]["cleanliness_score"] == 100.0


def test_roommate_request_lifecycle(
    client: TestClient,
    seeker_auth_headers: dict,
    candidate_seeker_user: User,
    seeker_user: User
):
    candidate_token_response = client.post("/api/v1/auth/login", json={
        "username_or_email": "candidate_seeker@housing.com",
        "password": "Password@123"
    })
    candidate_headers = {"Authorization": f"Bearer {candidate_token_response.json()['data']['access_token']}"}

    send_payload = {
        "recipient_id": candidate_seeker_user.id,
        "message": "Hello! Would love to team up as roommates in Dhaka."
    }
    create_res = client.post("/api/v1/roommates/requests", json=send_payload, headers=seeker_auth_headers)
    assert create_res.status_code == status.HTTP_201_CREATED
    request_id = create_res.json()["data"]["id"]

    received_res = client.get("/api/v1/roommates/requests/received", headers=candidate_headers)
    assert received_res.status_code == status.HTTP_200_OK
    assert any(r["id"] == request_id for r in received_res.json()["data"])

    respond_payload = {
        "status": "ACCEPTED",
        "response_message": "Sounds fantastic, let us connect!"
    }
    update_res = client.put(f"/api/v1/roommates/requests/{request_id}", json=respond_payload, headers=candidate_headers)
    assert update_res.status_code == status.HTTP_200_OK
    assert update_res.json()["data"]["status"] == "ACCEPTED"


def test_property_viewing_inquiry_flow(
    client: TestClient,
    seeker_auth_headers: dict,
    landlord_auth_headers: dict
):
    props = client.get("/api/v1/properties").json()["data"]
    target_property_id = props[0]["id"]

    viewing_time = (datetime.now(timezone.utc) + timedelta(days=3)).isoformat()
    inquiry_payload = {
        "property_id": target_property_id,
        "scheduled_viewing_date": viewing_time,
        "notes": "Looking forward to inspecting the apartment."
    }
    inquiry_res = client.post("/api/v1/inquiries", json=inquiry_payload, headers=seeker_auth_headers)
    assert inquiry_res.status_code == status.HTTP_201_CREATED
    inquiry_id = inquiry_res.json()["data"]["id"]

    landlord_list = client.get("/api/v1/inquiries/landlord-inquiries", headers=landlord_auth_headers)
    assert landlord_list.status_code == status.HTTP_200_OK
    assert any(i["id"] == inquiry_id for i in landlord_list.json()["data"])

    confirm_payload = {
        "status": "CONFIRMED",
        "landlord_notes": "Viewing confirmed for selected date."
    }
    confirm_res = client.patch(f"/api/v1/inquiries/{inquiry_id}/status", json=confirm_payload, headers=landlord_auth_headers)
    assert confirm_res.status_code == status.HTTP_200_OK
    assert confirm_res.json()["data"]["status"] == "CONFIRMED"


def test_rental_application_and_approval_flow(
    client: TestClient,
    seeker_auth_headers: dict,
    landlord_auth_headers: dict
):
    props = client.get("/api/v1/properties").json()["data"]
    target_property_id = props[0]["id"]

    app_payload = {
        "property_id": target_property_id,
        "proposed_move_in_date": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat(),
        "lease_duration_months": 12,
        "monthly_income": 65000.0,
        "credit_score": 750,
        "employment_status": "Employed Full-time",
        "emergency_contact_name": "Family Member",
        "emergency_contact_phone": "+8801711998877"
    }
    apply_res = client.post("/api/v1/applications", json=app_payload, headers=seeker_auth_headers)
    assert apply_res.status_code == status.HTTP_201_CREATED
    application_id = apply_res.json()["data"]["id"]

    status_update_payload = {
        "status": "APPROVED",
        "landlord_decision_notes": "Application accepted after credit check."
    }
    approval_res = client.patch(
        f"/api/v1/applications/{application_id}/status",
        json=status_update_payload,
        headers=landlord_auth_headers
    )
    assert approval_res.status_code == status.HTTP_200_OK
    assert approval_res.json()["data"]["status"] == "APPROVED"


def test_internal_messaging_and_notifications(
    client: TestClient,
    seeker_auth_headers: dict,
    candidate_seeker_user: User
):
    message_payload = {
        "receiver_id": candidate_seeker_user.id,
        "content": "Hey there! Are you still searching for a roommate?"
    }
    send_msg_res = client.post("/api/v1/messages", json=message_payload, headers=seeker_auth_headers)
    assert send_msg_res.status_code == status.HTTP_201_CREATED

    candidate_token_response = client.post("/api/v1/auth/login", json={
        "username_or_email": "candidate_seeker@housing.com",
        "password": "Password@123"
    })
    candidate_headers = {"Authorization": f"Bearer {candidate_token_response.json()['data']['access_token']}"}

    notifications_res = client.get("/api/v1/notifications", headers=candidate_headers)
    assert notifications_res.status_code == status.HTTP_200_OK
    notifications = notifications_res.json()["data"]
    assert len(notifications) > 0
    notif_id = notifications[0]["id"]

    read_res = client.patch(f"/api/v1/notifications/{notif_id}/read", headers=candidate_headers)
    assert read_res.status_code == status.HTTP_200_OK
    assert read_res.json()["data"]["is_read"] is True
