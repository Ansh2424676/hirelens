"""
tests/test_scoring.py

Regression tests for HireLens's Day 5 rule-based scoring engine:
scoring/ats_score.py, scoring/match_score.py, scoring/missing_skills.py,
and scoring/engine.py.

These are simple assertion-based sanity tests with hardcoded input/output
expectations, per the Day 5 Blueprint. They guard against future
regressions -- if a future change to the scoring logic breaks one of
these, that's a signal the change needs review, not necessarily that it's
wrong.

Run with:
    python -m pytest tests/test_scoring.py -v
"""

import sys
from pathlib import Path

# Allow running "python -m pytest tests/test_scoring.py" from the project
# root without needing the package installed.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scoring.ats_score import calculate_ats_score
from scoring.match_score import calculate_match_score
from scoring.missing_skills import detect_missing_skills
from scoring.engine import analyze


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

STRONG_RESUME = """
Ansh Gupta
ansh.gupta@email.com | +91 9876543210

Experience

- Data Analyst Intern at PySpiders using Python, SQL, Power BI
- Built dashboards and automated reports using Excel and Pandas
- Performed data cleaning and data wrangling on large datasets
- Collaborated with cross-functional teams on stakeholder communication

Education
MCA, Kanpur Institute of Technology

Skills
Python, SQL, Power BI, Flask, Machine Learning, Excel, Pandas, Numpy

Projects

- Built HireLens, a resume analyzer using Flask and Python
- Built a data visualization dashboard using Tableau
- Automated an ETL pipeline for reporting
"""

STRONG_JD = """
We are looking for a Data Analyst with strong experience in Python, SQL,
and Power BI. The candidate must have proficiency in Excel and Pandas for
data cleaning and analysis. Experience with Tableau is required. Knowledge
of machine learning is a plus. Familiarity with AWS and Docker is a bonus
but not mandatory. Strong communication and stakeholder communication
skills are required.
"""

UNRELATED_JD = """
We are hiring a Civil Engineer with expertise in structural design,
AutoCAD, and construction project management. Must have experience with
concrete technology, surveying, and site supervision. Knowledge of
building codes and safety regulations is required.
"""

MINIMAL_RESUME = (
    "hi there just some random words with no real structure at all"
)


# ---------------------------------------------------------------------------
# ATS Compatibility Score tests
# ---------------------------------------------------------------------------

def test_ats_score_strong_resume_scores_high():
    result = calculate_ats_score(STRONG_RESUME)

    assert result["score"] >= 80
    assert len(result["breakdown"]) == 6


def test_ats_score_empty_resume_scores_zero():
    result = calculate_ats_score("")

    assert result["score"] == 0
    assert all(
        item["points"] == 0
        for item in result["breakdown"]
    )


def test_ats_score_none_resume_does_not_crash():
    result = calculate_ats_score(None)

    assert result["score"] == 0


def test_ats_score_minimal_resume_scores_low():
    result = calculate_ats_score(MINIMAL_RESUME)
    strong_result = calculate_ats_score(STRONG_RESUME)

    # A structureless blob of text should score meaningfully lower than a
    # well-structured resume.
    assert result["score"] < strong_result["score"]
    assert result["score"] <= 40


def test_ats_score_breakdown_points_sum_to_score():
    result = calculate_ats_score(STRONG_RESUME)
    total = sum(
        item["points"]
        for item in result["breakdown"]
    )

    assert total == result["score"]


# ---------------------------------------------------------------------------
# Match Percentage tests
# ---------------------------------------------------------------------------

def test_match_score_strong_pair_scores_high():
    result = calculate_match_score(
        STRONG_RESUME,
        STRONG_JD,
    )

    assert result["match_percent"] >= 70
    assert "python" in result["matched_keywords"]
    assert "power bi" in result["matched_keywords"]


def test_match_score_unrelated_pair_scores_zero():
    result = calculate_match_score(
        STRONG_RESUME,
        UNRELATED_JD,
    )

    assert result["match_percent"] == 0
    assert result["matched_keywords"] == []


def test_match_score_empty_jd_returns_zero_not_crash():
    result = calculate_match_score(
        STRONG_RESUME,
        "",
    )

    assert result["match_percent"] == 0
    assert result["total_jd_keywords"] == 0


def test_match_score_empty_resume_returns_zero_not_crash():
    result = calculate_match_score(
        "",
        STRONG_JD,
    )

    assert result["match_percent"] == 0
    assert result["matched_keywords"] == []


def test_match_score_priority_phrase_weighting_increases_match():
    # A JD keyword mentioned as "required"/"must have" is weighted higher
    # than one mentioned only in passing.
    jd = (
        "Python experience is required for this role. "
        "Some familiarity with Ruby would also be nice to have "
        "if the candidate has time to learn it eventually."
    )

    resume_matches_priority = (
        "I have three years of Python experience."
    )
    resume_matches_casual = (
        "I have three years of Ruby experience."
    )

    priority_result = calculate_match_score(
        resume_matches_priority,
        jd,
    )

    casual_result = calculate_match_score(
        resume_matches_casual,
        jd,
    )

    assert (
        priority_result["match_percent"]
        > casual_result["match_percent"]
    )


# ---------------------------------------------------------------------------
# Missing Skills tests
# ---------------------------------------------------------------------------

def test_missing_skills_grouped_by_category():
    result = detect_missing_skills(
        STRONG_RESUME,
        STRONG_JD,
    )

    assert "cloud_platforms" in result["missing_by_category"]
    assert (
        "aws"
        in result["missing_by_category"]["cloud_platforms"]
    )

    assert result["total_missing"] == sum(
        len(skills)
        for skills in result["missing_by_category"].values()
    )


def test_missing_skills_none_when_resume_covers_everything():
    result = detect_missing_skills(
        STRONG_JD,
        STRONG_JD,
    )

    assert result["missing_by_category"] == {}
    assert result["total_missing"] == 0


def test_missing_skills_empty_inputs_do_not_crash():
    result = detect_missing_skills(
        "",
        "",
    )

    assert result["missing_by_category"] == {}
    assert result["total_missing"] == 0


# ---------------------------------------------------------------------------
# Engine (orchestrator) integration tests
# ---------------------------------------------------------------------------

def test_engine_returns_all_expected_top_level_keys():
    result = analyze(
        STRONG_RESUME,
        STRONG_JD,
    )

    assert set(result.keys()) == {
        "ats_score",
        "match_score",
        "missing_skills",
        "keyword_analysis",
    }


def test_engine_strong_pair_outscores_unrelated_pair():
    strong_result = analyze(
        STRONG_RESUME,
        STRONG_JD,
    )

    unrelated_result = analyze(
        STRONG_RESUME,
        UNRELATED_JD,
    )

    assert (
        strong_result["match_score"]["match_percent"]
        > unrelated_result["match_score"]["match_percent"]
    )


def test_engine_keyword_analysis_consistent_with_match_score():
    result = analyze(
        STRONG_RESUME,
        STRONG_JD,
    )

    assert (
        len(result["keyword_analysis"]["jd_keywords"])
        == result["match_score"]["total_jd_keywords"]
    )


def test_engine_handles_completely_empty_input_without_crashing():
    result = analyze(
        "",
        "",
    )

    assert result["ats_score"]["score"] == 0
    assert result["match_score"]["match_percent"] == 0
    assert result["missing_skills"]["total_missing"] == 0
    assert result["keyword_analysis"]["resume_keywords"] == []
    assert result["keyword_analysis"]["jd_keywords"] == []