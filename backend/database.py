from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# SQLite database file path - dynamically check directory for Portainer volume mount compatibility
DB_DIR = os.environ.get("DB_DIR")
if not DB_DIR:
    # Portainer stack config uses /app/data volume mount. Local dev uses default data dir.
    if os.path.exists("/app/data") and os.access("/app/data", os.W_OK):
        DB_DIR = "/app/data"
    else:
        DB_DIR = os.path.join(os.getcwd(), "data")

DB_PATH = os.path.join(DB_DIR, "syllabus.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
