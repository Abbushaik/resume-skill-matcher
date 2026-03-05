"""
Experience Level Detector

Detects experience level of a skill from resume text.

Examples detected:
- "5 years of Python"
- "3+ yrs experience in React"
- "over 7 years Java"
- "proficient in Docker"
- "familiar with Kubernetes"
"""

import re


BEGINNER_KEYWORDS = [
    "familiar with",
    "basic",
    "learning",
    "beginner",
    "intro to",
]

MID_KEYWORDS = [
    "proficient",
    "experienced",
    "hands-on",
    "worked with",
    "strong knowledge",
]

SENIOR_KEYWORDS = [
    "expert",
    "advanced",
    "deep expertise",
    "architected",
    "led development",
]


def detect_experience(text: str, skill: str) -> str:
    """
    Detect experience level for a given skill.

    Returns:
        senior | mid | beginner | unknown
    """

    text = text.lower()
    skill = skill.lower()

    # -------- Years of experience patterns --------

    patterns = [
        rf"(\d+)\+?\s*(years|yrs|year)\s*(of|in)?\s*{skill}",
        rf"{skill}.*?(\d+)\+?\s*(years|yrs|year)",
        rf"over\s*(\d+)\s*(years|yrs)\s*(of|in)?\s*{skill}",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            years = int(match.group(1))

            if years >= 5:
                return "senior"
            elif years >= 2:
                return "mid"
            else:
                return "beginner"

    # -------- Keyword detection --------

    for word in SENIOR_KEYWORDS:
        if f"{word} {skill}" in text or f"{word} in {skill}" in text:
            return "senior"

    for word in MID_KEYWORDS:
        if f"{word} {skill}" in text or f"{word} in {skill}" in text:
            return "mid"

    for word in BEGINNER_KEYWORDS:
        if f"{word} {skill}" in text or f"{word} in {skill}" in text:
            return "beginner"

    return "unknown"