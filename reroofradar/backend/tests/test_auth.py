def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_successful_registration(client):
    response = client.post(
        "/api/auth/register",
        json={
            "email": "test@example.com",
            "password": "securepass123",
            "full_name": "Test User",
            "company_name": "TestCo",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["full_name"] == "Test User"
    assert data["company_name"] == "TestCo"
    assert "id" in data
    assert data["is_active"] is True


def test_successful_login(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "login@example.com",
            "password": "securepass123",
            "full_name": "Login User",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={
            "email": "login@example.com",
            "password": "securepass123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_bad_credentials(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "bad@example.com",
            "password": "correctpass",
            "full_name": "Bad User",
        },
    )
    response = client.post(
        "/api/auth/login",
        json={
            "email": "bad@example.com",
            "password": "wrongpass",
        },
    )
    assert response.status_code == 401


def test_protected_endpoint_without_token(client):
    response = client.get("/api/campaigns/")
    assert response.status_code == 401


def test_protected_endpoint_with_invalid_token(client):
    response = client.get(
        "/api/campaigns/",
        headers={"Authorization": "Bearer invalidtoken123"},
    )
    assert response.status_code == 401


def test_auth_me_with_valid_token(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "me@example.com",
            "password": "securepass123",
            "full_name": "Me User",
            "company_name": "MeCo",
        },
    )
    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "me@example.com",
            "password": "securepass123",
        },
    )
    token = login_resp.json()["access_token"]
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "Me User"
    assert data["company_name"] == "MeCo"


def test_protected_endpoint_with_valid_token(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "campaign@example.com",
            "password": "securepass123",
            "full_name": "Campaign User",
        },
    )
    login_resp = client.post(
        "/api/auth/login",
        json={
            "email": "campaign@example.com",
            "password": "securepass123",
        },
    )
    token = login_resp.json()["access_token"]
    response = client.get(
        "/api/campaigns/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
