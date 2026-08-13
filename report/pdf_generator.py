"""
report/pdf_generator.py

Day 8: PDF report generation for HireLens.

Builds a professional, downloadable PDF summarizing a resume analysis
(ATS score, match percentage, missing skills, keyword analysis, and AI
suggestions) using reportlab's Platypus flowable layout engine.

Public contract:
    generate_pdf_report(analysis: dict, ai_suggestions: dict) -> bytes

Consumes the same structured data already produced by
scoring.engine.analyze() and ai_service.claude_provider.ClaudeProvider,
without re-deriving or re-wrangling any of it. Never raises on malformed,
partial, or missing optional data -- every section degrades gracefully
so a report can always be generated.

Pure function except for the in-memory PDF build. No file I/O, no
network calls, no external state.
"""

from datetime import datetime
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


# ---------------------------------------------------------------------------
# Branding (matches static/css/styles.css so the report feels consistent
# with the live dashboard, without touching or redesigning the dashboard).
# ---------------------------------------------------------------------------

_COLOR_TEXT = colors.HexColor("#172033")
_COLOR_MUTED = colors.HexColor("#667085")
_COLOR_ACCENT = colors.HexColor("#3157d5")
_COLOR_BORDER = colors.HexColor("#e5e7eb")
_COLOR_SUCCESS = colors.HexColor("#15803d")
_COLOR_WARNING = colors.HexColor("#b45309")
_COLOR_DANGER = colors.HexColor("#b42318")

_PAGE_MARGIN = 0.75 * inch


def _score_color(value):
    """
    Map a 0-100 score to the same red/yellow/green convention used
    on the live dashboard.
    """

    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return _COLOR_MUTED

    if numeric >= 70:
        return _COLOR_SUCCESS
    if numeric >= 40:
        return _COLOR_WARNING
    return _COLOR_DANGER


def _humanize_category(category: str) -> str:
    """
    Turn a SKILLS_DB category key like "programming_languages" into
    "Programming Languages" for display.
    """

    if not category:
        return "Other"

    return category.replace("_", " ").strip().title()


