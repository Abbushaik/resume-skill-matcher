"""
FastAPI REST API Routes.

Endpoints:
  POST /match        - Upload resume + role → get match score
  POST /match/all    - Upload resume → score against ALL roles
  GET  /roles        - List all available job roles
  GET  /history      - View all past match results from DB
  GET  /health       - Health check
"""

import os
import json
import logging
import tempfile
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, status
from sqlalchemy.orm import Session

from parser.pdf_parser import extract_text_from_pdf
from parser.docx_parser import extract_text_from_docx
from parser.image_parser import extract_text_from_image
from matcher.skill_extractor import extract_skills
from matcher.scoring import calculate_match
from database import get_db, MatchResult

logger = logging.getLogger(__name__)
router = APIRouter()

# Load job roles
ROLES_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "job_roles.json")

with open(ROLES_PATH, "r") as f:
    JOB_ROLES = json.load(f)["roles"]

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".jpg", ".jpeg", ".png", ".bmp", ".tiff"}


# ─────────────────────────────────────────────
# Resume Parser
# ─────────────────────────────────────────────

def _parse_resume(file: UploadFile) -> str:

    filename = file.filename or "resume"
    ext = os.path.splitext(filename)[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{ext}'. Only PDF, DOCX, JPG, PNG accepted.",
        )

    content = file.file.read()

    # File size validation (5MB)
    max_size = 5 * 1024 * 1024

    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum allowed size is 5MB. Your file is {round(len(content)/1024/1024,2)}MB."
        )

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:

        if ext == ".pdf":
            return extract_text_from_pdf(tmp_path)

        elif ext == ".docx":
            return extract_text_from_docx(tmp_path)

        else:
            return extract_text_from_image(tmp_path)

    except ValueError as e:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )

    except Exception as e:

        logger.error(f"Resume parsing failed: {e}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to parse resume."
        )

    finally:
        os.unlink(tmp_path)


# ─────────────────────────────────────────────
# Health Check
# ─────────────────────────────────────────────

@router.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": "Resume Skill Matcher API"}


# ─────────────────────────────────────────────
# List Roles
# ─────────────────────────────────────────────

@router.get("/roles", tags=["Roles"])
def list_roles():

    return {
        "total": len(JOB_ROLES),
        "roles": {
            key: {
                "title": data["title"],
                "required_skills": data["required_skills"],
                "optional_skills": data["optional_skills"],
            }
            for key, data in JOB_ROLES.items()
        },
    }


# ─────────────────────────────────────────────
# Match Resume To One Role
# ─────────────────────────────────────────────

@router.post("/match", tags=["Matching"])
async def match_resume_to_role(

    resume: UploadFile = File(...),
    role_id: str = Form(...),
    db: Session = Depends(get_db),

):

    if role_id not in JOB_ROLES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role '{role_id}' not found."
        )

    role = JOB_ROLES[role_id]

    resume_text = _parse_resume(resume)

    candidate_skills = extract_skills(resume_text)

    # ✅ FIXED CALL
    result = calculate_match(
        resume_text,
        candidate_skills,
        role["required_skills"],
        role["optional_skills"]
    )

    record = MatchResult(
        filename=resume.filename or "unknown",
        role_id=role_id,
        role_title=role["title"],
        match_percentage=result["match_percentage"],
        extracted_skills=", ".join(candidate_skills),
        matched_required=", ".join(result["matched_required"]),
        matched_optional=", ".join(result["matched_optional"]),
        missing_required=", ".join(result["missing_required"]),
        missing_optional=", ".join(result["missing_optional"]),
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "id": record.id,
        "role_id": role_id,
        "role_title": role["title"],
        "extracted_skills": candidate_skills,
        **result,
    }


# ─────────────────────────────────────────────
# Match Resume Against All Roles
# ─────────────────────────────────────────────

@router.post("/match/all", tags=["Matching"])
async def match_resume_to_all_roles(

    resume: UploadFile = File(...),
    top_n: Optional[int] = Form(default=5),
    db: Session = Depends(get_db),

):

    resume_text = _parse_resume(resume)

    candidate_skills = extract_skills(resume_text)

    results = []

    for role_id, role in JOB_ROLES.items():

        # ✅ FIXED CALL
        score_data = calculate_match(
            resume_text,
            candidate_skills,
            role["required_skills"],
            role["optional_skills"]
        )

        results.append({
            "role_id": role_id,
            "role_title": role["title"],
            "match_percentage": score_data["match_percentage"],
            "matched_required": score_data["matched_required"],
            "matched_optional": score_data["matched_optional"],
            "missing_required": score_data["missing_required"],
            "missing_optional": score_data["missing_optional"],
        })

    results.sort(key=lambda x: x["match_percentage"], reverse=True)

    top_n = max(1, min(top_n or 5, len(results)))

    if results:

        top = results[0]

        record = MatchResult(
            filename=resume.filename or "unknown",
            role_id=top["role_id"],
            role_title=top["role_title"],
            match_percentage=top["match_percentage"],
            extracted_skills=", ".join(candidate_skills),
            matched_required=", ".join(top["matched_required"]),
            matched_optional=", ".join(top["matched_optional"]),
            missing_required=", ".join(top["missing_required"]),
            missing_optional=", ".join(top["missing_optional"]),
        )

        db.add(record)
        db.commit()

    return {
        "extracted_skills": candidate_skills,
        "total_roles_evaluated": len(results),
        "top_matches": results[:top_n],
    }


# ─────────────────────────────────────────────
# History
# ─────────────────────────────────────────────

@router.get("/history", tags=["History"])
def get_history(db: Session = Depends(get_db)):

    records = db.query(MatchResult).order_by(MatchResult.created_at.desc()).all()

    return {
        "total": len(records),
        "results": [
            {
                "id": r.id,
                "filename": r.filename,
                "role_id": r.role_id,
                "role_title": r.role_title,
                "match_percentage": r.match_percentage,
                "extracted_skills": r.extracted_skills.split(", "),
                "matched_required": r.matched_required.split(", "),
                "missing_required": r.missing_required.split(", "),
                "created_at": r.created_at,
            }
            for r in records
        ],
    }