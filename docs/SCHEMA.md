# HireLens — Data Schema

**Companion to:** ARCHITECTURE.md
**Status:** Finalized Day 2

---

## 1. Does HireLens Need a Database?

**No.** Per the approved PRD (Section 5.2, explicitly out of scope for v1.0):
- No user accounts
- No saved history
- No multi-session persistence

The only "data" HireLens needs to manage is **one analysis result, temporarily, within a single user's browser session** — from the moment `/analyze` completes until either `/download-report` is called or the session ends. This is intentionally lightweight and does not warrant SQL, NoSQL, or any external database service.

This section documents the **in-memory/session data structure** instead of database tables — this is the correct and complete data design for v1.0 scope.

---

## 2. Storage Mechanism

- **Mechanism:** Flask server-side session (via Flask's built-in session handling, backed by a signed cookie referencing session data) **or**, if the payload proves too large for comfortable cookie-based sessions once AI suggestions are included, a simple in-memory dictionary on the server keyed by a per-request UUID stored in the user's session cookie.
- **Final decision point:** Day 8, once real payload sizes (including full AI suggestion text) are measured. Both options require zero new infrastructure (no database server, no external service) and both satisfy the "no persistent storage" requirement, since data is cleared when the session/app process ends.
- **Lifespan:** Data exists only for the duration of one analysis session. It is never written to disk permanently and is not retained after the user closes the browser tab or the server restarts.

---

## 3. Core Data Object: `AnalysisResult`

This is the single structured object that flows through the entire system — produced by the backend pipeline, consumed by the dashboard UI, and consumed again by the PDF report generator. Every module (`scoring/`, `ai_service/`, `report/`) reads and writes to this shared shape, so it is the most important "schema" in the project.

```python
AnalysisResult = {
    "meta": {
        "analyzed_at": "ISO 8601 timestamp",
        "resume_filename": "string",
        "resume_file_type": "pdf | docx",
    },

    "resume_text": "string (cleaned, extracted resume text)",
    "jd_text": "string (raw job description text as entered)",

    "ats_score": {
        "score": "int (0-100)",
        "breakdown": [
            {
                "factor": "string (e.g. 'Standard section headers detected')",
                "points": "int",
                "note": "string (short explanation)"
            }
        ]
    },

    "match_score": {
        "match_percent": "int (0-100)",
        "matched_keywords": ["string", "..."],
        "total_jd_keywords": "int"
    },

    "missing_skills": {
        "missing_by_category": {
            "programming_languages": ["string", "..."],
            "frameworks_libraries": ["string", "..."],
            "databases": ["string", "..."],
            "tools_platforms": ["string", "..."],
            "soft_skills": ["string", "..."]
        }
    },

    "keyword_analysis": {
        "matched": ["string", "..."],
        "missing": ["string", "..."]
    },

    "ai_suggestions": {
        "available": "boolean",
        "overall_feedback": "string | null",
        "strengths": ["string", "..."],
        "priority_improvements": [
            {
                "area": "string",
                "suggestion": "string",
                "example": "string"
            }
        ],
        "skills_to_highlight": ["string", "..."],
        "tone_notes": "string | null",
        "fallback_message": "string | null  (populated only if available == false)"
    }
}
```

### Field Notes
- **`available: false`** in `ai_suggestions` is the documented fallback state (per ARCHITECTURE.md Section 5) — the dashboard and PDF report must both handle this gracefully by showing `fallback_message` instead of the AI content blocks.
- **`resume_text`** is retained in the object (not discarded after scoring) because the AI service needs it, and so the report generator can optionally reference it — but it is **never persisted to disk** and is discarded when the session ends.
- All list fields default to empty lists (`[]`), never `null`, so downstream template/report code doesn't need repetitive null-checks.

---

## 4. Validation Rules Against PRD User Stories

| PRD Requirement | Schema Support |
|---|---|
| FR-3: ATS Compatibility Score with breakdown | `ats_score.score` + `ats_score.breakdown[]` |
| FR-4: Resume-to-Job Match % with explanation | `match_score.match_percent` + `matched_keywords` |
| FR-5: Missing Skills, grouped by category | `missing_skills.missing_by_category` |
| FR-6: Keyword Analysis (matched vs missing) | `keyword_analysis.matched` / `.missing` |
| FR-7: AI suggestions, structured & consistent | `ai_suggestions` object with fixed schema |
| FR-7: Graceful AI failure handling | `ai_suggestions.available` + `fallback_message` |
| FR-8: PDF report contains all results | Report generator consumes the full `AnalysisResult` object directly — no separate data model needed |
| NFR: Core scoring works without AI | `ats_score`, `match_score`, `missing_skills`, `keyword_analysis` are populated independently of `ai_suggestions` |

Every field required by any PRD user story has a corresponding, unambiguous place in this schema. No additional data structures are needed for v1.0.

---

## 5. Explicitly Deferred (v2.0 Schema Needs — Not Built Now)

If v2.0 adds accounts/history, a real schema will be needed then, roughly:
- `users` (id, email, created_at, ...)
- `analyses` (id, user_id, resume_filename, analysis_json, created_at, ...)
- `saved_reports` (id, analysis_id, pdf_path, created_at, ...)

**This is documented for future reference only — not implemented, not designed further, and not part of v1.0 scope.** Logged in `docs/v2_ideas.md`.

---

*End of SCHEMA.md*
