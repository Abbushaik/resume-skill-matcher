"""
Unit Tests for Resume Skill Matcher.
Run with: pytest tests/ -v
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from matcher.synonym_map import normalize_skill
from matcher.scoring import calculate_match


# ──────────────────────────────────────────────────────────────────────────────
# Test: Synonym Normalization
# ──────────────────────────────────────────────────────────────────────────────
class TestSynonymMap:

    def test_spring_boot_normalizes(self):
        assert normalize_skill("spring boot") == "springboot"

    def test_nodejs_variants(self):
        assert normalize_skill("node.js") == "nodejs"
        assert normalize_skill("node js") == "nodejs"
        assert normalize_skill("node") == "nodejs"

    def test_react_variants(self):
        assert normalize_skill("reactjs") == "react"
        assert normalize_skill("react.js") == "react"

    def test_expressjs_variants(self):
        assert normalize_skill("express") == "expressjs"
        assert normalize_skill("express.js") == "expressjs"
        assert normalize_skill("express js") == "expressjs"

    def test_git_variants(self):
        assert normalize_skill("github") == "git"
        assert normalize_skill("gitlab") == "git"
        assert normalize_skill("version control") == "git"

    def test_rest_api_variants(self):
        assert normalize_skill("restful") == "rest api"
        assert normalize_skill("restful api") == "rest api"
        assert normalize_skill("rest") == "rest api"

    def test_cicd_variants(self):
        assert normalize_skill("ci cd") == "ci/cd"
        assert normalize_skill("cicd") == "ci/cd"
        assert normalize_skill("github actions") == "ci/cd"

    def test_unknown_skill_returns_as_is(self):
        assert normalize_skill("solidity") == "solidity"

    def test_lowercase_normalization(self):
        assert normalize_skill("Spring Boot") == "springboot"
        assert normalize_skill("REACTJS") == "react"


# ──────────────────────────────────────────────────────────────────────────────
# Test: Scoring Engine
# ──────────────────────────────────────────────────────────────────────────────
class TestScoring:

    def test_perfect_match_returns_100(self):
        candidate = ["python", "sql", "git", "linux", "rest api"]
        required  = ["python", "sql", "git", "linux", "rest api"]
        result = calculate_match(candidate, required, [])
        assert result["match_percentage"] == 100.0

    def test_zero_match_returns_0(self):
        candidate = ["java", "spring"]
        required  = ["python", "sql", "docker"]
        optional  = ["react", "redis"]
        result = calculate_match(candidate, required, optional)
        assert result["match_percentage"] == 0.0

    def test_partial_required_match(self):
        candidate = ["python", "sql"]
        required  = ["python", "sql", "git", "linux", "rest api"]
        result = calculate_match(candidate, required, [])
        expected = round((2 * 0.70) / (5 * 0.70) * 100, 2)
        assert result["match_percentage"] == expected

    def test_optional_skills_boost_score(self):
        # Same required skills but one has optional matches
        without_opt = calculate_match(
            ["python", "sql", "git", "linux", "rest api"],
            ["python", "sql", "git", "linux", "rest api"],
            ["docker", "redis", "aws"]
        )
        with_opt = calculate_match(
            ["python", "sql", "git", "linux", "rest api", "docker"],
            ["python", "sql", "git", "linux", "rest api"],
            ["docker", "redis", "aws"]
        )
        assert with_opt["match_percentage"] > without_opt["match_percentage"]

    def test_required_weighted_more_than_optional(self):
        # 5/5 required 0/3 optional vs 0/5 required 3/3 optional
        all_req = calculate_match(
            ["python", "sql", "git", "linux", "rest api"],
            ["python", "sql", "git", "linux", "rest api"],
            ["docker", "redis", "aws"]
        )
        all_opt = calculate_match(
            ["docker", "redis", "aws"],
            ["python", "sql", "git", "linux", "rest api"],
            ["docker", "redis", "aws"]
        )
        assert all_req["match_percentage"] > all_opt["match_percentage"]

    def test_missing_skills_reported_correctly(self):
        candidate = ["python", "sql"]
        required  = ["python", "sql", "git"]
        optional  = ["docker"]
        result = calculate_match(candidate, required, optional)
        assert "git" in result["missing_required"]
        assert "docker" in result["missing_optional"]

    def test_matched_skills_reported_correctly(self):
        candidate = ["python", "sql"]
        required  = ["python", "sql", "git"]
        result = calculate_match(candidate, required, [])
        assert "python" in result["matched_required"]
        assert "sql" in result["matched_required"]

    def test_empty_candidate_returns_0(self):
        result = calculate_match([], ["python", "sql"], ["docker"])
        assert result["match_percentage"] == 0.0

    def test_empty_role_returns_0(self):
        result = calculate_match(["python", "sql"], [], [])
        assert result["match_percentage"] == 0.0

    def test_fuzzy_match_catches_typo(self):
        # 'pythonn' should fuzzy match to 'python'
        candidate = ["pythonn", "sql", "git", "linux", "rest api"]
        required  = ["python", "sql", "git", "linux", "rest api"]
        result = calculate_match(candidate, required, [])
        assert result["match_percentage"] == 100.0

    def test_all_result_keys_present(self):
        result = calculate_match(["python"], ["python", "sql"], ["docker"])
        expected_keys = [
            "match_percentage",
            "matched_required",
            "matched_optional",
            "missing_required",
            "missing_optional",
            "total_required",
            "total_optional",
            "match_strategy_breakdown",
        ]
        for key in expected_keys:
            assert key in result

    def test_strategy_breakdown_present(self):
        result = calculate_match(["python", "sql"], ["python", "sql"], [])
        breakdown = result["match_strategy_breakdown"]
        assert "exact_required" in breakdown
        assert "fuzzy_required" in breakdown
        assert "exact_optional" in breakdown
        assert "fuzzy_optional" in breakdown