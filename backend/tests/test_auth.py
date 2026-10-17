def test_register_user(client):
    payload = {
        "email": "testpatient@example.com",
        "password": "Password123!",
        "full_name": "Test Patient",
        "role": "patient",
        "phone": "+919876543210",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "testpatient@example.com"
    assert data["full_name"] == "Test Patient"
    assert data["role"] == "patient"
    assert "password" not in data


def test_register_duplicate_email(client):
    payload = {
        "email": "testpatient@example.com",
        "password": "Password123!",
        "full_name": "Duplicate User",
        "role": "patient",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]


def test_login_success(client):
    payload = {
        "email": "testpatient@example.com",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == "testpatient@example.com"


def test_login_invalid_password(client):
    payload = {
        "email": "testpatient@example.com",
        "password": "WrongPassword!",
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert "Incorrect email or password" in response.json()["error"]


def test_get_current_user_profile(client):
    # First login to get token
    login_res = client.post("/api/v1/auth/login", json={
        "email": "testpatient@example.com",
        "password": "Password123!",
    })
    token = login_res.json()["access_token"]

    # Call /me with Bearer token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testpatient@example.com"
    assert data["full_name"] == "Test Patient"
