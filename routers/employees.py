from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import User
from schemas import UserCreate, UserResponse
from dependencies import get_current_user, require_manager
from services.auth_service import hash_password

router = APIRouter(prefix="/employees", tags=["Employees"])


# Manager: get all employees in their department
@router.get("/", response_model=list[UserResponse])
def get_my_team(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    team = db.query(User).filter(
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).all()
    return team


# Manager: get a single employee (must be in their department)
@router.get("/{employee_id}", response_model=UserResponse)
def get_employee(employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    employee = db.query(User).filter(
        User.id == employee_id,
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in your department")
    return employee


# Manager: add a new employee to their department
@router.post("/", response_model=UserResponse)
def create_employee(data: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    # Check email not already taken
    existing = db.query(User).filter(User.email == data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_employee = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role="employee",
        department_id=current_user.department_id  # always assigned to manager's dept
    )
    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)
    return new_employee


# Manager: remove an employee from their department
@router.delete("/{employee_id}")
def delete_employee(employee_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    employee = db.query(User).filter(
        User.id == employee_id,
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in your department")

    db.delete(employee)
    db.commit()
    return {"message": f"Employee {employee.name} removed successfully"}


# Employee: view own profile
@router.get("/me/profile", response_model=UserResponse)
def my_profile(current_user: User = Depends(get_current_user)):
    return current_user