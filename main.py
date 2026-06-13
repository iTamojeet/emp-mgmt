from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from database import engine, Base

# Import all routers
from routers import auth, employees, departments, attendance, tasks, ai_insights, pages

# Create all DB tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Employee Management System",
    version="1.0.0",
    swagger_ui_parameters={"persistAuthorization": True}
)

# Mount static folder for CSS/JS files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register all routers
app.include_router(auth.router)
app.include_router(employees.router)
app.include_router(departments.router)
app.include_router(attendance.router)
app.include_router(tasks.router)
app.include_router(ai_insights.router)
app.include_router(pages.router)  # ← serves HTML pages

# Redirect root to login page
@app.get("/")
def root():
    return RedirectResponse(url="/login")