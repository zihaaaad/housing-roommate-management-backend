import json
from datetime import datetime, timedelta, timezone
from fastapi import status
from fastapi.testclient import TestClient
from app.models.user import User


def test_filter_min_rent_greater_than_max_rent_edge_case(client: TestClient):
    response = client.get("/api/v1/properties?min_rent=2500&max_rent=1000")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["error_code"] == "BAD_REQUEST"


def test_schedule_viewing_in_past_edge_case(
    client: TestClient,
    seeker_auth_headers: dict,
    landlord_auth_headers: dict
):
    create_payload = {
        "title": "Past Viewing Test Property",
        "description": "Property to test past viewing rejection.",
        "address": "100 Past St",
        "city": "Dhaka",
        "base_monthly_rent": 15000.0
    }
    prop_res = client.post("/api/v1/properties", json=create_payload, headers=landlord_auth_headers)
    target_property_id = prop_res.json()["data"]["id"]

    past_date = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    response = client.post(
        "/api/v1/inquiries",
        json={"property_id": target_property_id, "scheduled_viewing_date": past_date},
        headers=seeker_auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_landlord_cannot_schedule_viewing_for_own_property(
    client: TestClient,
    landlord_auth_headers: dict,
    landlord_user: User
):
    create_payload = {
        "title": "Owner Viewing Property",
        "description": "Property to test owner booking.",
        "address": "400 Test Ave",
        "city": "Dhaka",
        "base_monthly_rent": 18000.0
    }
    prop_res = client.post("/api/v1/properties", json=create_payload, headers=landlord_auth_headers)
    property_id = prop_res.json()["data"]["id"]

    future_date = (datetime.now(timezone.utc) + timedelta(days=5)).isoformat()
    book_res = client.post(
        "/api/v1/inquiries",
        json={"property_id": property_id, "scheduled_viewing_date": future_date},
        headers=landlord_auth_headers
    )
    assert book_res.status_code == status.HTTP_400_BAD_REQUEST


def test_landlord_cannot_apply_for_own_property(
    client: TestClient,
    landlord_auth_headers: dict,
    landlord_user: User
):
    create_payload = {
        "title": "Owner Lease Property",
        "description": "Property to test owner application.",
        "address": "450 Test Ave",
        "city": "Dhaka",
        "base_monthly_rent": 19000.0
    }
    prop_res = client.post("/api/v1/properties", json=create_payload, headers=landlord_auth_headers)
    property_id = prop_res.json()["data"]["id"]

    future_date = (datetime.now(timezone.utc) + timedelta(days=10)).isoformat()
    app_payload = {
        "property_id": property_id,
        "proposed_move_in_date": future_date,
        "lease_duration_months": 12,
        "monthly_income": 80000.0,
        "credit_score": 780,
        "employment_status": "Self Employed",
        "emergency_contact_name": "Contact Name",
        "emergency_contact_phone": "+8801819112233"
    }
    apply_res = client.post("/api/v1/applications", json=app_payload, headers=landlord_auth_headers)
    assert apply_res.status_code == status.HTTP_400_BAD_REQUEST


def test_empty_whitespace_message_edge_case(
    client: TestClient,
    seeker_auth_headers: dict,
    candidate_seeker_user: User
):
    response = client.post(
        "/api/v1/messages",
        json={"receiver_id": candidate_seeker_user.id, "content": "    "},
        headers=seeker_auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_case_insensitive_login_edge_case(client: TestClient, seeker_user: User):
    upper_email = seeker_user.email.upper()
    response = client.post("/api/v1/auth/login", json={
        "username_or_email": upper_email,
        "password": "Password@123"
    })
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["success"] is True


def test_update_user_basic_details_and_role(client: TestClient, seeker_auth_headers: dict, admin_auth_headers: dict, seeker_user: User):
    update_res = client.put(
        "/api/v1/users/me/basic",
        json={"full_name": "Updated Seeker Name", "phone_number": "+8801711999888"},
        headers=seeker_auth_headers
    )
    assert update_res.status_code == status.HTTP_200_OK
    assert update_res.json()["data"]["full_name"] == "Updated Seeker Name"

    role_res = client.patch(
        f"/api/v1/users/{seeker_user.id}/role",
        json={"role": "TENANT"},
        headers=admin_auth_headers
    )
    assert role_res.status_code == status.HTTP_200_OK
    assert role_res.json()["data"]["role"] == "TENANT"

    revert_role = client.patch(
        f"/api/v1/users/{seeker_user.id}/role",
        json={"role": "ROOMMATE_SEEKER"},
        headers=admin_auth_headers
    )
    assert revert_role.status_code == status.HTTP_200_OK


def test_delete_message_lifecycle(client: TestClient, seeker_auth_headers: dict, candidate_seeker_user: User):
    send_res = client.post(
        "/api/v1/messages",
        json={"receiver_id": candidate_seeker_user.id, "content": "Temporary message to delete."},
        headers=seeker_auth_headers
    )
    assert send_res.status_code == status.HTTP_201_CREATED
    msg_id = send_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/messages/{msg_id}", headers=seeker_auth_headers)
    assert del_res.status_code == status.HTTP_200_OK
    assert del_res.json()["success"] is True


def test_delete_notification_lifecycle(client: TestClient, candidate_seeker_user: User):
    token_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "candidate_seeker@housing.com",
        "password": "Password@123"
    })
    auth_headers = {"Authorization": f"Bearer {token_res.json()['data']['access_token']}"}

    notifs_res = client.get("/api/v1/notifications", headers=auth_headers)
    assert notifs_res.status_code == status.HTTP_200_OK
    notifs = notifs_res.json()["data"]
    if notifs:
        target_id = notifs[0]["id"]
        client.patch(f"/api/v1/notifications/{target_id}/read", headers=auth_headers)
        del_single = client.delete(f"/api/v1/notifications/{target_id}", headers=auth_headers)
        assert del_single.status_code == status.HTTP_200_OK

    clear_res = client.delete("/api/v1/notifications/clear-read", headers=auth_headers)
    assert clear_res.status_code == status.HTTP_200_OK


