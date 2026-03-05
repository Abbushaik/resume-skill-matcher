"""
Resume Skill Matcher API
Main application entry point.

Run with:
    uvicorn main:app --reload --host 0.0.0.0 --port 8000

Docs at:
    http://localhost:8000/docs
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from database import init_db

# ──────────────────────────────────────────────────────────────────────────────
# Logging setup
# ──────────────────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
os.makedirs("logs", exist_ok=True)

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("logs/app.log", encoding="utf-8"),
    ],
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Lifespan — runs on startup and shutdown
# ──────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up — initializing database...")
    init_db()
    logger.info("Database ready. Server is live.")
    yield
    logger.info("Shutting down.")


# ──────────────────────────────────────────────────────────────────────────────
# App
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Resume Skill Matcher API",
    description=(
        "Extracts skills from resumes (PDF/DOCX) and calculates "
        "a weighted match percentage against predefined job roles "
        "using NLP + fuzzy matching."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(router, prefix="/api/v1")


@app.get("/", include_in_schema=False)
def root():
    return {
        "message": "Resume Skill Matcher API v1.0.0",
        "docs": "Visit /docs for full API reference"
    }