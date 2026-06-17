from datetime import date, timedelta

FUTURE_DATE = str(date.today() + timedelta(days=7))


def test_manager_can_assign_task(client, seed_users, manager_token):
    """Manager can assign a task to an employee."""
    res = client.post("/tasks/", headers=manager_token, json={
        "title":       "Write unit tests",
        "assigned_to": seed_users["employee_id"],
        "due_date":    FUTURE_DATE
    })
    assert res.status_code == 200
    data = res.json()
    assert data["title"]       == "Write unit tests"
    assert data["status"]      == "pending"
    assert data["assigned_to"] == seed_users["employee_id"]
    assert data["assigned_by"] == seed_users["manager_id"]


def test_employee_cannot_assign_task(client, seed_users, employee_token):
    """Employee cannot assign tasks — RBAC check."""
    res = client.post("/tasks/", headers=employee_token, json={
        "title":       "Sneaky task",
        "assigned_to": seed_users["employee_id"],
        "due_date":    FUTURE_DATE
    })
    assert res.status_code == 403


def test_manager_can_view_team_tasks(client, seed_users, manager_token):
    """Manager can view all tasks in their department."""
    client.post("/tasks/", headers=manager_token, json={
        "title":       "Team task",
        "assigned_to": seed_users["employee_id"],
        "due_date":    FUTURE_DATE
    })
    res = client.get("/tasks/team", headers=manager_token)
    assert res.status_code == 200
    assert len(res.json()) >= 1


def test_employee_can_view_own_tasks(client, seed_users, manager_token, employee_token):
    """Employee can view tasks assigned to them."""
    client.post("/tasks/", headers=manager_token, json={
        "title":       "My task",
        "assigned_to": seed_users["employee_id"],
        "due_date":    FUTURE_DATE
    })
    res = client.get("/tasks/me", headers=employee_token)
    assert res.status_code == 200
    assert len(res.json()) == 1


def test_employee_can_update_task_status(client, seed_users, manager_token, employee_token):
    """Employee can update their task status."""
    # Assign task first
    task_res = client.post("/tasks/", headers=manager_token, json={
        "title":       "Update me",
        "assigned_to": seed_users["employee_id"],
        "due_date":    FUTURE_DATE
    })
    task_id = task_res.json()["id"]

    # Update to in_progress
    res = client.put(f"/tasks/{task_id}", headers=employee_token, json={
        "status": "in_progress"
    })
    assert res.status_code == 200
    assert res.json()["status"] == "in_progress"


def test_employee_can_complete_task(client, seed_users, manager_token, employee_token):
    """Employee can mark task as completed."""
    task_res = client.post("/tasks/", headers=manager_token, json={
        "title":       "Complete me",
        "assigned_to": seed_users["employee_id"],
        "due_date":    FUTURE_DATE
    })
    task_id = task_res.json()["id"]

    res = client.put(f"/tasks/{task_id}", headers=employee_token, json={
        "status": "completed"
    })
    assert res.status_code == 200
    assert res.json()["status"] == "completed"


def test_manager_can_delete_task(client, seed_users, manager_token):
    """Manager can delete a task they assigned."""
    task_res = client.post("/tasks/", headers=manager_token, json={
        "title":       "Delete me",
        "assigned_to": seed_users["employee_id"],
        "due_date":    FUTURE_DATE
    })
    task_id = task_res.json()["id"]

    res = client.delete(f"/tasks/{task_id}", headers=manager_token)
    assert res.status_code == 200