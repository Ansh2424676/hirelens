from pathlib import Path
import tempfile

from flask import Flask, render_template, request

from parsing import parse_resume
from scoring.keyword_extractor import extract_keywords


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MIN_JD_LENGTH = 100


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    uploaded_file = request.files.get("resume")
    job_description = request.form.get("job_description", "").strip()

    # Server-side Job Description validation
    if not job_description:
        return render_template(
            "index.html",
            error="Please enter a job description.",
            job_description=job_description
        )

    if len(job_description) < MIN_JD_LENGTH:
        return render_template(
            "index.html",
            error=(
                "Job description is too short. "
                "Please enter at least 100 characters."
            ),
            job_description=job_description
        )

    # Resume validation
    if not uploaded_file or not uploaded_file.filename:
        return render_template(
            "index.html",
            error="Please select a resume file.",
            job_description=job_description
        )

    extension = Path(uploaded_file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return render_template(
            "index.html",
            error="Invalid file type. Please upload a PDF or DOCX resume.",
            job_description=job_description
        )

    # Save uploaded resume temporarily
    with tempfile.NamedTemporaryFile(
        suffix=extension,
        delete=False
    ) as temp_file:
        uploaded_file.save(temp_file.name)
        temp_path = temp_file.name

    try:
        # Existing Day 3 resume parsing flow
        result = parse_resume(temp_path, extension)
    finally:
        Path(temp_path).unlink(missing_ok=True)

    if not result["success"]:
        return render_template(
            "index.html",
            error=result["error"],
            job_description=job_description
        )

    resume_text = result["raw_text"]

    # Day 4 keyword extraction
    resume_keywords = extract_keywords(resume_text)
    jd_keywords = extract_keywords(job_description)

    return render_template(
        "index.html",
        extracted_text=resume_text,
        resume_keywords=sorted(resume_keywords),
        jd_keywords=sorted(jd_keywords),
        job_description=job_description
    )


@app.errorhandler(413)
def file_too_large(_error):
    return render_template(
        "index.html",
        error="File is too large. Maximum allowed size is 5 MB."
    ), 413


if __name__ == "__main__":
    app.run(debug=True)