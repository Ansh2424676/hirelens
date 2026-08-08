import pdfplumber


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extract text from all pages of a PDF resume.

    Returns:
        {
            "success": bool,
            "text": str,
            "error": str | None
        }
    """
    try:
        extracted_pages = []

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    extracted_pages.append(page_text)

        extracted_text = "\n\n".join(extracted_pages).strip()

        if not extracted_text:
            return {
                "success": False,
                "text": "",
                "error": (
                    "This PDF appears to be scanned/image-based; "
                    "please upload a text-based PDF."
                ),
            }

        return {
            "success": True,
            "text": extracted_text,
            "error": None,
        }

    except Exception as exc:
        return {
            "success": False,
            "text": "",
            "error": f"Unable to read the PDF file: {exc}",
        }