def test_delete_roommate_request_lifecycle(client: TestClient, seeker_auth_headers: dict, candidate_seeker_user: User):
    create_res = client.post(
        "/api/v1/roommates/requests",
        json={"recipient_id": candidate_seeker_user.id, "message": "Will be deleted immediately."},
        headers=seeker_auth_headers
    )
    assert create_res.status_code == status.HTTP_201_CREATED
    req_id = create_res.json()["data"]["id"]

    del_res = client.delete(f"/api/v1/roommates/requests/{req_id}", headers=seeker_auth_headers)
    assert del_res.status_code == status.HTTP_200_OK
    assert del_res.json()["success"] is True


def test_delete_inquiry_and_application_lifecycle(client: TestClient, seeker_auth_headers: dict, landlord_auth_headers: dict):
    props = client.get("/api/v1/properties").json()["data"]
    target_property_id = props[0]["id"]

    viewing_time = (datetime.now(timezone.utc) + timedelta(days=6)).isoformat()
    inquiry_res = client.post(
        "/api/v1/inquiries",
        json={"property_id": target_property_id, "scheduled_viewing_date": viewing_time, "notes": "Temporary"},
        headers=seeker_auth_headers
    )
    assert inquiry_res.status_code == status.HTTP_201_CREATED
    inquiry_id = inquiry_res.json()["data"]["id"]

    del_inquiry = client.delete(f"/api/v1/inquiries/{inquiry_id}", headers=seeker_auth_headers)
    assert del_inquiry.status_code == status.HTTP_200_OK

    app_res = client.post(
        "/api/v1/applications",
        json={
            "property_id": target_property_id,
            "proposed_move_in_date": (datetime.now(timezone.utc) + timedelta(days=25)).isoformat(),
            "lease_duration_months": 6,
            "monthly_income": 60000.0,
            "employment_status": "Contractor",
            "emergency_contact_name": "Emergency Contact",
            "emergency_contact_phone": "+8801711223344"
        },
        headers=seeker_auth_headers
    )
    assert app_res.status_code == status.HTTP_201_CREATED
    app_id = app_res.json()["data"]["id"]

    del_app = client.delete(f"/api/v1/applications/{app_id}", headers=seeker_auth_headers)
    assert del_app.status_code == status.HTTP_200_OK


