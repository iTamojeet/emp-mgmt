import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, get_db
from main import app

# ── Use a separate in-memory SQLite DB for testing ──
# This means tests never touch your real MySQL data
SQLITE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Replace real DB with test DB in every request."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


# Override the DB dependency globally
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_db():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture(scope="function")
def seed_users():
    """Create a manager and an employee in test DB."""
    from models import User, Department
    from services.auth_service import hash_password

    db = TestingSessionLocal()

    # Create department
    dept = Department(name="Engineering")
    db.add(dept)
    db.commit()
    db.refresh(dept)
    dept_id = dept.id  # ← store before closing

    # Create manager
    manager = User(
        name="Test Manager",
        email="manager@test.com",
        hashed_password=hash_password("password123"),
        role="manager",
        department_id=dept_id
    )
    db.add(manager)
    db.commit()
    db.refresh(manager)
    manager_id = manager.id  # ← store before closing

    # Link manager to department
    dept.manager_id = manager_id
    db.commit()

    # Create employee
    employee = User(
        name="Test Employee",
        email="employee@test.com",
        hashed_password=hash_password("password123"),
        role="employee",
        department_id=dept_id
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)
    employee_id = employee.id  # ← store before closing

    db.close()  # now safe to close

    return {
        "manager_email":  "manager@test.com",
        "employee_email": "employee@test.com",
        "password":       "password123",
        "department_id":  dept_id,    # ← plain int, not ORM object
        "manager_id":     manager_id,
        "employee_id":    employee_id
    }


@pytest.fixture(scope="function")
def manager_token(client, seed_users):
    """Login as manager and return auth header."""
    res = client.post("/auth/login", json={
        "email":    seed_users["manager_email"],
        "password": seed_users["password"]
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def employee_token(client, seed_users):
    """Login as employee and return auth header."""
    res = client.post("/auth/login", json={
        "email":    seed_users["employee_email"],
        "password": seed_users["password"]
    })
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}