def _build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["ReportTitle"] = ParagraphStyle(
        "ReportTitle",
        parent=base["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=_COLOR_ACCENT,
        alignment=TA_CENTER,
        spaceAfter=4,
    )

    styles["ReportSubtitle"] = ParagraphStyle(
        "ReportSubtitle",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=10,
        textColor=_COLOR_MUTED,
        alignment=TA_CENTER,
        spaceAfter=18,
    )

    styles["SectionHeading"] = ParagraphStyle(
        "SectionHeading",
        parent=base["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=_COLOR_TEXT,
        spaceBefore=16,
        spaceAfter=8,
    )

    styles["SubHeading"] = ParagraphStyle(
        "SubHeading",
        parent=base["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        textColor=_COLOR_TEXT,
        spaceBefore=8,
        spaceAfter=4,
    )

    styles["Body"] = ParagraphStyle(
        "Body",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=_COLOR_TEXT,
        leading=14,
        alignment=TA_LEFT,
        spaceAfter=6,
        wordWrap="CJK",
    )

    styles["MutedNote"] = ParagraphStyle(
        "MutedNote",
        parent=styles["Body"],
        fontSize=8.5,
        textColor=_COLOR_MUTED,
    )

    styles["ScoreNumber"] = ParagraphStyle(
        "ScoreNumber",
        parent=base["Normal"],
        fontName="Helvetica-Bold",
        fontSize=30,
        leading=36,
        alignment=TA_CENTER,
        spaceAfter=2,
    )

    styles["ScoreCaption"] = ParagraphStyle(
        "ScoreCaption",
        parent=base["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        textColor=_COLOR_MUTED,
        alignment=TA_CENTER,
    )

    styles["BulletItem"] = ParagraphStyle(
        "BulletItem",
        parent=styles["Body"],
        leftIndent=14,
        bulletIndent=2,
        spaceAfter=4,
    )

    styles["Footer"] = ParagraphStyle(
        "Footer",
        parent=base["Normal"],
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=_COLOR_MUTED,
        alignment=TA_CENTER,
        spaceBefore=20,
    )

    return styles


def _safe_text(value, fallback: str = "Not available") -> str:
    """
    Coerce a value into safe, escaped-friendly display text.
    reportlab's Paragraph treats its input as a light markup language,
    so raw values are escaped before being wrapped in tags elsewhere.
    """

    if value is None:
        return fallback

    text = str(value).strip()

    if not text:
        return fallback

    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _build_header(styles: dict) -> list:
    generated_at = datetime.now().strftime("%d %B %Y, %I:%M %p")

    return [
        Paragraph("HireLens", styles["ReportTitle"]),
        Paragraph(
            "AI-Powered Resume Analysis Report",
            styles["ReportSubtitle"],
        ),
        Paragraph(
            f"Generated on {generated_at}",
            styles["MutedNote"],
        ),
        Spacer(1, 6),
        HRFlowable(
            width="100%",
            thickness=1,
            color=_COLOR_BORDER,
            spaceAfter=12,
        ),
    ]


def _build_score_summary(analysis: dict, styles: dict) -> list:
    ats_score = analysis.get("ats_score") or {}
    match_score = analysis.get("match_score") or {}

    ats_value = ats_score.get("score")
    match_value = match_score.get("match_percent")

    ats_display = (
        f"{int(ats_value)}"
        if isinstance(ats_value, (int, float))
        else "N/A"
    )
    match_display = (
        f"{int(match_value)}%"
        if isinstance(match_value, (int, float))
        else "N/A"
    )

    ats_color = _score_color(ats_value)
    match_color = _score_color(match_value)

    ats_number_style = ParagraphStyle(
        "AtsNumber",
        parent=styles["ScoreNumber"],
        textColor=ats_color,
    )
    match_number_style = ParagraphStyle(
        "MatchNumber",
        parent=styles["ScoreNumber"],
        textColor=match_color,
    )

    score_table = Table(
        [
            [
                Paragraph(ats_display, ats_number_style),
                Paragraph(match_display, match_number_style),
            ],
            [
                Paragraph("ATS Compatibility Score", styles["ScoreCaption"]),
                Paragraph("Resume-to-JD Match", styles["ScoreCaption"]),
            ],
        ],
        colWidths=[3.1 * inch, 3.1 * inch],
    )

    score_table.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
                ("TOPPADDING", (0, 1), (-1, 1), 2),
                ("BOTTOMPADDING", (0, 1), (-1, 1), 14),
                ("BOX", (0, 0), (0, -1), 0.75, _COLOR_BORDER),
                ("BOX", (1, 0), (1, -1), 0.75, _COLOR_BORDER),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )

    elements = [
        Paragraph("Score Summary", styles["SectionHeading"]),
        score_table,
    ]

    return elements


def _build_missing_skills(analysis: dict, styles: dict) -> list:
    missing_skills = analysis.get("missing_skills") or {}
    missing_by_category = missing_skills.get("missing_by_category") or {}
    total_missing = missing_skills.get("total_missing", 0)

    elements = [Paragraph("Missing Skills", styles["SectionHeading"])]

    if not missing_by_category or not total_missing:
        elements.append(
            Paragraph(
                "No missing skills detected -- the resume covers every "
                "skill keyword found in the job description.",
                styles["Body"],
            )
        )
        return elements

    elements.append(
        Paragraph(
            f"{_safe_text(total_missing)} skill keyword(s) from the job "
            "description were not found in the resume, grouped by "
            "category below.",
            styles["Body"],
        )
    )

    for category, skills in missing_by_category.items():
        if not skills:
            continue

        elements.append(
            Paragraph(_humanize_category(category), styles["SubHeading"])
        )

        skills_line = ", ".join(_safe_text(skill) for skill in skills)

        elements.append(Paragraph(skills_line, styles["Body"]))

    return elements


def _build_keyword_summary(analysis: dict, styles: dict) -> list:
    keyword_analysis = analysis.get("keyword_analysis") or {}
    match_score = analysis.get("match_score") or {}

    resume_keyword_count = len(keyword_analysis.get("resume_keywords") or [])
    jd_keyword_count = len(keyword_analysis.get("jd_keywords") or [])
    matched_count = len(match_score.get("matched_keywords") or [])
    missing_count = len(match_score.get("missing_keywords") or [])

    summary_rows = [
        ["Keywords found in job description", str(jd_keyword_count)],
        ["Keywords found in resume", str(resume_keyword_count)],
        ["Matched keywords", str(matched_count)],
        ["Missing keywords", str(missing_count)],
    ]

    table = Table(summary_rows, colWidths=[4.2 * inch, 2 * inch])
    table.setStyle(
        TableStyle(
            [
                ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("TEXTCOLOR", (0, 0), (-1, -1), _COLOR_TEXT),
                ("ALIGN", (1, 0), (1, -1), "RIGHT"),
                ("LINEBELOW", (0, 0), (-1, -2), 0.5, _COLOR_BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    return [
        Paragraph("Keyword Analysis Summary", styles["SectionHeading"]),
        table,
    ]


def _build_ai_suggestions(ai_suggestions: dict, styles: dict) -> list:
    elements = [Paragraph("AI-Powered Suggestions", styles["SectionHeading"])]

    suggestions = ai_suggestions or {}

    if not suggestions or "error" in suggestions:
        elements.append(
            Paragraph(
                "AI-powered suggestions were not available for this "
                "report. The score summary, missing skills, and keyword "
                "analysis above are still fully accurate and based on "
                "HireLens's rule-based scoring engine.",
                styles["Body"],
            )
        )
        return elements

    overall_feedback = suggestions.get("overall_feedback")
    strengths = suggestions.get("strengths") or []
    priority_improvements = suggestions.get("priority_improvements") or []
    skills_to_highlight = suggestions.get("skills_to_highlight") or []
    tone_notes = suggestions.get("tone_notes")

    if overall_feedback:
        elements.append(
            Paragraph("Overall Feedback", styles["SubHeading"])
        )
        elements.append(
            Paragraph(_safe_text(overall_feedback), styles["Body"])
        )

    if strengths:
        elements.append(Paragraph("Strengths", styles["SubHeading"]))

        for item in strengths:
            elements.append(
                Paragraph(
                    f"\u2022 {_safe_text(item)}",
                    styles["BulletItem"],
                )
            )

    if priority_improvements:
        elements.append(
            Paragraph("Priority Improvements", styles["SubHeading"])
        )

        for improvement in priority_improvements:
            if not isinstance(improvement, dict):
                continue

            area = _safe_text(improvement.get("area"), fallback="General")
            suggestion = _safe_text(improvement.get("suggestion"))
            example = improvement.get("example")

            elements.append(
                Paragraph(
                    f"<b>{area}</b> &mdash; {suggestion}",
                    styles["Body"],
                )
            )

            if example:
                elements.append(
                    Paragraph(
                        f"<i>Example:</i> {_safe_text(example)}",
                        styles["MutedNote"],
                    )
                )

    if skills_to_highlight:
        elements.append(
            Paragraph("Skills to Highlight", styles["SubHeading"])
        )
        skills_line = ", ".join(
            _safe_text(skill) for skill in skills_to_highlight
        )
        elements.append(Paragraph(skills_line, styles["Body"]))

    if tone_notes:
        elements.append(Paragraph("Tone Notes", styles["SubHeading"]))
        elements.append(Paragraph(_safe_text(tone_notes), styles["Body"]))

    if not any(
        [
            overall_feedback,
            strengths,
            priority_improvements,
            skills_to_highlight,
            tone_notes,
        ]
    ):
        elements.append(
            Paragraph(
                "No AI suggestions were returned for this analysis.",
                styles["Body"],
            )
        )

    return elements


def _build_footer(styles: dict) -> list:
    return [
        HRFlowable(
            width="100%",
            thickness=0.75,
            color=_COLOR_BORDER,
            spaceBefore=18,
        ),
        Paragraph(
            "Generated by HireLens \u2014 AI Job Match & Resume Analyzer "
            "(AB Talks 60-Day Claude AI Challenge Capstone)",
            styles["Footer"],
        ),
    ]


def generate_pdf_report(analysis: dict, ai_suggestions: dict) -> bytes:
    """
    Build a professional PDF report from a HireLens analysis result and
    the corresponding AI suggestions, returning the PDF as raw bytes.

    Both arguments are expected to follow the structures produced by
    scoring.engine.analyze() and ai_service.claude_provider.ClaudeProvider
    .generate_suggestions(), but every section is defensive: missing
    keys, empty collections, None values, or an AI fallback response
    (ai_suggestions == {"error": ...}) are all handled without raising,
    so a report can always be generated.
    """

    analysis = analysis or {}
    ai_suggestions = ai_suggestions or {}

    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=_PAGE_MARGIN,
        rightMargin=_PAGE_MARGIN,
        topMargin=_PAGE_MARGIN,
        bottomMargin=_PAGE_MARGIN,
        title="HireLens Resume Analysis Report",
        author="HireLens",
    )

    styles = _build_styles()

    story = []
    story.extend(_build_header(styles))
    story.extend(_build_score_summary(analysis, styles))
    story.extend(_build_missing_skills(analysis, styles))
    story.extend(_build_keyword_summary(analysis, styles))
    story.extend(_build_ai_suggestions(ai_suggestions, styles))
    story.extend(_build_footer(styles))

    doc.build(story)

    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes