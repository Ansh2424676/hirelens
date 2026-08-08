from pathlib import Path

from .pdf_parser import extract_text_from_pdf
from .docx_parser import extract_text_from_docx
from .cleaner import clean_text


def parse_resume(file_path: str, file_type: str) -> dict:
    """Parse a PDF or DOCX resume using one consistent output contract."""
    extension = file_type.lower().lstrip(".")

    if extension == "pdf":
        result = extract_text_from_pdf(file_path)
    elif extension == "docx":
        result = extract_text_from_docx(file_path)
    else:
        return {
            "success": False,
            "raw_text": "",
            "error": "Unsupported file type. Please upload a PDF or DOCX resume.",
        }

    if not result["success"]:
        return {
            "success": False,
            "raw_text": "",
            "error": result["error"],
        }

    return {
        "success": True,
        "raw_text": clean_text(result["text"]),
        "error": None,
    }