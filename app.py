from pathlib import Path
import tempfile

from flask import Flask, render_template, request

from parsing import parse_resume

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route("/upload-resume", methods=["POST"])
def upload_resume():
    uploaded_file = request.files.get("resume")

    if not uploaded_file or not uploaded_file.filename:
        return render_template(
            "index.html",
            error="Please select a resume file."
        )

    extension = Path(uploaded_file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        return render_template(
            "index.html",
            error="Invalid file type. Please upload a PDF or DOCX resume."
        )

    with tempfile.NamedTemporaryFile(
        suffix=extension,
        delete=False
    ) as temp_file:
        uploaded_file.save(temp_file.name)
        temp_path = temp_file.name

    result = parse_resume(temp_path, extension)

    Path(temp_path).unlink(missing_ok=True)

    if not result["success"]:
        return render_template(
            "index.html",
            error=result["error"]
        )

    return render_template(
        "index.html",
        extracted_text=result["raw_text"]
    )


@app.errorhandler(413)
def file_too_large(_error):
    return render_template(
        "index.html",
        error="File is too large. Maximum allowed size is 5 MB."
    ), 413


if __name__ == "__main__":
    app.run(debug=True)