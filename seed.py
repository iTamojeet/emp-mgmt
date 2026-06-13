from database import SessionLocal
from models import User, Department
from services.auth_service import hash_password

db = SessionLocal()

# Make sure departments exist first
departments = db.query(Department).all()
if not departments:
    print("Run the SQL schema first. No departments found.")
    db.close()
    exit()

users = [
    User(name="Alice Manager",  email="alice@company.com", hashed_password=hash_password("password123"), role="manager",  department_id=1),
    User(name="Bob Manager",    email="bob@company.com",   hashed_password=hash_password("password123"), role="manager",  department_id=2),
    User(name="Carol Employee", email="carol@company.com", hashed_password=hash_password("password123"), role="employee", department_id=1),
    User(name="Dave Employee",  email="dave@company.com",  hashed_password=hash_password("password123"), role="employee", department_id=1),
    User(name="Eve Employee",   email="eve@company.com",   hashed_password=hash_password("password123"), role="employee", department_id=2),
]

db.add_all(users)
db.commit()

# Link managers to departments
dept1 = db.query(Department).filter(Department.id == 1).first()
dept2 = db.query(Department).filter(Department.id == 2).first()
alice = db.query(User).filter(User.email == "alice@company.com").first()
bob   = db.query(User).filter(User.email == "bob@company.com").first()

dept1.manager_id = alice.id
dept2.manager_id = bob.id
db.commit()
db.close()

print("✅ Seed done. Alice & Bob are managers. Carol, Dave, Eve are employees.")