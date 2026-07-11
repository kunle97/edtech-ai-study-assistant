import uuid

from fastapi.testclient import TestClient


def unique_email() -> str:
    return f"student-{uuid.uuid4()}@example.com"


def register_user(
    client: TestClient,
    email: str,
    password: str = "StudyPass123!",
):
    return client.post(
        "/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )


def login_user(
    client: TestClient,
    email: str,
    password: str = "StudyPass123!",
):
    return client.post(
        "/api/v1/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )


def test_register_student(client: TestClient) -> None:
    email = unique_email()

    response = register_user(client, email)

    assert response.status_code == 201

    body = response.json()
    assert body["email"] == email
    assert body["role"] == "student"
    assert body["is_suspended"] is False
    assert "password_hash" not in body


def test_duplicate_registration_returns_conflict(
    client: TestClient,
) -> None:
    email = unique_email()

    assert register_user(client, email).status_code == 201

    response = register_user(client, email)

    assert response.status_code == 409
    assert response.json()["detail"] == (
        "An account with this email already exists"
    )


def test_login_returns_access_token(client: TestClient) -> None:
    email = unique_email()
    register_user(client, email)

    response = login_user(client, email)

    assert response.status_code == 200

    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == email


def test_login_rejects_wrong_password(client: TestClient) -> None:
    email = unique_email()
    register_user(client, email)

    response = login_user(
        client,
        email,
        password="WrongPassword123!",
    )

    assert response.status_code == 401


def test_me_returns_authenticated_user(client: TestClient) -> None:
    email = unique_email()
    register_user(client, email)

    login_response = login_user(client, email)
    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == email


def test_me_rejects_missing_token(client: TestClient) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401