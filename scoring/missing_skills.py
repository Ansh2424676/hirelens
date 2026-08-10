"""
scoring/missing_skills.py

Detects which job-description skill keywords are absent from the resume,
and groups them by SKILLS_DB category so the output is readable rather
than a flat, overwhelming list.

Public contract:
    detect_missing_skills(resume_text: str, jd_text: str) -> dict

Returns:
    {
        "missing_by_category": {
            "programming_languages": [...],
            "tools_platforms": [...],
            ...
        },
        "total_missing": int,
    }

Pure function. No I/O, no external dependencies.
"""

from scoring.keyword_extractor import extract_keywords
from scoring.skills_dictionary import SKILLS_DB


def _group_missing_by_category(
    missing_keywords: set[str],
) -> dict[str, list[str]]:
    """
    Group a set of missing canonical skill names by their SKILLS_DB
    category. Categories with no missing skills are omitted entirely.
    """

    grouped = {}

    for category, terms in SKILLS_DB.items():
        category_missing = sorted(
            term
            for term in terms
            if term in missing_keywords
        )

        if category_missing:
            grouped[category] = category_missing

    return grouped


def detect_missing_skills(
    resume_text: str,
    jd_text: str,
) -> dict:
    """
    Detect JD skill keywords missing from the resume,
    grouped by category.
    """

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    missing_keywords = jd_keywords - resume_keywords

    return {
        "missing_by_category": _group_missing_by_category(
            missing_keywords
        ),
        "total_missing": len(missing_keywords),
    }