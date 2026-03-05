"""
Database setup using SQLAlchemy + SQLite.
Stores match results for every resume uploaded.
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# SQLite file will be created at root as resume_matcher.db
DATABASE_URL = "sqlite:///./resume_matcher.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ──────────────────────────────────────────────────────────────────────────────
# Table: MatchResult
# Stores every match request made via the API
# ──────────────────────────────────────────────────────────────────────────────
class MatchResult(Base):
    __tablename__ = "match_results"

    id                = Column(Integer, primary_key=True, index=True)
    filename          = Column(String, nullable=False)
    role_id           = Column(String, nullable=False)
    role_title        = Column(String, nullable=False)
    match_percentage  = Column(Float, nullable=False)
    extracted_skills  = Column(Text, nullable=False)   # stored as comma-separated
    matched_required  = Column(Text, nullable=False)
    matched_optional  = Column(Text, nullable=False)
    missing_required  = Column(Text, nullable=False)
    missing_optional  = Column(Text, nullable=False)
    created_at        = Column(DateTime, default=datetime.utcnow)


def init_db():
    """Create all tables if they don't exist."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Dependency injector for FastAPI routes."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()