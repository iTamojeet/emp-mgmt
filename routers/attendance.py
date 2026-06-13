from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Attendance, User
from schemas import AttendanceCreate, AttendanceResponse
from dependencies import get_current_user, require_manager
from datetime import date

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# Manager: mark attendance for an employee
@router.post("/", response_model=AttendanceResponse)
def mark_attendance(data: AttendanceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    # Make sure the employee belongs to this manager's department
    employee = db.query(User).filter(
        User.id == data.user_id,
        User.department_id == current_user.department_id
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in your department")

    # Check if attendance already marked for this date
    existing = db.query(Attendance).filter(
        Attendance.user_id == data.user_id,
        Attendance.date == data.date
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Attendance already marked for this date")

    record = Attendance(user_id=data.user_id, date=data.date, status=data.status)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


# Manager: update attendance for an employee
@router.put("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance(attendance_id: int, data: AttendanceCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Attendance record not found")

    record.status = data.status
    db.commit()
    db.refresh(record)
    return record


# Manager: view attendance of entire team
@router.get("/team", response_model=list[AttendanceResponse])
def get_team_attendance(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    team_ids = [u.id for u in db.query(User).filter(
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).all()]

    return db.query(Attendance).filter(Attendance.user_id.in_(team_ids)).all()


# Employee: view own attendance
@router.get("/me", response_model=list[AttendanceResponse])
def my_attendance(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Attendance).filter(Attendance.user_id == current_user.id).all()