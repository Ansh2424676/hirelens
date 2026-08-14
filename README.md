# HireLens

AI-powered Resume Analyzer & Job Match Assistant built as the capstone project for the **AB Talks 60-Day Claude AI Challenge**.

HireLens analyzes a resume against a target job description and provides ATS compatibility scoring, resume-to-job matching, missing-skill detection, keyword analysis, AI-powered improvement suggestions, and a downloadable PDF report.

---

## Features

### Resume Analysis

- Upload resumes in PDF and DOCX format.
- Extract resume text for analysis.
- Analyze resume content against a target job description.

### ATS Compatibility

HireLens calculates an ATS compatibility score based on resume characteristics and screening factors.

The results include a detailed ATS score breakdown.

### Resume-to-Job Match

HireLens compares resume keywords with job-description keywords and calculates a match percentage.

The match score is designed to distinguish between relevant and unrelated job descriptions.

### Missing Skills

The application identifies skills present in the target job description but not detected in the resume.

Missing skills are grouped for easier review.

### Keyword Analysis

HireLens displays:

- Matched keywords
- Resume keywords
- Job-description keywords

The skills dictionary covers programming, data analytics, AI/ML, web technologies, enterprise IT, testing, soft skills, and design-related skills.

### AI Career Suggestions

The application can generate AI-powered resume improvement suggestions, including:

- Overall feedback
- Resume strengths
- Skills to highlight
- Priority improvements
- Communication and tone recommendations

If the external AI service is unavailable, the rule-based analysis remains available.

### PDF Report

Users can download a PDF report containing the analysis results, including:

- ATS score
- Resume-to-job match
- Missing skills
- Keyword analysis
- AI recommendations

---

## Technology Stack

### Backend

- Python
- Flask

### Resume Processing

- PDF resume parsing
- DOCX resume parsing

### Scoring

- Rule-based ATS scoring
- Keyword extraction
- Resume-to-job matching
- Missing-skill detection

### AI

- Anthropic Claude API
- Anthropic Python SDK
- Environment-based API key configuration

### Frontend

- HTML
- CSS
- JavaScript
- Jinja templates

### Testing

- pytest

### Reporting

- PDF report generation

---

## Project Structure

```text
hirelens/
│
├── ai_service/
│   └── claude_provider.py
│
├── scoring/
│   ├── ats_score.py
│   ├── engine.py
│   ├── keyword_extractor.py
│   ├── match_score.py
│   ├── missing_skills.py
│   └── skills_dictionary.py
│
├── report/
│   └── pdf_generator.py
│
├── templates/
│   ├── index.html
│   └── results.html
│
├── static/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
│
├── tests/
│   ├── test_download_report.py
│   ├── test_pdf_generator.py
│   └── test_scoring.py
│
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   ├── HireLens_Implementation_Blueprint.md
│   ├── PROJECT-STRUCTURE.md
│   ├── PROGRESS_LOG.md
│   ├── SCHEMA.md
│   ├── SETUP.md
│   ├── UI-WIREFRAMES.md
│   ├── test_log.md
│   └── v2_ideas.md
│
├── .env
├── .gitignore
├── README.md
└── requirements.txt