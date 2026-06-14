from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User, Performance, SelfReview
from schemas import (
    PerformanceCreateFull, PerformanceResponseFull,
    SelfReviewCreate, SelfReviewResponse
)
from dependencies import get_current_user, require_manager

router = APIRouter(prefix="/performance", tags=["Performance"])


# ── MANAGER: add a performance review for an employee ──
@router.post("/review", response_model=PerformanceResponseFull)
def add_review(
    data: PerformanceCreateFull,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    # Make sure employee is in manager's department
    employee = db.query(User).filter(
        User.id == data.user_id,
        User.department_id == current_user.department_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in your department")

    if not (1 <= data.score <= 10):
        raise HTTPException(status_code=400, detail="Score must be between 1 and 10")

    review = Performance(
        user_id     = data.user_id,
        score       = data.score,
        notes       = data.notes,
        reviewed_by = current_user.id,
        period      = data.period,
        review_date = data.review_date
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# ── MANAGER: get all performance reviews for their team ──
@router.get("/team", response_model=list[PerformanceResponseFull])
def get_team_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    team_ids = [u.id for u in db.query(User).filter(
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).all()]

    return db.query(Performance).filter(
        Performance.user_id.in_(team_ids)
    ).all()


# ── MANAGER: get self reviews submitted by their team ──
@router.get("/team/self-reviews", response_model=list[SelfReviewResponse])
def get_team_self_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_manager)
):
    team_ids = [u.id for u in db.query(User).filter(
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).all()]

    return db.query(SelfReview).filter(
        SelfReview.user_id.in_(team_ids)
    ).all()


# ── EMPLOYEE: submit self review ──
@router.post("/self-review", response_model=SelfReviewResponse)
def submit_self_review(
    data: SelfReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not (1 <= data.workload <= 5):
        raise HTTPException(status_code=400, detail="Workload must be between 1 and 5")

    review = SelfReview(
        user_id     = current_user.id,
        achievement = data.achievement,
        challenges  = data.challenges,
        workload    = data.workload,
        period      = data.period,
        review_date = data.review_date
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review


# ── EMPLOYEE: view own performance reviews from manager ──
@router.get("/my-reviews", response_model=list[PerformanceResponseFull])
def my_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(Performance).filter(
        Performance.user_id == current_user.id
    ).all()


# ── EMPLOYEE: view own self reviews ──
@router.get("/my-self-reviews", response_model=list[SelfReviewResponse])
def my_self_reviews(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return db.query(SelfReview).filter(
        SelfReview.user_id == current_user.id
    ).all()