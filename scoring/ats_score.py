"""
scoring/ats_score.py

Calculates the ATS Compatibility Score: a structural quality score (0-100)
for a resume, independent of any specific job description.

Public contract:
    calculate_ats_score(resume_text: str) -> dict

Returns:
    {
        "score": int,
        "breakdown": [
            {
                "factor": str,
                "points": int,
                "max_points": int,
                "note": str,
            },
            ...
        ],
    }

Pure function. No I/O, no external dependencies.
"""

import re


# ---------------------------------------------------------------------------
# Section header patterns
# ---------------------------------------------------------------------------

_SECTION_PATTERNS = {
    "Experience section": re.compile(
        r"\b(work experience|professional experience|experience|"
        r"employment history|work history)\b",
        re.IGNORECASE,
    ),
    "Education section": re.compile(
        r"\b(education|academic background|educational qualifications|"
        r"qualifications)\b",
        re.IGNORECASE,
    ),
    "Skills section": re.compile(
        r"\b(skills|technical skills|core competencies|key skills)\b",
        re.IGNORECASE,
    ),
    "Projects section": re.compile(
        r"\b(projects|personal projects|academic projects|key projects)\b",
        re.IGNORECASE,
    ),
}

_POINTS_PER_SECTION = 7


# ---------------------------------------------------------------------------
# Contact info patterns
# ---------------------------------------------------------------------------

_EMAIL_PATTERN = re.compile(
    r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+"
)

_PHONE_PATTERN = re.compile(
    r"(\+?\d{1,3}[\s.-]?)?"
    r"(\(?\d{3,5}\)?[\s.-]?){2,3}"
    r"\d{3,4}"
)

_EMAIL_POINTS = 8
_PHONE_POINTS = 8


# ---------------------------------------------------------------------------
# Bullet point detection
# ---------------------------------------------------------------------------

_BULLET_PATTERN = re.compile(
    r"^[ \t]*[•▪●◦‣·\-\*]\s+",
    re.MULTILINE,
)

_BULLET_POINTS = 12


# ---------------------------------------------------------------------------
# Length check
# ---------------------------------------------------------------------------

_LENGTH_POINTS = 16


# ---------------------------------------------------------------------------
# Clean extraction check
# ---------------------------------------------------------------------------

_EXTRACTION_POINTS = 16


# ---------------------------------------------------------------------------
# Special character / layout artifact check
# ---------------------------------------------------------------------------

_ALLOWED_PUNCTUATION = set(".,;:!?()-'\"/@&%+#\n\t ")
_ARTIFACT_POINTS = 12


def _check_sections(text: str) -> tuple[int, dict]:
    points = 0
    found = []
    missing = []

    for label, pattern in _SECTION_PATTERNS.items():
        if pattern.search(text):
            points += _POINTS_PER_SECTION
            found.append(label)
        else:
            missing.append(label)

    max_points = _POINTS_PER_SECTION * len(_SECTION_PATTERNS)

    if missing:
        note = (
            f"Found: {', '.join(found) or 'none'}. "
            f"Missing: {', '.join(missing)}."
        )
    else:
        note = "All standard section headers detected."

    return points, {
        "factor": "Standard section headers",
        "points": points,
        "max_points": max_points,
        "note": note,
    }


def _check_contact_info(text: str) -> tuple[int, dict]:
    points = 0
    found = []
    missing = []

    if _EMAIL_PATTERN.search(text):
        points += _EMAIL_POINTS
        found.append("email")
    else:
        missing.append("email")

    if _PHONE_PATTERN.search(text):
        points += _PHONE_POINTS
        found.append("phone number")
    else:
        missing.append("phone number")

    if missing:
        note = (
            f"Detected: {', '.join(found) or 'none'}. "
            f"Not detected: {', '.join(missing)}."
        )
    else:
        note = "Email and phone number both detected."

    return points, {
        "factor": "Detectable contact info",
        "points": points,
        "max_points": _EMAIL_POINTS + _PHONE_POINTS,
        "note": note,
    }


