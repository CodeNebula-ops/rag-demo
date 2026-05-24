import re

import structlog
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.core.language_detector import detect_language

logger = structlog.get_logger()


def chunk_document(
    text: str,
    document_title: str,
) -> list[dict]:
    sections = _split_into_sections(text)
    all_chunks = []
    chunk_index = 0

    for section_path, section_text in sections:
        paragraph_chunks = _split_into_paragraphs(section_text)

        for para_text in paragraph_chunks:
            prefixed_text = f"Section: [{section_path}]\n\n{para_text}" if section_path else para_text
            language = detect_language(para_text)
            sentences = _split_into_sentences(para_text)

            all_chunks.append({
                "chunk_index": chunk_index,
                "chunk_text": prefixed_text,
                "section_path": section_path,
                "chunk_level": "paragraph",
                "token_count": len(prefixed_text.split()),
                "language": language,
                "sentences": sentences,
            })
            chunk_index += 1

    logger.info("document_chunked", title=document_title, total_chunks=len(all_chunks))
    return all_chunks


def _split_into_sections(text: str) -> list[tuple[str, str]]:
    heading_pattern = re.compile(
        r"^(#{1,3}\s+.+|[A-Z][A-Z\s]{2,}[A-Z]|(?:Chapter|Section|Part)\s+\d+[.:]\s*.+)$",
        re.MULTILINE,
    )

    matches = list(heading_pattern.finditer(text))
    if not matches:
        return [("", text)]

    sections = []
    for i, match in enumerate(matches):
        heading = match.group().strip().lstrip("#").strip()
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        section_text = text[start:end].strip()
        if section_text:
            sections.append((heading, section_text))

    preamble = text[: matches[0].start()].strip()
    if preamble:
        sections.insert(0, ("Introduction", preamble))

    return sections


def _split_into_paragraphs(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=lambda t: len(t.split()),
    )
    return splitter.split_text(text)


def _split_into_sentences(text: str) -> list[str]:
    parts = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in parts if s.strip()]
