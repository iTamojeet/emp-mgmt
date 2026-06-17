from datetime import date

TODAY = str(date.today())


def test_manager_can_mark_attendance(client, seed_users, manager_token):
    """Manager can mark attendance for an employee."""
    res = client.post("/attendance/", headers=manager_token, json={
        "user_id": seed_users["employee_id"],
        "date":    TODAY,
        "status":  "present"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"]  == "present"
    assert data["user_id"] == seed_users["employee_id"]


def test_duplicate_attendance_fails(client, seed_users, manager_token):
    """Marking attendance twice for same day fails."""
    payload = {
        "user_id": seed_users["employee_id"],
        "date":    TODAY,
        "status":  "present"
    }
    client.post("/attendance/", headers=manager_token, json=payload)
    res = client.post("/attendance/", headers=manager_token, json=payload)
    assert res.status_code == 400


def test_employee_cannot_mark_attendance(client, seed_users, employee_token):
    """Employee cannot mark attendance — RBAC check."""
    res = client.post("/attendance/", headers=employee_token, json={
        "user_id": seed_users["employee_id"],
        "date":    TODAY,
        "status":  "present"
    })
    assert res.status_code == 403


def test_manager_can_view_team_attendance(client, seed_users, manager_token):
    """Manager can view team attendance records."""
    # Mark first
    client.post("/attendance/", headers=manager_token, json={
        "user_id": seed_users["employee_id"],
        "date":    TODAY,
        "status":  "present"
    })
    res = client.get("/attendance/team", headers=manager_token)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_employee_can_view_own_attendance(client, seed_users, manager_token, employee_token):
    """Employee can view their own attendance."""
    # Manager marks first
    client.post("/attendance/", headers=manager_token, json={
        "user_id": seed_users["employee_id"],
        "date":    TODAY,
        "status":  "present"
    })
    res = client.get("/attendance/me", headers=employee_token)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["status"] == "present"


def test_all_attendance_statuses(client, seed_users, manager_token):
    """All valid attendance statuses are accepted."""
    from datetime import timedelta
    statuses = ["present", "absent", "half_day", "leave"]
    for i, status in enumerate(statuses):
        day = str(date.today() + timedelta(days=i+1))
        res = client.post("/attendance/", headers=manager_token, json={
            "user_id": seed_users["employee_id"],
            "date":    day,
            "status":  status
        })
        assert res.status_code == 200