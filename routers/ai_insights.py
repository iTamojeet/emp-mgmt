from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models import User, Attendance, Task, Performance
from schemas import InsightRequest
from dependencies import require_manager
from services.report_service import get_team_report_data
from services.gemini_service import get_gemini_insights, get_attrition_risk
from datetime import date, timedelta

router = APIRouter(prefix="/insights", tags=["AI Insights"])


@router.post("/report")
def get_report(data: InsightRequest, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    report = get_team_report_data(manager=current_user, period=data.period, db=db)
    return report


@router.post("/ai")
def get_ai_insights(data: InsightRequest, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    report = get_team_report_data(manager=current_user, period=data.period, db=db)
    insights = get_gemini_insights(report)
    return {
        "period": data.period,
        "report_data": report,
        "ai_insights": insights
    }


@router.get("/attrition")
def get_attrition(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    # Get all employees in manager's department
    employees = db.query(User).filter(
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).all()

    last_30 = date.today() - timedelta(days=30)
    results = []

    for emp in employees:
        # Attendance in last 30 days
        att = db.query(Attendance).filter(
            Attendance.user_id == emp.id,
            Attendance.date >= last_30
        ).all()

        total_days   = len(att)
        present_days = sum(1 for a in att if a.status == "present")
        absent_days  = sum(1 for a in att if a.status == "absent")

        # Tasks in last 30 days
        tasks = db.query(Task).filter(
            Task.assigned_to == emp.id,
            func.date(Task.created_at) >= last_30
        ).all()

        total_tasks     = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "completed")

        # Performance scores in last 30 days
        perf = db.query(Performance).filter(
            Performance.user_id == emp.id,
            Performance.review_date >= last_30
        ).all()

        avg_score = round(sum(p.score for p in perf) / len(perf), 2) if perf else None

        # Build employee data for Gemini
        emp_data = {
            "name":             emp.name,
            "attendance": {
                "total_days_recorded": total_days,
                "present":             present_days,
                "absent":              absent_days,
            },
            "tasks": {
                "total":     total_tasks,
                "completed": completed_tasks,
            },
            "avg_performance_score": avg_score
        }

        # Get Gemini attrition assessment
        risk = get_attrition_risk(emp_data)
        results.append({
            "employee": emp.name,
            "data":     emp_data,
            "attrition_risk": risk
        })

    return results