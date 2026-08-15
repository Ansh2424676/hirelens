# HireLens — 30-Day Growth Plan

## Objective

Transform the current HireLens MVP into a more reliable, intelligent, and production-ready career analysis product over the next 30 days.

The plan builds directly on the current technology stack:

- Python
- Flask
- HTML/CSS/JavaScript
- Resume parsing
- Keyword extraction
- Deterministic scoring
- Claude AI suggestions
- PDF report generation
- pytest
- Git/GitHub

Each day introduces one achievable milestone that builds on the previous day's work.

---

## Week 1 — Reliability and Engineering Foundation

### Day 1 — Baseline and Documentation

Review the current HireLens architecture, README, dependencies, tests, and application workflow.

Deliverables:

- Updated architecture notes
- Current feature inventory
- Known limitations list
- Baseline test result

Success criterion:

The current system can be understood and reproduced by another developer.

---

### Day 2 — Test Coverage Expansion

Review existing tests and identify untested application paths.

Add tests for:

- Invalid resume uploads
- Empty input
- Missing job description
- Unsupported file types
- Malformed extracted text

Success criterion:

New edge cases are covered without breaking existing tests.

---

### Day 3 — Resume Parsing Hardening

Improve resume parsing reliability.

Focus on:

- Empty PDFs
- Poorly formatted PDFs
- Multi-page resumes
- Missing sections
- Unusual text layouts

Success criterion:

Parsing failures produce useful error messages instead of application crashes.

---

### Day 4 — Keyword Normalization

Improve keyword normalization.

Handle cases such as:

```text
Git
GitHub
SQL
SQL queries
Power BI
PowerBI
Machine Learning
ML