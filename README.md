# Employee Management System

A FastAPI-based Employee Management System with RBAC, MySQL, and Google Gemini AI insights.

## Tech Stack
- **Backend:** Python 3.14, FastAPI, SQLAlchemy
- **Database:** MySQL 9.5 (Docker)
- **Frontend:** Jinja2 HTML/CSS (Windows XP theme)
- **Auth:** JWT (python-jose), bcrypt
- **AI:** Google Gemini API

## Project Structure
emp-mgmt/
├── main.py               # App entry point
├── database.py           # DB connection
├── models.py             # SQLAlchemy ORM models
├── schemas.py            # Pydantic schemas
├── dependencies.py       # Auth dependencies / RBAC
├── seed.py               # Dummy data seeder
├── routers/
│   ├── auth.py           # Login, /me
│   ├── employees.py      # Employee CRUD
│   ├── departments.py    # Department CRUD
│   ├── attendance.py     # Attendance tracking
│   ├── tasks.py          # Task management
│   ├── ai_insights.py    # Gemini AI reports
│   └── pages.py          # HTML page routes
├── services/
│   ├── auth_service.py   # JWT + bcrypt
│   ├── report_service.py # Data aggregation
│   └── gemini_service.py # Gemini API calls
└── templates/            # Jinja2 HTML (XP theme)

## Setup

### 1. Clone and create virtual environment
```bash
git clone <your-repo>
cd emp-mgmt
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Start MySQL (Docker)
```bash
docker exec -it mysql mysql -u root -p
# paste the SQL schema from schema.sql
```

### 3. Configure environment
```bash
cp .env.example .env
# edit .env with your values
```

### 4. Seed dummy data
```bash
python3 seed.py
```

### 5. Run the app
```bash
python3 -m uvicorn main:app --reload
```

Visit: http://127.0.0.1:8000

## Default Credentials
| Name | Email | Password | Role |
|------|-------|----------|------|
| Alice Manager | alice@company.com | password123 | Manager |
| Bob Manager | bob@company.com | password123 | Manager |
| Carol Employee | carol@company.com | password123 | Employee |
| Dave Employee | dave@company.com | password123 | Employee |
| Eve Employee | eve@company.com | password123 | Employee |

## API Endpoints
| Method | Endpoint | Access | Description |
|--------|----------|--------|-------------|
| POST | /auth/login | Public | Login |
| GET | /auth/me | Any | Current user |
| GET | /employees/ | Manager | Get team |
| POST | /employees/ | Manager | Add employee |
| DELETE | /employees/{id} | Manager | Remove employee |
| POST | /attendance/ | Manager | Mark attendance |
| GET | /attendance/team | Manager | Team attendance |
| GET | /attendance/me | Employee | Own attendance |
| POST | /tasks/ | Manager | Assign task |
| GET | /tasks/team | Manager | Team tasks |
| PUT | /tasks/{id} | Employee | Update task status |
| GET | /tasks/me | Employee | Own tasks |
| POST | /insights/ai | Manager | Gemini AI report |

## GenAI Feature
Managers can generate AI-powered team insights for weekly, monthly, or quarterly periods. Gemini analyzes attendance, task completion, and performance data to provide actionable recommendations.