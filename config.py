import os
from dotenv import load_dotenv

load_dotenv()

# Railway provides DATABASE_URL directly
# Local dev uses individual vars from .env
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    DB_HOST     = os.getenv("DB_HOST")
    DB_PORT     = os.getenv("DB_PORT")
    DB_USER     = os.getenv("DB_USER")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_NAME     = os.getenv("DB_NAME")
    DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    # Railway gives mysql:// — SQLAlchemy needs mysql+pymysql://
    if DATABASE_URL.startswith("mysql://"):
        DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)