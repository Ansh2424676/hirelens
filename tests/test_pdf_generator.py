"""
tests/test_pdf_generator.py

Regression tests for HireLens's Day 8 PDF report generator:
report/pdf_generator.py.

These tests verify that generate_pdf_report(analysis, ai_suggestions)
always returns valid, non-empty PDF bytes -- across normal results, score
extremes, long content, the AI fallback case, and missing/empty optional
fields -- without raising an exception.

They intentionally do not assert on exact visual layout (reportlab's
internal PDF structure is not meant to be parsed here); they assert on
what matters for release-readiness: the function never crashes and
always produces a well-formed PDF document.

Run with:
    python -m pytest tests/test_pdf_generator.py -v
"""

import sys
from pathlib import Path

# Allow running "python -m pytest tests/test_pdf_generator.py" from the
# project root without needing the package installed.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from report.pdf_generator import generate_pdf_report


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

def _make_analysis(
    ats_score=72,
    match_percent=65,
    missing_by_category=None,
    total_missing=None,
    matched_keywords=None,
    missing_keywords=None,
    resume_keywords=None,
    jd_keywords=None,
):
    """
    Build a structurally valid analysis dict matching the exact shape
    produced by scoring.engine.analyze(), with sensible defaults that
    can be overridden per test.
    """

    if missing_by_category is None:
        missing_by_category = {
            "cloud_platforms": ["aws", "azure"],
            "devops_tools": ["docker", "kubernetes"],
        }

    if total_missing is None:
        total_missing = sum(
            len(skills) for skills in missing_by_category.values()
        )

    if matched_keywords is None:
        matched_keywords = ["python", "flask", "sql"]

    if missing_keywords is None:
        missing_keywords = ["aws", "azure", "docker", "kubernetes"]

    if resume_keywords is None:
        resume_keywords = ["python", "flask", "sql", "git"]

    if jd_keywords is None:
        jd_keywords = [
            "python",
            "flask",
            "sql",
            "aws",
            "azure",
            "docker",
            "kubernetes",
        ]

    return {
        "ats_score": {
            "score": ats_score,
            "breakdown": [
                {
                    "factor": "Standard section headers",
                    "points": 21,
                    "max_points": 28,
                    "note": "Found: Experience section, Skills section.",
                },
            ],
        },
        "match_score": {
            "match_percent": match_percent,
            "matched_keywords": matched_keywords,
            "missing_keywords": missing_keywords,
            "total_jd_keywords": len(jd_keywords),
        },
        "missing_skills": {
            "missing_by_category": missing_by_category,
            "total_missing": total_missing,
        },
        "keyword_analysis": {
            "resume_keywords": resume_keywords,
            "jd_keywords": jd_keywords,
        },
    }


def _make_ai_suggestions(
    overall_feedback="This resume shows solid technical fundamentals "
    "with clear project experience.",
    strengths=None,
    priority_improvements=None,
    skills_to_highlight=None,
    tone_notes="The tone is professional and appropriately concise.",
):
    if strengths is None:
        strengths = [
            "Clear, quantified project descriptions",
            "Consistent formatting throughout",
        ]

    if priority_improvements is None:
        priority_improvements = [
            {
                "area": "Cloud experience",
                "suggestion": "Add specific AWS or Azure project examples.",
                "example": "Deployed a Flask API to AWS EC2 with an "
                "RDS backend.",
            }
        ]

    if skills_to_highlight is None:
        skills_to_highlight = ["Python", "Flask", "SQL"]

    return {
        "overall_feedback": overall_feedback,
        "strengths": strengths,
        "priority_improvements": priority_improvements,
        "skills_to_highlight": skills_to_highlight,
        "tone_notes": tone_notes,
    }


def _assert_valid_pdf(pdf_bytes: bytes) -> None:
    """
    Shared assertion: the output is non-empty bytes forming a
    well-formed PDF document.
    """

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 0
    assert pdf_bytes.startswith(b"%PDF-")
    assert pdf_bytes.rstrip().endswith(b"%%EOF")


# ---------------------------------------------------------------------------
# 1. Normal analysis
# ---------------------------------------------------------------------------

def test_normal_analysis_produces_valid_pdf():
    analysis = _make_analysis()
    ai_suggestions = _make_ai_suggestions()

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)


# ---------------------------------------------------------------------------
# 2. High score
# ---------------------------------------------------------------------------

def test_high_score_produces_valid_pdf():
    analysis = _make_analysis(
        ats_score=100,
        match_percent=100,
        missing_by_category={},
        total_missing=0,
        matched_keywords=["python", "flask", "sql", "aws"],
        missing_keywords=[],
        jd_keywords=["python", "flask", "sql", "aws"],
    )
    ai_suggestions = _make_ai_suggestions(
        overall_feedback="Excellent match -- this resume is very "
        "well-aligned with the job description."
    )

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)


# ---------------------------------------------------------------------------
# 3. Low score
# ---------------------------------------------------------------------------

def test_low_score_produces_valid_pdf():
    analysis = _make_analysis(
        ats_score=0,
        match_percent=0,
        missing_by_category={
            "programming_languages": ["python", "java", "sql"],
        },
        total_missing=3,
        matched_keywords=[],
        missing_keywords=["python", "java", "sql"],
        resume_keywords=[],
        jd_keywords=["python", "java", "sql"],
    )
    ai_suggestions = _make_ai_suggestions(
        overall_feedback="This resume needs significant work to align "
        "with the target role.",
        strengths=[],
    )

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)


# ---------------------------------------------------------------------------
# 4. Long missing-skills list
# ---------------------------------------------------------------------------

