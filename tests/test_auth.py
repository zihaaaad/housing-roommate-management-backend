from fastapi import status
from fastapi.testclient import TestClient


def test_user_registration_success(client: TestClient):
    payload = {
        "email": "fresh_user@housing.com",
        "username": "fresh_user",
        "password": "SecurePassword@123",
        "full_name": "Fresh User",
        "phone_number": "+8801711889900",
        "role": "ROOMMATE_SEEKER"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    json_data = response.json()
    assert json_data["success"] is True
    assert json_data["data"]["email"] == "fresh_user@housing.com"
    assert "password" not in json_data["data"]


def test_user_registration_duplicate_email(client: TestClient):
    payload = {
        "email": "fresh_user@housing.com",
        "username": "distinct_user",
        "password": "SecurePassword@123",
        "full_name": "Duplicate User",
        "role": "ROOMMATE_SEEKER"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json()["success"] is False


def test_user_login_success(client: TestClient):
    payload = {
        "username_or_email": "fresh_user@housing.com",
        "password": "SecurePassword@123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    json_data = response.json()
    assert json_data["success"] is True
    assert "access_token" in json_data["data"]
    assert "refresh_token" in json_data["data"]


def test_user_login_invalid_password(client: TestClient):
    payload = {
        "username_or_email": "fresh_user@housing.com",
        "password": "WrongPassword@123"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json()["success"] is False


def test_token_refresh_flow(client: TestClient):
    login_response = client.post("/api/v1/auth/login", json={
        "username_or_email": "fresh_user@housing.com",
        "password": "SecurePassword@123"
    })
    refresh_token = login_response.json()["data"]["refresh_token"]

    refresh_response = client.post("/api/v1/auth/refresh", json={
        "refresh_token": refresh_token
    })
    assert refresh_response.status_code == status.HTTP_200_OK
    assert "access_token" in refresh_response.json()["data"]


def test_forgot_and_reset_password_flow(client: TestClient):
    forgot_response = client.post("/api/v1/auth/forgot-password", json={
        "email": "fresh_user@housing.com"
    })
    assert forgot_response.status_code == status.HTTP_200_OK
    reset_token = forgot_response.json()["data"]["reset_token"]
    assert reset_token is not None

    reset_response = client.post("/api/v1/auth/reset-password", json={
        "reset_token": reset_token,
        "new_password": "NewSecretPassword@999"
    })
    assert reset_response.status_code == status.HTTP_200_OK

    login_new_pass = client.post("/api/v1/auth/login", json={
        "username_or_email": "fresh_user@housing.com",
        "password": "NewSecretPassword@999"
    })
    assert login_new_pass.status_code == status.HTTP_200_OK


def test_get_current_user_unauthorized(client: TestClient):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_current_user_authorized(client: TestClient, seeker_auth_headers: dict):
    response = client.get("/api/v1/auth/me", headers=seeker_auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["data"]["email"] == "test_seeker@housing.com"
