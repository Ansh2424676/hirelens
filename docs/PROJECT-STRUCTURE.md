# HireLens — Project Structure

**Companion to:** ARCHITECTURE.md
**Status:** Finalized Day 2 — reflects the folder structure created today, plus where each future day's work will live.

---

## 1. Current Structure (As Built, End of Day 2)

```
hirelens/
├── venv/                      # Local virtual environment (gitignored, never committed)
├── .gitignore                 # Excludes venv/, .env, __pycache__, uploads, generated files
├── .env                       # Real API key (gitignored, never committed)
├── .env.example                # Template showing required env vars (committed)
├── requirements.txt            # Pinned Python dependencies (Flask, python-dotenv, anthropic)
├── app.py                      # Flask entry point (currently a minimal skeleton)
├── README.md                   # Project overview (expanded further on Day 9)
│
├── parsing/                    # Resume text extraction module (built Day 3)
│   └── __init__.py
│
├── scoring/                    # Rule-based ATS/match/missing-skills engine (built Day 4-5)
│   └── __init__.py
│
├── ai_service/                 # Claude API integration, provider-agnostic (built Day 6)
│   └── __init__.py
│
├── report/                     # PDF report generation (built Day 8)
│   └── __init__.py
│
├── templates/                  # Jinja2 HTML templates (built out Day 3, polished Day 7)
│
├── static/
│   ├── css/                    # Stylesheets (built Day 7)
│   └── js/                     # Client-side JS (form validation, loading state — Day 7)
│
├── test_files/                 # Local sample resumes/JDs for manual testing (gitignored)
│
└── docs/
    ├── PROGRESS_LOG.md         # One-line entry per day (updated daily)
    └── v2_ideas.md              # Deferred feature backlog (updated as ideas arise)
```

---

## 2. Folder Responsibilities (Why Each Exists)

| Folder/File | Responsibility | Why This Structure |
|---|---|---|
| `app.py` | Flask app instance, route definitions, request orchestration | Kept as the single "wiring" layer — it calls into modules but contains no business logic itself, so parsing/scoring/AI logic stays testable independent of Flask |
| `parsing/` | Converts uploaded files into clean text | Isolated so parsing logic can be unit-tested without a running web server, and so PDF/DOCX-specific code doesn't leak into scoring or UI logic |
| `scoring/` | All rule-based intelligence (ATS score, match %, missing skills, keyword analysis) | Kept as pure functions with no I/O — directly supports the PRD's reliability requirement that core scoring never depends on external services, and makes this module trivially unit-testable |
| `ai_service/` | Claude API integration, isolated behind a clean interface | Directly implements PRD FR-7's "provider-agnostic" requirement — if the AI provider ever changes, only this folder is touched |
| `report/` | PDF generation logic | Kept separate from `scoring/` so report *formatting* concerns never mix with score *calculation* concerns — the report generator simply consumes the finished `AnalysisResult` object (see `SCHEMA.md`) |
| `templates/` | HTML page templates | Standard Flask/Jinja2 convention; keeps presentation markup out of Python route code |
| `static/` | CSS and JS assets | Standard Flask convention; served directly, no build step required |
| `test_files/` | Local sample resumes/JDs used for manual and matrix testing (Day 3, Day 9) | Gitignored — real resumes shouldn't be committed to a public repo; only used locally |
| `docs/` | All project documentation (architecture, schema, API, wireframes, progress log, backlog) | Keeps documentation discoverable and separate from application code, and directly supports the PRD's Day 10 success criterion requiring clear documentation |

---

## 3. Where Future Work Will Live (Day-by-Day Mapping)

| Day | Adds To |
|---|---|
| Day 3 | `parsing/pdf_parser.py`, `parsing/docx_parser.py`, `parsing/cleaner.py`; first real route in `app.py`; first version of `templates/index.html` |
| Day 4 | `scoring/skills_dictionary.py`, `scoring/keyword_extractor.py` |
| Day 5 | `scoring/ats_score.py`, `scoring/match_score.py`, `scoring/missing_skills.py`, `scoring/engine.py`; `tests/test_scoring.py` (new top-level `tests/` folder) |
| Day 6 | `ai_service/base.py`, `ai_service/claude_provider.py`, `ai_service/response_parser.py`, `ai_service/prompts.py` |
| Day 7 | Final `templates/index.html`, `templates/results.html`; `static/css/styles.css`; `static/js/app.js` |
| Day 8 | `report/pdf_generator.py`; session/cache wiring in `app.py`; possible `routes/` split if `app.py` grows large |
| Day 9 | `docs/test_log.md`; bug fixes distributed across existing files (no new top-level structure expected) |
| Day 10 | `Procfile` (or Render-equivalent config); `docs/screenshots/`; `docs/demo_video_link.md`; finalized `README.md` |

**Note on `routes/`:** The Day 1 Blueprint mentioned an optional `routes/` folder. Given the final endpoint count is small (4 endpoints total, per `API.md`), all routes will live directly in `app.py` unless it grows unwieldy — if that happens on Day 8, we'll split into `routes/` at that point rather than over-structuring prematurely. This is a minor, low-risk deviation flagged per the "explain before changing" rule — no functional impact, purely an organizational choice deferred until it's actually needed.

---

## 4. Naming & Convention Rules (for consistency across all remaining days)

- All Python modules: `snake_case.py`
- All functions: `snake_case()`
- Module-level constants (e.g., `SKILLS_DB`): `UPPER_SNAKE_CASE`
- Templates: `snake_case.html`
- No abbreviated/cryptic names — favor clarity (`generate_pdf_report`, not `gen_pdf`)
- Every module's public functions should have a docstring stating input/output shape (especially important since multiple modules pass the shared `AnalysisResult` structure between them)

---

*End of PROJECT-STRUCTURE.md*
