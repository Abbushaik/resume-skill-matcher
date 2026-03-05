# Resume Skill Matcher API

An AI-powered REST API that extracts skills from resumes (PDF/DOCX)
and calculates a weighted match percentage against predefined job
roles using NLP + fuzzy matching.

---

## Tech Stack

- **FastAPI** — REST API framework
- **pdfplumber** — PDF text extraction
- **python-docx** — DOCX text extraction
- **spaCy** — NLP skill extraction
- **rapidfuzz** — Fuzzy skill matching
- **SQLAlchemy + SQLite** — Data storage
- **pytest** — Unit testing

---

## Project Structure
```
resume-matcher/
├── api/
│   └── routes.py            # FastAPI endpoints
├── matcher/
│   ├── skill_extractor.py   # NLP skill extraction
│   ├── synonym_map.py       # Skill normalization
│   └── scoring.py           # Weighted scoring engine
├── parser/
│   ├── pdf_parser.py        # PDF extraction
│   └── docx_parser.py       # DOCX extraction
├── data/
│   └── job_roles.json       # Job roles + skills
├── tests/
│   └── test_matcher.py      # Unit tests
├── logs/                    # Auto-created on startup
├── database.py              # SQLite setup
├── main.py                  # App entry point
└── requirements.txt
```

---

## Setup

### 1. Clone the repo and create virtual environment
```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows
source venv/bin/activate          # Mac/Linux
```

### 2. Install dependencies
```bash
pip install fastapi uvicorn[standard] python-multipart pdfplumber python-docx rapidfuzz spacy aiofiles sqlalchemy pytest
```

### 3. Download spaCy model
```bash
python -m spacy download en_core_web_sm
```

### 4. Run the server
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Open API docs
```
http://localhost:8000/docs
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/roles` | List all job roles |
| POST | `/api/v1/match` | Match resume to specific role |
| POST | `/api/v1/match/all` | Match resume to all roles |
| GET | `/api/v1/history` | View past match results |

---

## POST /api/v1/match

**Form fields:**

| Field | Type | Description |
|-------|------|-------------|
| `resume` | File | PDF or DOCX resume |
| `role_id` | string | Role key from `/roles` |

**Example Response:**
```json
{
  "role_id": "fullstack_engineer",
  "role_title": "Full Stack Engineer",
  "match_percentage": 74.58,
  "extracted_skills": ["git", "javascript", "nodejs", "react"],
  "matched_required": ["git", "javascript", "nodejs"],
  "matched_optional": ["react", "mongodb"],
  "missing_required": ["css", "html"],
  "missing_optional": ["docker", "aws"]
}
```

---

## Scoring Formula
```
score = (matched_required × 0.70 + matched_optional × 0.30)
      / (total_required  × 0.70 + total_optional  × 0.30) × 100
```

Required skills carry **70%** weight, optional skills carry **30%** weight.

---

## Matching Strategies

1. **Exact Match** — direct set intersection after normalization
2. **Fuzzy Match** — rapidfuzz token_sort_ratio (threshold: 82/100)

---

## Run Tests
```bash
pytest tests/ -v
```

---

## Available Job Roles

| Role ID | Title |
|---------|-------|
| `backend_engineer` | Backend Engineer |
| `frontend_engineer` | Frontend Engineer |
| `fullstack_engineer` | Full Stack Engineer |
| `java_backend_engineer` | Java Backend Engineer |
| `nodejs_developer` | Node.js Developer |
| `devops_engineer` | DevOps Engineer |
| `data_scientist` | Data Scientist |
| `ml_engineer` | ML Engineer |
| `mobile_developer` | Mobile Developer |