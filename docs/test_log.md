# HireLens — Day 9 Test Log

## Structured Testing & Bug-Fix Record

**Project:** HireLens  
**Version:** v1.0  
**Testing Day:** Day 9 — Structured Testing, Bug Fixing & Polish  
**Date:** 14 August 2026  
**Environment:** Windows / Python 3.14.6 / Flask / Local Development  
**Test Runner:** pytest  

---

## 1. Testing Objective

The objective of Day 9 testing was to validate the feature-complete HireLens application against realistic resume and job-description inputs, identify critical issues, fix them, and verify that the fixes did not introduce regressions.

Testing focused on:

- Resume-to-job matching
- Keyword extraction
- Missing-skill detection
- ATS scoring
- PDF report generation
- Results-page rendering
- Progress-bar accuracy
- Unrelated job-description behavior
- High-match job-description behavior
- Input validation
- Security and secret hygiene
- Regression testing

No new product features were intentionally introduced during this testing cycle.

---

## 2. Automated Test Suite

| Test | Result | Notes |
|---|---|---|
| Full pytest suite | PASS | 56 tests passed |
| ATS scoring tests | PASS | Existing scoring behavior preserved |
| Match-score tests | PASS | Match percentage and keyword behavior verified |
| Missing-skills tests | PASS | Missing keyword detection preserved |
| PDF generator tests | PASS | PDF generation remained functional |
| Download report tests | PASS | Report download functionality remained functional |

### Command

`python -m pytest -q`

### Result

`56 passed in 2.71s`

---

## 3. Manual Test Matrix

### Test 01 — High-Match Data Analyst Job Description

**Category:** Core workflow / Regression

**Expected:** Relevant Data Analyst JD should produce a high match score with limited missing skills.

**Actual:**
- ATS Compatibility: 88/100
- Resume-to-JD Match: 81%
- Missing Skills: 3
- Matched Keywords: 13
- Results page loaded successfully
- Progress bar matched the displayed score
- Download report available

**Status:** PASS

---

### Test 02 — Unrelated Graphic Designer Job Description

**Category:** Low-match / Edge case

**Initial result before fix:**
- Resume-to-JD Match: 100%
- Missing Skills: 0

**Bug:** Graphic Design-specific skills were missing from the keyword dictionary, causing an incorrect perfect match.

**Fix:** Added relevant design skills including Photoshop, Illustrator, InDesign, Figma, UI/UX Design, Typography, Color Theory, Graphic Design, Branding, Illustration, Image Editing, Responsive Web Design, and Digital Marketing.

**Retest result:**
- Resume-to-JD Match: 0%
- Missing Skills: 17
- ATS Compatibility: 88/100
- Analysis completed successfully
- No crash

**Status:** PASS — FIXED AND RETESTED

---

### Test 03 — Keyword Extraction

**Category:** Scoring / Keyword extraction

**Command tested:**

`python -c "from scoring.keyword_extractor import extract_keywords; jd='Adobe Photoshop Adobe Illustrator Figma UI/UX design Typography Color theory Graphic design Visual communication Branding Illustration Image editing Responsive web design'; print(sorted(extract_keywords(jd)))"`

**Result:** Design-specific keywords including Photoshop, Illustrator, Figma, Graphic Design, Typography, Branding, Illustration, Image Editing, Responsive Web Design, and Visual Communication were detected.

**Status:** PASS

---

### Test 04 — Match Progress Bar

**Category:** UI / Data consistency

**Bug:** Progress bar was hard-coded to 72% while the displayed match score was dynamic.

**Fix:** Progress bar now receives the actual match score and updates dynamically.

**Retest:** Data Analyst test displayed 81% match and the progress bar visually represented approximately 81%.

**Status:** PASS — FIXED AND RETESTED

---

### Test 05 — Download Report Label

**Category:** UI polish

**Issue:** Results page contained outdated Day 8 wording.

**Fix:** Updated labels to simply `Download report`.

**Status:** PASS

---

### Test 06 — Empty Job Description

**Category:** Input validation

**Expected:** Empty JD should prevent form submission.

**Actual:** Submission was blocked and analysis did not start.

**Status:** PASS

---

### Test 07 — JD Below Minimum Length

**Category:** Input validation

**Test input:** `Data analyst role.`

**Expected:** Submission should be blocked because JD requires at least 100 characters.

**Actual:** Minimum-length validation message was displayed.

**Status:** PASS

---

