"""
scoring/engine.py

Single orchestrating entry point for HireLens's rule-based scoring engine.
Combines the ATS Compatibility Score, Match Percentage, Missing Skills, and
raw keyword analysis into one structured result object.

This is the function the Flask route calls. Everything downstream (the AI
suggestion layer on Day 6, the PDF report generator on Day 8) consumes this
single structured dict.

Public contract:
    analyze(resume_text: str, jd_text: str) -> dict

Returns:
    {
        "ats_score": {...},
        "match_score": {...},
        "missing_skills": {...},
        "keyword_analysis": {
            "resume_keywords": list[str],
            "jd_keywords": list[str],
        },
    }

Pure function. No I/O, no external dependencies.
"""

from scoring.ats_score import calculate_ats_score
from scoring.match_score import calculate_match_score
from scoring.missing_skills import detect_missing_skills
from scoring.keyword_extractor import extract_keywords


def analyze(
    resume_text: str,
    jd_text: str,
) -> dict:
    """
    Run the full rule-based scoring pipeline against a resume/JD pair.
    """

    ats_result = calculate_ats_score(resume_text)

    match_result = calculate_match_score(
        resume_text,
        jd_text,
    )

    missing_result = detect_missing_skills(
        resume_text,
        jd_text,
    )

    return {
        "ats_score": ats_result,
        "match_score": match_result,
        "missing_skills": missing_result,
        "keyword_analysis": {
            "resume_keywords": sorted(
                extract_keywords(resume_text)
            ),
            "jd_keywords": sorted(
                extract_keywords(jd_text)
            ),
        },
    }