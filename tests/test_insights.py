from datetime import date, timedelta
from unittest.mock import patch

TODAY = str(date.today())


def test_get_raw_report(client, seed_users, manager_token):
    """Manager can get raw team report data."""
    res = client.post("/insights/report", headers=manager_token, json={
        "period": "weekly"
    })
    assert res.status_code == 200
    data = res.json()
    assert "attendance"  in data
    assert "tasks"       in data
    assert "performance" in data
    assert data["total_employees"] == 1


def test_employee_cannot_get_report(client, seed_users, employee_token):
    """Employee cannot access AI insights — RBAC check."""
    res = client.post("/insights/report", headers=employee_token, json={
        "period": "weekly"
    })
    assert res.status_code == 403


def test_ai_insights_mocked(client, seed_users, manager_token):
    """AI insights endpoint works — Gemini mocked to avoid API calls in tests."""
    with patch("services.gemini_service.model") as mock_model:
        # Mock Gemini response
        mock_model.generate_content.return_value.text = "Great team performance this week."

        res = client.post("/insights/ai", headers=manager_token, json={
            "period": "monthly"
        })
        assert res.status_code == 200
        data = res.json()
        assert "ai_insights" in data
        assert "report_data" in data


def test_attrition_risk_mocked(client, seed_users, manager_token):
    """Attrition risk endpoint works — Gemini mocked."""
    import json
    mock_response = json.dumps({
        "risk_level":      "LOW",
        "reason":          "Good attendance and task completion.",
        "recommendation":  "Keep up the good work."
    })

    with patch("services.gemini_service.model") as mock_model:
        mock_model.generate_content.return_value.text = mock_response

        res = client.get("/insights/attrition", headers=manager_token)
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1  # 1 employee in test dept
        assert data[0]["attrition_risk"]["risk_level"] == "LOW"


def test_report_reflects_actual_data(client, seed_users, manager_token):
    """Report data correctly reflects marked attendance."""
    # Mark attendance for employee
    client.post("/attendance/", headers=manager_token, json={
        "user_id": seed_users["employee_id"],
        "date":    TODAY,
        "status":  "present"
    })

    res = client.post("/insights/report", headers=manager_token, json={
        "period": "weekly"
    })
    assert res.status_code == 200
    data = res.json()
    # Employee should show 1 present day
    emp_attendance = data["attendance"].get("Test Employee", {})
    assert emp_attendance.get("present") == 1