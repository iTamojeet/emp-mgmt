from sqlalchemy.orm import Session
from sqlalchemy import func
from models import User, Attendance, Task, Performance
from datetime import date, timedelta

def get_period_dates(period: str):
    today = date.today()
    if period == "weekly":
        start = today - timedelta(days=7)
    elif period == "monthly":
        start = today - timedelta(days=30)
    elif period == "quarterly":
        start = today - timedelta(days=90)
    return start, today


def get_team_report_data(manager: User, period: str, db: Session) -> dict:
    start, end = get_period_dates(period)

    # Get all employees in manager's department
    employees = db.query(User).filter(
        User.department_id == manager.department_id,
        User.role == "employee"
    ).all()

    employee_ids = [e.id for e in employees]

    # Attendance summary
    attendance_records = db.query(Attendance).filter(
        Attendance.user_id.in_(employee_ids),
        Attendance.date >= start,
        Attendance.date <= end
    ).all()

    attendance_summary = {}
    for emp in employees:
        records = [a for a in attendance_records if a.user_id == emp.id]
        attendance_summary[emp.name] = {
            "present":  sum(1 for r in records if r.status == "present"),
            "absent":   sum(1 for r in records if r.status == "absent"),
            "half_day": sum(1 for r in records if r.status == "half_day"),
            "leave":    sum(1 for r in records if r.status == "leave"),
        }

    # Task summary
    # Instead of filtering by created_at date range
    # Just get ALL tasks for the team and let Gemini see the full picture
    tasks = db.query(Task).filter(
    Task.assigned_to.in_(employee_ids)
    ).all()

    task_summary = {}
    for emp in employees:
        emp_tasks = [t for t in tasks if t.assigned_to == emp.id]
        task_summary[emp.name] = {
            "total":       len(emp_tasks),
            "completed":   sum(1 for t in emp_tasks if t.status == "completed"),
            "in_progress": sum(1 for t in emp_tasks if t.status == "in_progress"),
            "pending":     sum(1 for t in emp_tasks if t.status == "pending"),
        }

    # Performance summary
    performance_records = db.query(Performance).filter(
        Performance.user_id.in_(employee_ids),
        Performance.review_date >= start,
        Performance.review_date <= end
    ).all()

    performance_summary = {}
    for emp in employees:
        emp_perf = [p for p in performance_records if p.user_id == emp.id]
        if emp_perf:
            avg_score = sum(p.score for p in emp_perf) / len(emp_perf)
            performance_summary[emp.name] = round(float(avg_score), 2)
        else:
            performance_summary[emp.name] = "No reviews yet"

    return {
        "period": period,
        "start_date": str(start),
        "end_date": str(end),
        "department_id": manager.department_id,
        "total_employees": len(employees),
        "attendance": attendance_summary,
        "tasks": task_summary,
        "performance": performance_summary,
    }