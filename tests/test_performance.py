from datetime import date

TODAY = str(date.today())


def test_manager_can_add_review(client, seed_users, manager_token):
    """Manager can add a performance review for employee."""
    res = client.post("/performance/review", headers=manager_token, json={
        "user_id":     seed_users["employee_id"],
        "score":       8.5,
        "notes":       "Great work this week",
        "period":      "weekly",
        "review_date": TODAY
    })
    assert res.status_code == 200
    data = res.json()
    assert data["score"]       == 8.5
    assert data["user_id"]     == seed_users["employee_id"]
    assert data["reviewed_by"] == seed_users["manager_id"]


def test_review_score_out_of_range(client, seed_users, manager_token):
    """Score outside 1-10 is rejected."""
    res = client.post("/performance/review", headers=manager_token, json={
        "user_id":     seed_users["employee_id"],
        "score":       15.0,  # invalid
        "period":      "weekly",
        "review_date": TODAY
    })
    assert res.status_code == 400


def test_employee_cannot_add_review(client, seed_users, employee_token):
    """Employee cannot add performance reviews — RBAC check."""
    res = client.post("/performance/review", headers=employee_token, json={
        "user_id":     seed_users["employee_id"],
        "score":       9.0,
        "period":      "weekly",
        "review_date": TODAY
    })
    assert res.status_code == 403


def test_employee_can_submit_self_review(client, seed_users, employee_token):
    """Employee can submit a self review."""
    res = client.post("/performance/self-review", headers=employee_token, json={
        "achievement": "Completed all assigned tasks",
        "challenges":  "Tight deadlines",
        "workload":    3,
        "period":      "weekly",
        "review_date": TODAY
    })
    assert res.status_code == 200
    data = res.json()
    assert data["achievement"] == "Completed all assigned tasks"
    assert data["workload"]    == 3


def test_workload_out_of_range(client, seed_users, employee_token):
    """Workload outside 1-5 is rejected."""
    res = client.post("/performance/self-review", headers=employee_token, json={
        "achievement": "Did stuff",
        "workload":    6,  # invalid
        "period":      "weekly",
        "review_date": TODAY
    })
    assert res.status_code == 400


def test_employee_can_view_own_reviews(client, seed_users, manager_token, employee_token):
    """Employee can view performance reviews given by manager."""
    # Manager adds review first
    client.post("/performance/review", headers=manager_token, json={
        "user_id":     seed_users["employee_id"],
        "score":       7.0,
        "period":      "weekly",
        "review_date": TODAY
    })
    res = client.get("/performance/my-reviews", headers=employee_token)
    assert res.status_code == 200
    assert len(res.json()) == 1
    assert res.json()[0]["score"] == 7.0


def test_manager_can_view_team_self_reviews(client, seed_users, manager_token, employee_token):
    """Manager can view self reviews submitted by their team."""
    # Employee submits self review
    client.post("/performance/self-review", headers=employee_token, json={
        "achievement": "Learned FastAPI",
        "workload":    2,
        "period":      "weekly",
        "review_date": TODAY
    })
    res = client.get("/performance/team/self-reviews", headers=manager_token)
    assert res.status_code == 200
    assert len(res.json()) >= 1