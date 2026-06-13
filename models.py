from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Date, Text, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Department(Base):
    __tablename__ = "departments"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False, unique=True)
    manager_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    employees  = relationship("User", foreign_keys="User.department_id", back_populates="department")
    manager    = relationship("User", foreign_keys=[manager_id])


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    name            = Column(String(100), nullable=False)
    email           = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role            = Column(Enum("manager", "employee"), nullable=False, default="employee")
    department_id   = Column(Integer, ForeignKey("departments.id"), nullable=True)
    created_at      = Column(TIMESTAMP, server_default=func.now())

    department  = relationship("Department", foreign_keys=[department_id], back_populates="employees")
    attendance  = relationship("Attendance", back_populates="user")
    tasks       = relationship("Task", foreign_keys="Task.assigned_to", back_populates="assignee")
    performance = relationship("Performance", foreign_keys="Performance.user_id", back_populates="user")


class Attendance(Base):
    __tablename__ = "attendance"

    id      = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date    = Column(Date, nullable=False)
    status  = Column(Enum("present", "absent", "half_day", "leave"), nullable=False)

    user = relationship("User", back_populates="attendance")


class Task(Base):
    __tablename__ = "tasks"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(Integer, ForeignKey("users.id"), nullable=False)
    assigned_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    status      = Column(Enum("pending", "in_progress", "completed"), default="pending")
    due_date    = Column(Date, nullable=True)
    created_at  = Column(TIMESTAMP, server_default=func.now())

    assignee    = relationship("User", foreign_keys=[assigned_to], back_populates="tasks")
    assigner    = relationship("User", foreign_keys=[assigned_by])


class Performance(Base):
    __tablename__ = "performance"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    score       = Column(DECIMAL(4, 2), nullable=False)
    notes       = Column(Text, nullable=True)
    reviewed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    period      = Column(Enum("weekly", "monthly", "quarterly"), nullable=False)
    review_date = Column(Date, nullable=False)

    user        = relationship("User", foreign_keys=[user_id], back_populates="performance")
    reviewer    = relationship("User", foreign_keys=[reviewed_by])