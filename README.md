# Resume Skill Matcher

AI-powered Resume Skill Matcher that analyzes resumes and matches them with job roles using NLP and skill scoring.

## Tech Stack

Backend:
- FastAPI
- Python
- spaCy NLP
- RapidFuzz
- SQLite

Frontend:
- React
- Vite
- Tailwind CSS

## Features

- Resume parsing (PDF, DOCX, Images)
- OCR support for scanned resumes
- Skill extraction using NLP
- Exact + Fuzzy skill matching
- Experience based scoring
- Role ranking system

## Project Structure
resume-skill-matcher/
│
├── backend/
│ ├── api/
│ ├── matcher/
│ ├── parser/
│ ├── data/
│ ├── tests/
│ ├── main.py
│ ├── database.py
│ └── requirements.txt
│
├── frontend/
│ ├── src/
│ ├── public/
│ ├── package.json
│ └── vite.config.js
│
└── README.md


## Run Backend
    cd backend
    venv\Scripts\activate
    uvicorn main:app --reload


## Run Frontend
    cd frontend
    npm install
    npm run dev

