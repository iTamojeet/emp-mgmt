from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Department, User
from schemas import DepartmentCreate, DepartmentResponse
from dependencies import require_manager, get_current_user

router = APIRouter(prefix="/departments", tags=["Departments"])


# Anyone logged in: view all departments
@router.get("/", response_model=list[DepartmentResponse])
def get_departments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Department).all()


# Anyone logged in: view a single department
@router.get("/{department_id}", response_model=DepartmentResponse)
def get_department(department_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")
    return dept


# Manager: create a new department
@router.post("/", response_model=DepartmentResponse)
def create_department(data: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    existing = db.query(Department).filter(Department.name == data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Department already exists")

    dept = Department(name=data.name, manager_id=data.manager_id)
    db.add(dept)
    db.commit()
    db.refresh(dept)
    return dept


# Manager: update department manager
@router.put("/{department_id}", response_model=DepartmentResponse)
def update_department(department_id: int, data: DepartmentCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    dept = db.query(Department).filter(Department.id == department_id).first()
    if not dept:
        raise HTTPException(status_code=404, detail="Department not found")

    dept.name = data.name
    if data.manager_id:
        dept.manager_id = data.manager_id
    db.commit()
    db.refresh(dept)
    return dept