### Test 08 — DOCX Resume

**Category:** Resume format

**Expected:** DOCX resume should be accepted and processed.

**Actual:**
- DOCX accepted
- Resume processed
- Valid JD accepted
- Analysis completed
- Results page loaded
- No crash

**Status:** PASS

---

### Test 09 — Oversized Resume

**Category:** File validation

**Test:** Approximately 6 MB dummy PDF.

**Expected:** File exceeding 5 MB should be rejected.

**Actual:** Oversized resume was rejected and analysis did not proceed.

**Status:** PASS

---

### Test 10 — Invalid File Type

**Category:** File validation

A `.txt` file was created for testing but was deleted before the browser upload test was completed.

**Status:** NOT EXECUTED

This test is intentionally not marked as PASS.

---

### Test 11 — AI Service Failure / Fallback

**Category:** Error handling

During local testing the Claude request returned:

`Claude request was rejected. The account may have insufficient credits or the request configuration may be invalid.`

The application still returned the results page with HTTP 200 and preserved the rule-based analysis.

**Status:** PASS — FALLBACK BEHAVIOR OBSERVED

**Note:** The external AI-service rejection is treated as an environment/account configuration issue rather than a core workflow crash.

---

## 4. Automated Regression After Fixes

### Command

`python -m pytest -q`

### Result

`56 passed in 2.71s`

**Status:** PASS

No existing automated tests were broken by the Day 9 fixes.

---

## 5. Security & Secret Hygiene

### `.env` Tracking

Command:

`git ls-files .env`

Result: No output.

**Status:** PASS

The local `.env` file is not tracked by Git.

### Anthropic Secret Search

Command:

`git grep -n "sk-ant-" -- . ':!venv'`

Result: No output.

**Status:** PASS

No Anthropic API secret was found in tracked files.

### Environment Variable Reference

Command:

`git grep -n "ANTHROPIC_API_KEY" -- . ':!venv'`

Result: Only environment-variable references and documentation were found.

**Status:** PASS

No actual API key value was exposed.

---

## 6. Temporary Test File Cleanup

Temporary oversized and invalid-file test files were created under `test_files`.

The directory was removed after testing.

Verification:

`Test-Path test_files`

Result:

`False`

**Status:** PASS

---

## 7. Critical Bug Triage

| Issue | Severity | Status |
|---|---|---|
| Unrelated JD incorrectly produced 100% match | Critical | Fixed and retested |
| Missing skills incorrectly reported as 0 | Critical | Fixed and retested |
| Match progress bar used hard-coded 72% | Cosmetic / UX | Fixed and retested |
| Outdated Day 8 report label | Cosmetic | Fixed |
| Empty JD submission | Validation | Working |
| JD below 100 characters | Validation | Working |
| Oversized file rejection | Validation | Working |
| Invalid `.txt` upload | Validation | Not executed |

---

## 8. Day 9 QA Checklist

- [x] Automated pytest suite passes
- [x] High-match Data Analyst test
- [x] Low-match Graphic Designer test
- [x] Keyword extraction verified
- [x] Missing-skill detection verified
- [x] ATS scoring verified
- [x] DOCX workflow verified
- [x] Empty JD validation verified
- [x] Minimum JD length validation verified
- [x] Oversized file rejection verified
- [x] Progress-bar accuracy verified
- [x] Download report label corrected
- [x] API key hygiene verified
- [x] Temporary test files cleaned
- [x] Regression tests passed

---

## 9. Remaining Day 9 Coverage

- [ ] Complete invalid file-type browser test
- [ ] Very short resume
- [ ] Very long 2+ page resume
- [ ] Resume with unusual fonts/symbols
- [ ] DOCX with tables
- [ ] Short JD
- [ ] Long/detailed JD
- [ ] Unusual JD formatting
- [ ] Mobile-width browser
- [ ] Non-Chrome browser
- [ ] Performance sanity check
- [ ] Final visual polish review
- [ ] Final end-to-end walkthrough

---

## 10. Final QA Notes

The major scoring defect discovered during Day 9 was fixed and successfully retested.

HireLens now correctly distinguishes between relevant Data Analyst roles and unrelated Graphic Designer roles.

The application also correctly validates empty and undersized job descriptions, rejects oversized resumes, supports DOCX resumes, maintains PDF report functionality, and passes the complete automated regression suite.

No new product features were added during the bug-fixing work.

Remaining items are primarily structured test coverage and final release-readiness checks.
