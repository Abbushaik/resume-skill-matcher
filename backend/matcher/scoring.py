"""
Scoring Engine.
Calculates weighted match percentage between resume skills and job role.

Two matching strategies:
  1. Exact match  — direct set intersection after normalization
  2. Fuzzy match  — rapidfuzz for near-matches (typos, abbreviations)

Weighted formula:
  score = (matched_required * 0.70 + matched_optional * 0.30)
        / (total_required  * 0.70 + total_optional  * 0.30) * 100

Enhanced with Experience Level Detection per skill.
"""

import logging
from typing import List, Dict, Any

from rapidfuzz import fuzz, process

from matcher.synonym_map import normalize_skill
from matcher.experience_detector import detect_experience

logger = logging.getLogger(__name__)

# Scoring weights
W_REQ = 0.70
W_OPT = 0.30

# Fuzzy threshold
FUZZY_THRESHOLD = 82

# Experience multipliers
EXPERIENCE_WEIGHT = {
    "senior": 1.2,
    "mid": 1.0,
    "beginner": 0.8,
    "unknown": 1.0,
}


def _exact_match(candidate_skills: List[str], target_skills: List[str]) -> List[str]:
    """Return skills present in both lists after normalization."""
    candidate_set = {normalize_skill(s) for s in candidate_skills}

    return [
        s for s in target_skills
        if normalize_skill(s) in candidate_set
    ]


def _fuzzy_match(candidate_skills: List[str], target_skills: List[str]) -> List[str]:
    """
    For each unmatched target skill, try rapidfuzz token_sort_ratio.
    """

    already_matched = set(_exact_match(candidate_skills, target_skills))

    unmatched_targets = [
        s for s in target_skills
        if s not in already_matched
    ]

    if not unmatched_targets or not candidate_skills:
        return []

    fuzzy_hits = []

    for target in unmatched_targets:

        result = process.extractOne(
            target,
            candidate_skills,
            scorer=fuzz.token_sort_ratio,
            score_cutoff=FUZZY_THRESHOLD,
        )

        if result:
            logger.debug(
                f"Fuzzy match: '{target}' ← '{result[0]}' (score={result[1]})"
            )

            fuzzy_hits.append(target)

    return fuzzy_hits


def calculate_match(
    resume_text: str,
    candidate_skills: List[str],
    required_skills: List[str],
    optional_skills: List[str],
) -> Dict[str, Any]:
    """
    Calculate weighted match score with experience adjustment.
    """

    # ---------- REQUIRED SKILLS ----------

    exact_req = _exact_match(candidate_skills, required_skills)
    fuzzy_req = _fuzzy_match(candidate_skills, required_skills)

    matched_req = list(set(exact_req + fuzzy_req))
    missing_req = [s for s in required_skills if s not in matched_req]

    # ---------- OPTIONAL SKILLS ----------

    exact_opt = _exact_match(candidate_skills, optional_skills)
    fuzzy_opt = _fuzzy_match(candidate_skills, optional_skills)

    matched_opt = list(set(exact_opt + fuzzy_opt))
    missing_opt = [s for s in optional_skills if s not in matched_opt]

    # ---------- EXPERIENCE DETECTION ----------

    experience_levels = {}

    req_score = 0

    for skill in matched_req:

        level = detect_experience(resume_text, skill)

        experience_levels[skill] = level

        req_score += EXPERIENCE_WEIGHT[level]

    opt_score = 0

    for skill in matched_opt:

        level = detect_experience(resume_text, skill)

        experience_levels[skill] = level

        opt_score += EXPERIENCE_WEIGHT[level]

    # ---------- FINAL SCORE ----------

    total_req = len(required_skills)
    total_opt = len(optional_skills)

    denominator = (total_req * W_REQ) + (total_opt * W_OPT)

    if denominator == 0:
        score = 0.0
    else:
        numerator = (req_score * W_REQ) + (opt_score * W_OPT)
        score = round((numerator / denominator) * 100, 2)

    result = {
        "match_percentage": score,
        "matched_required": sorted(matched_req),
        "matched_optional": sorted(matched_opt),
        "missing_required": sorted(missing_req),
        "missing_optional": sorted(missing_opt),
        "total_required": total_req,
        "total_optional": total_opt,
        "experience_levels": experience_levels,
        "match_strategy_breakdown": {
            "exact_required": sorted(exact_req),
            "fuzzy_required": sorted(fuzzy_req),
            "exact_optional": sorted(exact_opt),
            "fuzzy_optional": sorted(fuzzy_opt),
        },
    }

    logger.info(
        f"Score: {score}% | "
        f"Required: {len(matched_req)}/{total_req} | "
        f"Optional: {len(matched_opt)}/{total_opt}"
    )

    return result