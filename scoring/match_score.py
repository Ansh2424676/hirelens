"""
scoring/match_score.py

Calculates the Resume-to-Job Match Percentage: a weighted overlap between
the skill keywords detected in a resume and those detected in a job
description using Day 4's keyword extractor.

Keywords that appear near priority phrasing in the job description
(e.g. "required", "must have", "proficient in") are weighted higher.

Public contract:
    calculate_match_score(resume_text: str, jd_text: str) -> dict

Returns:
    {
        "match_percent": int,
        "matched_keywords": list[str],
        "missing_keywords": list[str],
        "total_jd_keywords": int,
    }

Pure function. No I/O, no external dependencies.
"""

import re

from scoring.keyword_extractor import extract_keywords


# ---------------------------------------------------------------------------
# Priority phrases
# ---------------------------------------------------------------------------

_PRIORITY_PHRASES = [
    "required",
    "must have",
    "must-have",
    "must possess",
    "proficient in",
    "proficiency in",
    "hands-on experience",
    "hands on experience",
    "strong knowledge of",
    "strong experience in",
    "expertise in",
    "mandatory",
    "essential",
    "minimum qualification",
]

_PRIORITY_WEIGHT = 2
_BASE_WEIGHT = 1

_SENTENCE_SPLIT_PATTERN = re.compile(r"(?<=[.!?\n])\s+")


def _compute_jd_keyword_weights(
    jd_text: str,
    jd_keywords: set[str],
) -> dict[str, int]:
    """
    Assign each JD keyword a weight of 1 (base) or 2 (priority), based on
    whether it appears in a sentence containing priority phrasing.
    """

    weights = {
        keyword: _BASE_WEIGHT
        for keyword in jd_keywords
    }

    sentences = _SENTENCE_SPLIT_PATTERN.split(jd_text or "")

    for sentence in sentences:
        lowered = sentence.lower()

        if any(
            phrase in lowered
            for phrase in _PRIORITY_PHRASES
        ):
            sentence_keywords = extract_keywords(sentence)

            for keyword in sentence_keywords:
                if keyword in weights:
                    weights[keyword] = _PRIORITY_WEIGHT

    return weights


def calculate_match_score(
    resume_text: str,
    jd_text: str,
) -> dict:
    """
    Calculate the weighted Resume-to-JD Match Percentage.

    If the job description contains no detectable dictionary keywords,
    match_percent is 0 rather than dividing by zero.
    """

    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(jd_text)

    if not jd_keywords:
        return {
            "match_percent": 0,
            "matched_keywords": [],
            "missing_keywords": [],
            "total_jd_keywords": 0,
        }

    weights = _compute_jd_keyword_weights(
        jd_text,
        jd_keywords,
    )

    matched_keywords = jd_keywords & resume_keywords
    missing_keywords = jd_keywords - resume_keywords

    total_weighted = sum(
        weights[keyword]
        for keyword in jd_keywords
    )

    matched_weighted = sum(
        weights[keyword]
        for keyword in matched_keywords
    )

    match_percent = (
        round(
            (matched_weighted / total_weighted) * 100
        )
        if total_weighted
        else 0
    )

    return {
        "match_percent": match_percent,
        "matched_keywords": sorted(matched_keywords),
        "missing_keywords": sorted(missing_keywords),
        "total_jd_keywords": len(jd_keywords),
    }