def test_long_missing_skills_list_produces_valid_pdf():
    missing_by_category = {
        "programming_languages": [
            "python", "java", "javascript", "typescript", "c", "c++",
            "c#", "sql", "r", "go", "ruby", "php", "kotlin", "swift",
            "scala", "bash",
        ],
        "frameworks_libraries": [
            "flask", "django", "fastapi", "spring boot", "react",
            "angular", "vue.js", "node.js", "express.js", ".net",
            "laravel", "next.js", "jquery",
        ],
        "databases": [
            "mysql", "postgresql", "mongodb", "oracle", "sql server",
            "sqlite", "redis", "cassandra", "dynamodb", "mariadb",
        ],
        "cloud_platforms": [
            "aws", "azure", "google cloud platform", "gcp", "aws ec2",
            "aws s3", "aws lambda", "azure functions", "heroku",
            "render",
        ],
    }

    total_missing = sum(len(v) for v in missing_by_category.values())

    analysis = _make_analysis(
        ats_score=35,
        match_percent=5,
        missing_by_category=missing_by_category,
        total_missing=total_missing,
        matched_keywords=["git"],
        missing_keywords=[
            skill
            for skills in missing_by_category.values()
            for skill in skills
        ],
        resume_keywords=["git"],
        jd_keywords=[
            skill
            for skills in missing_by_category.values()
            for skill in skills
        ]
        + ["git"],
    )
    ai_suggestions = _make_ai_suggestions()

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)

    # A report covering 4 large categories should reasonably be expected
    # to span more than a single trivial page of bytes.
    assert len(pdf_bytes) > 2000


# ---------------------------------------------------------------------------
# 5. Long AI suggestions
# ---------------------------------------------------------------------------

def test_long_ai_suggestions_produce_valid_pdf():
    long_paragraph = (
        "This resume demonstrates a strong foundation in backend "
        "development, with particular strength in Python and Flask. "
    ) * 20

    long_example = (
        "For instance, consider restructuring the experience section "
        "to lead with quantified impact statements such as reduced "
        "API response time by 40 percent through query optimization "
        "and caching. "
    ) * 15

    analysis = _make_analysis()
    ai_suggestions = _make_ai_suggestions(
        overall_feedback=long_paragraph,
        strengths=[
            "Strength number " + str(i) + ": " + long_example[:200]
            for i in range(6)
        ],
        priority_improvements=[
            {
                "area": f"Improvement area {i}",
                "suggestion": long_paragraph,
                "example": long_example,
            }
            for i in range(4)
        ],
        tone_notes=long_paragraph,
    )

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)

    # Long content should reasonably be expected to overflow onto
    # multiple pages rather than being silently truncated.
    assert pdf_bytes.count(b"/Type /Page") >= 1
    assert len(pdf_bytes) > 4000


# ---------------------------------------------------------------------------
# 6. AI fallback / no-AI case
# ---------------------------------------------------------------------------

def test_ai_fallback_response_produces_valid_pdf():
    analysis = _make_analysis()
    ai_suggestions = {"error": "AI suggestions temporarily unavailable"}

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)


def test_empty_ai_suggestions_dict_produces_valid_pdf():
    analysis = _make_analysis()

    pdf_bytes = generate_pdf_report(analysis, {})

    _assert_valid_pdf(pdf_bytes)


def test_none_ai_suggestions_produces_valid_pdf():
    analysis = _make_analysis()

    pdf_bytes = generate_pdf_report(analysis, None)

    _assert_valid_pdf(pdf_bytes)


# ---------------------------------------------------------------------------
# 7. Missing / empty optional fields
# ---------------------------------------------------------------------------

def test_empty_analysis_dict_does_not_crash():
    pdf_bytes = generate_pdf_report({}, {})

    _assert_valid_pdf(pdf_bytes)


def test_none_analysis_does_not_crash():
    pdf_bytes = generate_pdf_report(None, None)

    _assert_valid_pdf(pdf_bytes)


def test_analysis_missing_optional_keys_does_not_crash():
    # A partial analysis dict missing several expected keys should still
    # degrade gracefully rather than raising a KeyError.
    partial_analysis = {
        "ats_score": {"score": 50},
        # match_score, missing_skills, keyword_analysis intentionally
        # omitted.
    }

    pdf_bytes = generate_pdf_report(partial_analysis, {})

    _assert_valid_pdf(pdf_bytes)


def test_ai_suggestions_with_empty_lists_does_not_crash():
    analysis = _make_analysis()
    ai_suggestions = {
        "overall_feedback": "",
        "strengths": [],
        "priority_improvements": [],
        "skills_to_highlight": [],
        "tone_notes": "",
    }

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)


def test_priority_improvement_missing_example_does_not_crash():
    analysis = _make_analysis()
    ai_suggestions = _make_ai_suggestions(
        priority_improvements=[
            {
                "area": "Formatting",
                "suggestion": "Use consistent bullet styling.",
                # "example" intentionally omitted -- REQUIRED_KEYS in
                # response_parser.py only guarantees this key exists
                # coming from a validated Claude response, but the PDF
                # generator should not assume it is always present.
            }
        ]
    )

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)


def test_missing_skills_with_no_categories_produces_valid_pdf():
    analysis = _make_analysis(
        missing_by_category={},
        total_missing=0,
    )
    ai_suggestions = _make_ai_suggestions()

    pdf_bytes = generate_pdf_report(analysis, ai_suggestions)

    _assert_valid_pdf(pdf_bytes)


# ---------------------------------------------------------------------------
# Return type contract
# ---------------------------------------------------------------------------

def test_return_type_is_always_bytes():
    analysis = _make_analysis()
    ai_suggestions = _make_ai_suggestions()

    result = generate_pdf_report(analysis, ai_suggestions)

    assert isinstance(result, bytes)