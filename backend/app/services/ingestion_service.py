from pathlib import Path

import chardet
import fitz
import structlog
from docx import Document as DocxDocument

from app.core.exceptions import FileValidationError
from app.core.text_preprocessor import remove_headers_footers

logger = structlog.get_logger()


def _extract_text(file_path: str, ext: str) -> str:
    if ext == ".pdf":
        return _extract_pdf(file_path)
    elif ext in (".docx", ".doc"):
        return _extract_docx(file_path)
    elif ext in (".txt", ".md"):
        return _extract_text_file(file_path)
    raise FileValidationError(f"Cannot extract text from {ext}")


def _extract_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    pages = []
    for page in doc:
        text = page.get_text()
        pages.append(text)
    doc.close()

    pages = remove_headers_footers(pages)
    return "\n\n".join(pages)


def _extract_docx(file_path: str) -> str:
    doc = DocxDocument(file_path)
    parts = []
    for para in doc.paragraphs:
        if para.style and para.style.name.startswith("Heading"):
            level = para.style.name.replace("Heading ", "")
            prefix = "#" * min(int(level) if level.isdigit() else 1, 3)
            parts.append(f"{prefix} {para.text}")
        elif para.text.strip():
            parts.append(para.text)
    return "\n\n".join(parts)


def _extract_text_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        raw = f.read()
    detected = chardet.detect(raw)
    encoding = detected.get("encoding", "utf-8") or "utf-8"
    return raw.decode(encoding, errors="replace")
