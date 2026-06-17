def test_login_success_manager(client, seed_users):
    """Manager can login with correct credentials."""
    res = client.post("/auth/login", json={
        "email":    seed_users["manager_email"],
        "password": seed_users["password"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "manager"
    assert data["name"] == "Test Manager"


def test_login_success_employee(client, seed_users):
    """Employee can login with correct credentials."""
    res = client.post("/auth/login", json={
        "email":    seed_users["employee_email"],
        "password": seed_users["password"]
    })
    assert res.status_code == 200
    data = res.json()
    assert data["role"] == "employee"


def test_login_wrong_password(client, seed_users):
    """Login fails with wrong password."""
    res = client.post("/auth/login", json={
        "email":    seed_users["manager_email"],
        "password": "wrongpassword"
    })
    assert res.status_code == 401
    assert res.json()["detail"] == "Invalid email or password"


def test_login_wrong_email(client, seed_users):
    """Login fails with unknown email."""
    res = client.post("/auth/login", json={
        "email":    "nobody@test.com",
        "password": "password123"
    })
    assert res.status_code == 401


def test_get_me_as_manager(client, seed_users, manager_token):
    """Authenticated manager can get their own info."""
    res = client.get("/auth/me", headers=manager_token)
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == seed_users["manager_email"]
    assert data["role"] == "manager"


def test_get_me_as_employee(client, seed_users, employee_token):
    """Authenticated employee can get their own info."""
    res = client.get("/auth/me", headers=employee_token)
    assert res.status_code == 200
    assert res.json()["role"] == "employee"


def test_get_me_without_token(client):
    """Unauthenticated request to /me is rejected."""
    res = client.get("/auth/me")
    assert res.status_code == 401


def test_get_me_with_invalid_token(client):
    """Invalid token is rejected."""
    res = client.get("/auth/me", headers={"Authorization": "Bearer faketoken"})
    assert res.status_code == 401