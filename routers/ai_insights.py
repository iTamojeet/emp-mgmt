from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import InsightRequest
from dependencies import require_manager
from services.report_service import get_team_report_data
from services.gemini_service import get_gemini_insights

router = APIRouter(prefix="/insights", tags=["AI Insights"])


# Manager: get raw report data for their team
@router.post("/report")
def get_report(data: InsightRequest, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    report = get_team_report_data(manager=current_user, period=data.period, db=db)
    return report


# Manager: get Gemini AI insights for their team
@router.post("/ai")
def get_ai_insights(data: InsightRequest, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    report = get_team_report_data(manager=current_user, period=data.period, db=db)
    insights = get_gemini_insights(report)
    return {
        "period": data.period,
        "report_data": report,
        "ai_insights": insights
    }