def _check_length(text: str) -> tuple[int, dict]:
    word_count = len(text.split())

    if 200 <= word_count <= 1200:
        points = _LENGTH_POINTS
        note = (
            f"Resume length ({word_count} words) is in the ideal range."
        )
    elif 100 <= word_count < 200 or 1200 < word_count <= 1800:
        points = _LENGTH_POINTS // 2
        note = (
            f"Resume length ({word_count} words) is a bit outside "
            "the ideal range."
        )
    else:
        points = 0

        if word_count < 100:
            note = (
                f"Resume is too short ({word_count} words) — "
                "ATS may flag it as thin content."
            )
        else:
            note = (
                f"Resume is too long ({word_count} words) — "
                "consider trimming."
            )

    return points, {
        "factor": "Reasonable resume length",
        "points": points,
        "max_points": _LENGTH_POINTS,
        "note": note,
    }


def _check_clean_extraction(text: str) -> tuple[int, dict]:
    total_chars = len(text) or 1
    alpha_chars = sum(char.isalpha() for char in text)
    alpha_ratio = alpha_chars / total_chars

    if alpha_ratio >= 0.5:
        points = _EXTRACTION_POINTS
        note = "Text extracted cleanly with no signs of parsing failure."
    elif alpha_ratio >= 0.3:
        points = _EXTRACTION_POINTS // 2
        note = (
            "Some signs of messy extraction "
            "(low readable-text ratio)."
        )
    else:
        points = 0
        note = (
            "Text extraction looks unreliable — resume may use "
            "a complex layout."
        )

    return points, {
        "factor": "No parsing-failure evidence",
        "points": points,
        "max_points": _EXTRACTION_POINTS,
        "note": note,
    }


def _check_bullets(text: str) -> tuple[int, dict]:
    matches = _BULLET_PATTERN.findall(text)
    bullet_count = len(matches)

    if bullet_count >= 3:
        points = _BULLET_POINTS
        note = f"{bullet_count} bullet points detected."
    elif bullet_count >= 1:
        points = _BULLET_POINTS // 2
        note = (
            f"Only {bullet_count} bullet point(s) detected — "
            "consider using more."
        )
    else:
        points = 0
        note = (
            "No bullet points detected — ATS and recruiters favor "
            "scannable bullets."
        )

    return points, {
        "factor": "Bullet point usage",
        "points": points,
        "max_points": _BULLET_POINTS,
        "note": note,
    }


def _check_artifacts(text: str) -> tuple[int, dict]:
    total_chars = len(text) or 1

    special_count = sum(
        1
        for char in text
        if not char.isalnum()
        and char not in _ALLOWED_PUNCTUATION
    )

    special_ratio = special_count / total_chars

    if special_ratio < 0.02:
        points = _ARTIFACT_POINTS
        note = "No significant layout artifacts detected."
    elif special_ratio < 0.05:
        points = _ARTIFACT_POINTS // 2
        note = (
            "Some unusual characters detected — may indicate "
            "table/column layout."
        )
    else:
        points = 0
        note = (
            "High density of unusual characters — likely a "
            "table/column-based layout ATS struggles with."
        )

    return points, {
        "factor": "Absence of layout artifacts",
        "points": points,
        "max_points": _ARTIFACT_POINTS,
        "note": note,
    }


def calculate_ats_score(resume_text: str) -> dict:
    """
    Calculate the ATS Compatibility Score (0-100) for a resume.

    Empty or whitespace-only input returns a score of 0 with a
    breakdown explaining every factor failed.
    """

    text = resume_text or ""

    checks = [
        _check_sections,
        _check_contact_info,
        _check_length,
        _check_clean_extraction,
        _check_bullets,
        _check_artifacts,
    ]

    breakdown = []
    total_points = 0

    if not text.strip():
        for check_fn in checks:
            _, entry = check_fn("")
            entry["points"] = 0
            entry["note"] = "No resume text was provided."
            breakdown.append(entry)

        return {
            "score": 0,
            "breakdown": breakdown,
        }

    for check_fn in checks:
        points, entry = check_fn(text)
        total_points += points
        breakdown.append(entry)

    score = max(0, min(100, round(total_points)))

    return {
        "score": score,
        "breakdown": breakdown,
    }