import re


def clean_text(text: str) -> str:
    """Normalize resume text while preserving useful line breaks."""
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = "".join(char for char in text if char == "\n" or char == "\t" or char.isprintable())
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()