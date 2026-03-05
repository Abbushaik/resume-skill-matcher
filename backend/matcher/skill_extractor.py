"""
Skill Extractor Module.
Extracts candidate skills from raw resume text using:
 - Better text cleaning (handles |, •, /, special chars)
 - Known skill keyword matching
 - Sentence-level scanning (catches skills in descriptions)
 - spaCy NLP noun-chunk extraction
 - Section-aware parsing (Skills section gets priority)
"""

import re
import logging
from typing import List, Set

import spacy

from matcher.synonym_map import normalize_skill

logger = logging.getLogger(__name__)

# Known tech skill keywords for fast lookup
KNOWN_SKILLS_SEED = {
    # Languages
    "python", "java", "javascript", "typescript", "c", "c++", "c#",
    "go", "golang", "rust", "kotlin", "swift", "ruby", "php", "scala",
    "r", "bash", "sql", "html", "css",

    # Frameworks
    "react", "angular", "vue", "nodejs", "expressjs", "fastapi",
    "flask", "django", "spring", "springboot", "hibernate",
    "nextjs", "tailwind", "bootstrap", "react native",

    # Databases
    "mysql", "postgresql", "sqlite", "mongodb", "redis", "cassandra",
    "oracle", "dynamodb", "elasticsearch", "firebase",

    # DevOps / Cloud
    "docker", "kubernetes", "git", "linux", "aws", "azure", "gcp",
    "terraform", "ansible", "jenkins", "ci/cd", "nginx",

    # Concepts
    "rest api", "graphql", "microservices", "machine learning",
    "deep learning", "nlp", "data structures", "algorithms",
    "system design", "agile", "devops", "socketio", "oops", "oop",

    # Mobile
    "android", "ios", "flutter", "expo",

    # Messaging / Cache
    "kafka", "celery", "rabbitmq",

    # Testing
    "jest", "pytest", "junit", "selenium", "cypress",

    # Tools
    "maven", "gradle", "webpack", "vite", "figma",
    "pandas", "numpy", "tensorflow", "pytorch", "scikit-learn",
    "mlflow", "spark", "airflow", "tableau",

    # Extra common ones
    "postman", "swagger", "jira", "linux", "ubuntu",
    "socketio", "socket.io", "jwt", "oauth", "graphql",
}

# Regex to detect skills section header
SKILLS_SECTION_PATTERN = re.compile(
    r"(technical\s+skills|skills|technologies|tech\s+stack|tools|"
    r"programming\s+languages|frameworks|expertise|proficiencies|"
    r"core\s+competencies|key\s+skills|it\s+skills|software\s+skills)",
    re.IGNORECASE,
)

# Load spaCy model once
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("spaCy model loaded: en_core_web_sm")
except OSError:
    nlp = None
    logger.warning("spaCy model not found. Run: python -m spacy download en_core_web_sm")


def _clean_text(text: str) -> str:
    """
    Clean resume text before scanning.
    Handles different template formats:
    - Python | React | Node.js  → Python React Node.js
    - Python • React • Node.js  → Python React Node.js
    - Python/React/Node.js      → Python React Node.js
    - Python, React, Node.js    → Python React Node.js
    """
    # Replace separators with spaces
    text = re.sub(r'[|•·/\\●◆▪▸►\-–—]+', ' ', text)
    # Remove brackets and parentheses content that isn't skill-related
    text = re.sub(r'[\(\)\[\]\{\}]', ' ', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


def _extract_skills_section(text: str) -> str:
    """
    Try to isolate the skills section from resume text.
    Falls back to full text if not found.
    """
    lines = text.split("\n")
    in_skills = False
    skills_lines = []

    next_section = re.compile(
        r"^(experience|education|projects|certifications|awards|"
        r"work history|employment|summary|objective|internship|"
        r"achievements|publications|languages|hobbies|interests)",
        re.IGNORECASE
    )

    for line in lines:
        stripped = line.strip()
        if SKILLS_SECTION_PATTERN.match(stripped):
            in_skills = True
            continue
        if in_skills:
            if next_section.match(stripped) and len(stripped) < 40:
                break
            skills_lines.append(stripped)

    return " ".join(skills_lines) if skills_lines else text


def _keyword_match(text: str) -> Set[str]:
    """
    Fast keyword scan.
    Checks multi-word phrases first, then single tokens.
    Works on both original and cleaned text.
    """
    cleaned = _clean_text(text)
    found = set()

    # Scan both original and cleaned text
    for scan_text in [text.lower(), cleaned.lower()]:
        # Multi-word skills first
        for skill in KNOWN_SKILLS_SEED:
            if " " in skill and skill in scan_text:
                found.add(normalize_skill(skill))

        # Single word tokens
        tokens = set(re.findall(r'\b[a-zA-Z][a-zA-Z0-9#+./-]{1,25}\b', scan_text))
        for token in tokens:
            norm = normalize_skill(token)
            if norm in KNOWN_SKILLS_SEED or token in KNOWN_SKILLS_SEED:
                found.add(norm)

    return found


def _scan_sentences(text: str) -> Set[str]:
    """
    Scan every sentence in the resume for skills.
    Catches skills mentioned inside project descriptions
    like 'Built a web app using React and Node.js'
    """
    found = set()
    # Split by sentence endings and newlines
    sentences = re.split(r'[.\n;]', text)
    for sentence in sentences:
        found |= _keyword_match(sentence)
    return found


def _nlp_extract(text: str) -> Set[str]:
    """Use spaCy noun chunks and named entities to catch tech terms."""
    if nlp is None:
        return set()

    doc = nlp(text[:50000])
    found = set()

    for chunk in doc.noun_chunks:
        norm = normalize_skill(chunk.text.strip().lower())
        if norm in KNOWN_SKILLS_SEED:
            found.add(norm)

    for ent in doc.ents:
        if ent.label_ in ("ORG", "PRODUCT"):
            norm = normalize_skill(ent.text.strip().lower())
            if norm in KNOWN_SKILLS_SEED:
                found.add(norm)

    return found


def extract_skills(resume_text: str) -> List[str]:
    """
    Main entry point.
    Extracts and deduplicates skills from resume text.

    Strategy:
      1. Clean text (handle |, •, / separators)
      2. Keyword scan on full resume
      3. Keyword scan on isolated skills section
      4. Sentence-level scan (catches skills in descriptions)
      5. spaCy NLP pass
      6. Deduplicate and sort

    Args:
        resume_text: Raw text extracted from resume.

    Returns:
        Sorted list of unique normalized skill names.
    """
    if not resume_text or not resume_text.strip():
        return []

    skills_section = _extract_skills_section(resume_text)

    # Step 1: Keyword scan on full resume
    found = _keyword_match(resume_text)

    # Step 2: Keyword scan on skills section
    found |= _keyword_match(skills_section)

    # Step 3: Sentence-level scan (catches skills in project descriptions)
    found |= _scan_sentences(resume_text)

    # Step 4: NLP pass on skills section
    found |= _nlp_extract(skills_section)

    result = sorted(found)
    logger.info(f"Extracted {len(result)} skills: {result}")
    return result