import pytest
from app.services.guardrails_service import compute_confidence, should_skip_llm
from app.services.citation_service import has_citations, extract_citations


def test_confidence_high():
    result = compute_confidence([0.9, 0.85, 0.88], 0.95)
    assert result["level"] == "high"
    assert result["score"] >= 0.85


def test_confidence_low():
    result = compute_confidence([0.2, 0.1], 0.3)
    assert result["level"] == "low"
    assert result["score"] < 0.7


def test_should_skip_llm_all_low():
    assert should_skip_llm([0.1, 0.2, 0.05]) is True


def test_should_skip_llm_has_high():
    assert should_skip_llm([0.1, 0.5, 0.05]) is False


def test_should_skip_llm_empty():
    assert should_skip_llm([]) is True


def test_has_citations_true():
    assert has_citations("Answer text [Source: Doc, Section 1] more text") is True


def test_has_citations_false():
    assert has_citations("Answer with no citations") is False


def test_extract_citations_from_text():
    chunks = [
        {"chunk_text": "some content", "document_title": "My Doc", "section_path": "Intro", "document_id": "123", "reranker_score": 0.9},
    ]
    answer = "The answer is here [Source: My Doc, Intro]."
    citations = extract_citations(answer, chunks)
    assert len(citations) >= 1
    assert citations[0]["document_title"] == "My Doc"
