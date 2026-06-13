from pydantic import BaseModel
from typing import Optional
from datetime import date
from enum import Enum

# --- Enums ---
class RoleEnum(str, Enum):
    manager  = "manager"
    employee = "employee"

class AttendanceStatus(str, Enum):
    present  = "present"
    absent   = "absent"
    half_day = "half_day"
    leave    = "leave"

class TaskStatus(str, Enum):
    pending     = "pending"
    in_progress = "in_progress"
    completed   = "completed"

class PeriodEnum(str, Enum):
    weekly    = "weekly"
    monthly   = "monthly"
    quarterly = "quarterly"

# --- Auth ---
class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    name: str

# --- User ---
class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: RoleEnum = RoleEnum.employee
    department_id: Optional[int] = None

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    department_id: Optional[int]

    class Config:
        from_attributes = True

# --- Department ---
class DepartmentCreate(BaseModel):
    name: str
    manager_id: Optional[int] = None

class DepartmentResponse(BaseModel):
    id: int
    name: str
    manager_id: Optional[int]

    class Config:
        from_attributes = True

# --- Attendance ---
class AttendanceCreate(BaseModel):
    user_id: int
    date: date
    status: AttendanceStatus

class AttendanceResponse(BaseModel):
    id: int
    user_id: int
    date: date
    status: str

    class Config:
        from_attributes = True

# --- Task ---
class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    assigned_to: int
    due_date: Optional[date] = None

class TaskUpdate(BaseModel):
    status: TaskStatus

class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    assigned_to: int
    assigned_by: int
    status: str
    due_date: Optional[date]

    class Config:
        from_attributes = True

# --- Performance ---
class PerformanceCreate(BaseModel):
    user_id: int
    score: float
    notes: Optional[str] = None
    period: PeriodEnum
    review_date: date

class PerformanceResponse(BaseModel):
    id: int
    user_id: int
    score: float
    notes: Optional[str]
    period: str
    review_date: date

    class Config:
        from_attributes = True

# --- AI Insight ---
class InsightRequest(BaseModel):
    period: PeriodEnum