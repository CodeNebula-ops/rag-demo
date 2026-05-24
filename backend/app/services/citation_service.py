import re
import structlog

logger = structlog.get_logger()


def extract_citations(answer: str, retrieved_chunks: list[dict]) -> list[dict]:
    citation_pattern = re.compile(r"\[Source:\s*([^,\]]+?)(?:,\s*([^\]]+?))?\]")
    matches = citation_pattern.findall(answer)

    citations = []
    seen = set()

    for doc_title, section in matches:
        doc_title = doc_title.strip()
        section = section.strip() if section else ""
        key = f"{doc_title}|{section}"

        if key in seen:
            continue
        seen.add(key)

        best_chunk = _find_matching_chunk(doc_title, section, retrieved_chunks)
        if best_chunk:
            citations.append({
                "text_snippet": best_chunk["chunk_text"][:200],
                "document_title": best_chunk.get("document_title", doc_title),
                "section_path": best_chunk.get("section_path", section),
                "document_id": best_chunk.get("document_id", ""),
                "relevance_score": round(best_chunk.get("reranker_score", 0.0), 3),
            })

    if not citations and retrieved_chunks:
        for chunk in retrieved_chunks[:3]:
            citations.append({
                "text_snippet": chunk["chunk_text"][:200],
                "document_title": chunk.get("document_title", "Unknown"),
                "section_path": chunk.get("section_path", ""),
                "document_id": chunk.get("document_id", ""),
                "relevance_score": round(chunk.get("reranker_score", 0.0), 3),
            })

    return citations


def _find_matching_chunk(doc_title: str, section: str, chunks: list[dict]) -> dict | None:
    doc_title_lower = doc_title.lower()
    section_lower = section.lower()

    best_match = None
    best_score = 0

    for chunk in chunks:
        score = 0
        chunk_title = chunk.get("document_title", "").lower()
        chunk_section = chunk.get("section_path", "").lower()

        if doc_title_lower in chunk_title or chunk_title in doc_title_lower:
            score += 2
        if section_lower and (section_lower in chunk_section or chunk_section in section_lower):
            score += 1

        if score > best_score:
            best_score = score
            best_match = chunk

    return best_match if best_score > 0 else (chunks[0] if chunks else None)


def has_citations(answer: str) -> bool:
    return bool(re.search(r"\[Source:", answer))