def test_delete_user_account_lifecycle(client: TestClient, admin_auth_headers: dict):
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "user_to_delete@housing.com",
        "username": "user_to_delete",
        "password": "Password@123",
        "full_name": "Temporary User",
        "phone_number": "+8801711223399"
    })
    assert reg_res.status_code == status.HTTP_201_CREATED
    user_id = reg_res.json()["data"]["id"]

    login_res = client.post("/api/v1/auth/login", json={
        "username_or_email": "user_to_delete@housing.com",
        "password": "Password@123"
    })
    user_token = login_res.json()["data"]["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    del_own = client.delete("/api/v1/users/me", headers=user_headers)
    assert del_own.status_code == status.HTTP_200_OK

    re_check = client.get(f"/api/v1/users/{user_id}")
    assert re_check.status_code == status.HTTP_404_NOT_FOUND


def test_application_approval_rejects_competing_applications(
    client: TestClient,
    landlord_auth_headers: dict,
    seeker_auth_headers: dict
):
    create_payload = {
        "title": "Double Booking Test Property",
        "description": "Property to test auto-rejecting competing applications.",
        "address": "99 Competition Rd",
        "city": "Dhaka",
        "base_monthly_rent": 20000.0
    }
    prop_res = client.post("/api/v1/properties", json=create_payload, headers=landlord_auth_headers)
    property_id = prop_res.json()["data"]["id"]

    move_in = (datetime.now(timezone.utc) + timedelta(days=20)).isoformat()
    app1_res = client.post(
        "/api/v1/applications",
        json={
            "property_id": property_id,
            "proposed_move_in_date": move_in,
            "lease_duration_months": 12,
            "monthly_income": 80000.0,
            "employment_status": "Employed",
            "emergency_contact_name": "Contact 1",
            "emergency_contact_phone": "+8801700000001"
        },
        headers=seeker_auth_headers
    )
    app1_id = app1_res.json()["data"]["id"]

    reg_seeker2 = client.post("/api/v1/auth/register", json={
        "email": "seeker2_competition@housing.com",
        "username": "seeker2_competition",
        "password": "Password@123",
        "full_name": "Applicant Two",
        "phone_number": "+8801700000002"
    })
    login_seeker2 = client.post("/api/v1/auth/login", json={
        "username_or_email": "seeker2_competition@housing.com",
        "password": "Password@123"
    })
    seeker2_headers = {"Authorization": f"Bearer {login_seeker2.json()['data']['access_token']}"}

    app2_res = client.post(
        "/api/v1/applications",
        json={
            "property_id": property_id,
            "proposed_move_in_date": move_in,
            "lease_duration_months": 12,
            "monthly_income": 75000.0,
            "employment_status": "Employed",
            "emergency_contact_name": "Contact 2",
            "emergency_contact_phone": "+8801700000003"
        },
        headers=seeker2_headers
    )
    app2_id = app2_res.json()["data"]["id"]

    approve_res = client.patch(
        f"/api/v1/applications/{app1_id}/status",
        json={"status": "APPROVED", "landlord_decision_notes": "Welcome to your new home!"},
        headers=landlord_auth_headers
    )
    assert approve_res.status_code == status.HTTP_200_OK
    assert approve_res.json()["data"]["status"] == "APPROVED"

    check_app2 = client.get(f"/api/v1/applications/{app2_id}", headers=seeker2_headers)
    assert check_app2.status_code == status.HTTP_200_OK
    assert check_app2.json()["data"]["status"] == "REJECTED"
    assert "leased" in check_app2.json()["data"]["landlord_decision_notes"].lower()

    check_prop = client.get(f"/api/v1/properties/{property_id}")
    assert check_prop.status_code == status.HTTP_200_OK
    assert check_prop.json()["data"]["status"] == "LEASED"


def test_auth_rate_limiting_exceeded(client: TestClient):
    from app.core.rate_limiter import forgot_password_rate_limiter
    forgot_password_rate_limiter.requests.clear()
    for _ in range(10):
        client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent@housing.com"})
    blocked_res = client.post("/api/v1/auth/forgot-password", json={"email": "nonexistent@housing.com"})
    assert blocked_res.status_code == status.HTTP_429_TOO_MANY_REQUESTS
    assert blocked_res.json()["error_code"] == "RATE_LIMIT_EXCEEDED"
    forgot_password_rate_limiter.requests.clear()


def test_websocket_chat_communication(client: TestClient, seeker_user: User, landlord_user: User):
    from app.core.security import create_access_token
    token = create_access_token(str(seeker_user.id))
    with client.websocket_connect(f"/ws/chat?token={token}") as ws:
        payload = {
            "receiver_id": landlord_user.id,
            "content": "Real-time WebSocket message test."
        }
        ws.send_text(json.dumps(payload))
        resp = ws.receive_json()
        assert resp["status"] == "sent"
        assert resp["data"]["content"] == "Real-time WebSocket message test."


def test_get_user_conversations_inbox(client: TestClient, seeker_auth_headers: dict, landlord_auth_headers: dict, landlord_user: User):
    send_res = client.post(
        "/api/v1/messages",
        json={"receiver_id": landlord_user.id, "content": "Hello landlord, is the flat vacant?"},
        headers=seeker_auth_headers
    )
    assert send_res.status_code == status.HTTP_201_CREATED

    conv_res = client.get("/api/v1/messages/conversations", headers=seeker_auth_headers)
    assert conv_res.status_code == status.HTTP_200_OK
    data = conv_res.json()["data"]
    assert len(data) >= 1
    assert data[0]["last_message"] == "Hello landlord, is the flat vacant?"
    assert data[0]["lastMessage"] == "Hello landlord, is the flat vacant?"

    all_res = client.get("/api/v1/messages", headers=seeker_auth_headers)
    assert all_res.status_code == status.HTTP_200_OK



