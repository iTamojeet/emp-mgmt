from fastapi import APIRouter, Depends, HTTPException, Response, Request
from sqlalchemy.orm import Session
from database import get_db
from models import User, Department
from schemas import LoginRequest, TokenResponse
from services.auth_service import verify_password, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Create token with user info inside
    token = create_access_token(data={
        "sub": str(user.id),
        "role": user.role,
        "name": user.name
    })

    return TokenResponse(access_token=token, role=user.role, name=user.name)

@router.get("/me")
def get_me(request: Request, db: Session = Depends(get_db)):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Get manager info via department
    manager_name  = None
    manager_email = None
    if user.department_id:
        dept = db.query(Department).filter(Department.id == user.department_id).first()
        if dept and dept.manager_id:
            manager = db.query(User).filter(User.id == dept.manager_id).first()
            if manager:
                manager_name  = manager.name
                manager_email = manager.email

    return {
        "id":            user.id,
        "name":          user.name,
        "email":         user.email,
        "role":          user.role,
        "department_id": user.department_id,
        "manager_name":  manager_name,
        "manager_email": manager_email
    }