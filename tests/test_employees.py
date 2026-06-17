def test_manager_can_get_team(client, seed_users, manager_token):
    """Manager can view their team."""
    res = client.get("/employees/", headers=manager_token)
    assert res.status_code == 200
    # Should have 1 employee (Test Employee)
    assert len(res.json()) == 1
    assert res.json()[0]["email"] == seed_users["employee_email"]


def test_employee_cannot_get_team(client, seed_users, employee_token):
    """Employee cannot access team list — RBAC check."""
    res = client.get("/employees/", headers=employee_token)
    assert res.status_code == 403


def test_unauthenticated_cannot_get_team(client):
    """Unauthenticated request is rejected."""
    res = client.get("/employees/")
    assert res.status_code == 401


def test_manager_can_add_employee(client, seed_users, manager_token):
    """Manager can add a new employee to their department."""
    res = client.post("/employees/", headers=manager_token, json={
        "name":     "New Employee",
        "email":    "new@test.com",
        "password": "pass123"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["name"]  == "New Employee"
    assert data["email"] == "new@test.com"
    assert data["role"]  == "employee"


def test_manager_cannot_add_duplicate_email(client, seed_users, manager_token):
    """Adding employee with existing email fails."""
    res = client.post("/employees/", headers=manager_token, json={
        "name":     "Duplicate",
        "email":    seed_users["employee_email"],  # already exists
        "password": "pass123"
    })
    assert res.status_code == 400


def test_manager_can_delete_employee(client, seed_users, manager_token):
    """Manager can remove an employee from their team."""
    res = client.delete(
        f"/employees/{seed_users['employee_id']}",
        headers=manager_token
    )
    assert res.status_code == 200
    assert "removed" in res.json()["message"].lower()


def test_employee_can_view_own_profile(client, seed_users, employee_token):
    """Employee can view their own profile."""
    res = client.get("/employees/me/profile", headers=employee_token)
    assert res.status_code == 200
    assert res.json()["email"] == seed_users["employee_email"]