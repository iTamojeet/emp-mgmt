from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter(tags=["Pages"])
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard/manager")
def manager_dashboard(request: Request):
    return templates.TemplateResponse("dashboard_manager.html", {"request": request})

@router.get("/dashboard/employee")
def employee_dashboard(request: Request):
    return templates.TemplateResponse("dashboard_employee.html", {"request": request})