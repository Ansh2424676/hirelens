# HireLens — API Design

**Companion to:** ARCHITECTURE.md, SCHEMA.md
**Status:** Finalized Day 2 — design only, no implementation yet (per Day 2 scope rules).

All endpoints are server-rendered (Flask returns HTML directly for page routes) except where noted. There is no separate JSON REST API layer in v1.0 — this keeps the architecture simple and matches the PRD's single-workflow, no-frontend-framework approach. Endpoints are documented in the order a user encounters them.

---

## Endpoint 1: `GET /`

**Purpose:** Renders the homepage/upload page — the entry point of the entire product.

- **Request:** No parameters.
- **Response:** `200 OK`, renders `index.html` (resume upload form + JD input form).
- **Validation:** None (static page render).
- **Authentication:** None (public route, no auth in v1.0).
- **Error Cases:** None expected; if template rendering fails, Flask's default error handling applies (should never occur in normal operation).

---

## Endpoint 2: `POST /analyze`

**Purpose:** Core endpoint — accepts the uploaded resume and job description, runs the full pipeline (parse → score → AI suggestions), and renders the results dashboard.

- **Request:**
  - `Content-Type: multipart/form-data`
  - Fields:
    - `resume_file` (file, required) — `.pdf` or `.docx`, max 5MB
    - `jd_text` (string, required) — pasted job description text, min 100 characters
- **Response (success):** `200 OK`, renders `results.html` with the full `AnalysisResult` object (see SCHEMA.md) passed into the template context. The result is also stored server-side (session/cache) for the subsequent report download.
- **Response (validation failure):** `200 OK` (re-renders `index.html` with inline error — not a 4xx, since this is a form re-render, not an API failure) with a specific, user-facing message:
  - "Please upload a PDF or DOCX file." (wrong file type)
  - "File is too large. Maximum size is 5MB." (size limit)
  - "Job description is too short. Please provide at least 100 characters." (JD length)
  - "We couldn't read this file. It may be corrupted or scanned as an image rather than text." (parsing failure)
- **Validation:**
  - File extension check (`.pdf`, `.docx` only).
  - File size check (≤ 5MB) — enforced before parsing begins.
  - JD text length check (≥ 100 characters).
  - Parsing success check (raw text extraction must succeed and be non-empty).
- **Authentication:** None.
- **Error Cases:**
  | Case | Handling |
  |---|---|
  | No file uploaded | Inline error, re-render `index.html` |
  | Invalid file type | Inline error, re-render `index.html` |
  | File exceeds size limit | Inline error, re-render `index.html` |
  | Corrupted/unreadable file | Inline error, re-render `index.html` |
  | Scanned/image-based PDF (no extractable text) | Inline error, re-render `index.html`, message explains likely cause |
  | JD text missing or too short | Inline error, re-render `index.html` |
  | AI suggestion generation fails (timeout, API error, malformed response) | **Does not fail the request** — `results.html` still renders with `ai_suggestions.available = false` and a fallback message; ATS score, match %, and missing skills render normally |
  | Unexpected server error during parsing/scoring | `500`-level friendly error page (generic "something went wrong, please try again" — no stack trace exposed) |

---

## Endpoint 3: `GET /download-report`

**Purpose:** Generates and returns the PDF report for the most recently analyzed resume/JD pair in the current session.

- **Request:** No body parameters. Relies on the server-side session (or cache, keyed via session) established during `/analyze`.
- **Response (success):** `200 OK`, `Content-Type: application/pdf`, `Content-Disposition: attachment; filename=HireLens_Report.pdf` — triggers a file download in the browser.
- **Validation:**
  - Session must contain a valid, previously generated `AnalysisResult`.
- **Authentication:** None.
- **Error Cases:**
  | Case | Handling |
  |---|---|
  | No analysis found in session (e.g., user navigated directly to this URL without analyzing first) | Redirect to `/` with a message: "Please analyze a resume first." |
  | PDF generation fails internally | Friendly error message, logged server-side, user directed to try again; does not crash the app |
  | Session expired between analyze and download | Same handling as "no analysis found" — redirect to `/` with explanatory message |

---

## Endpoint 4: `GET /health` *(recommended addition — supports Day 10 deployment verification)*

**Purpose:** A lightweight health-check endpoint to confirm the deployed application is running correctly, and optionally that the Claude API key is configured (without making a real API call). Useful for verifying production deployment on Day 10 and for the hosting platform's own health checks if supported.

- **Request:** None.
- **Response:** `200 OK`, JSON: `{"status": "ok", "ai_configured": true|false}`
- **Validation:** None.
- **Authentication:** None.
- **Error Cases:** None expected — this route should never fail unless the app itself is down.

> **Note on this addition:** This endpoint was not in the original Day 1 Blueprint. It's a small, low-risk addition that directly supports the PRD's deployment-reliability goal (Section 11 risk: "deployment behaves differently from local dev") by giving Day 10 a fast, concrete way to verify the production deployment without running the full user flow every time. It requires no new dependencies and takes minutes to implement on Day 8 or Day 10. Flagging it here per the "explain before changing" rule — happy to drop it if you'd rather keep the endpoint surface area minimal.

---

## Summary Table

| Method | Route | Purpose | Auth |
|---|---|---|---|
| GET | `/` | Upload page | None |
| POST | `/analyze` | Run full analysis pipeline, render dashboard | None |
| GET | `/download-report` | Generate & download PDF report | None |
| GET | `/health` | Deployment health check (recommended addition) | None |

No other endpoints are needed for v1.0. This directly mirrors the PRD's single-workflow core (Resume Upload → JD Input → Analysis → AI Suggestions → PDF Report) with zero extraneous surface area.

---

*End of API.md*
