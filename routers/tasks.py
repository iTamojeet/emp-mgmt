from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Task, User
from schemas import TaskCreate, TaskUpdate, TaskResponse
from dependencies import get_current_user, require_manager

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# Manager: assign a task to an employee
@router.post("/", response_model=TaskResponse)
def create_task(data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    # Verify employee is in manager's department
    employee = db.query(User).filter(
        User.id == data.assigned_to,
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found in your department")

    task = Task(
        title=data.title,
        description=data.description,
        assigned_to=data.assigned_to,
        assigned_by=current_user.id,
        due_date=data.due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


# Manager: view all tasks assigned in their department
@router.get("/team", response_model=list[TaskResponse])
def get_team_tasks(db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    team_ids = [u.id for u in db.query(User).filter(
        User.department_id == current_user.department_id,
        User.role == "employee"
    ).all()]

    return db.query(Task).filter(Task.assigned_to.in_(team_ids)).all()


# Manager: delete a task
@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_manager)):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_by == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}


# Employee: view own tasks
@router.get("/me", response_model=list[TaskResponse])
def my_tasks(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Task).filter(Task.assigned_to == current_user.id).all()


# Employee: update task status
@router.put("/{task_id}", response_model=TaskResponse)
def update_task_status(task_id: int, data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id, Task.assigned_to == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found or not assigned to you")

    task.status = data.status
    db.commit()
    db.refresh(task)
    return task