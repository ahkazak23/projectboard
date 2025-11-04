from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings


DATABASE_URL = getattr(settings, "SQLALCHEMY_DATABASE_URL", None) or getattr(settings, "DATABASE_URL", None)
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
