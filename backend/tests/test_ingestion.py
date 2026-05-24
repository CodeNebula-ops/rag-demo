import pytest
from app.services.chunking_service import chunk_document, _split_into_sections, _split_into_sentences
from app.core.text_preprocessor import normalize_text


def test_normalize_text():
    text = "Hello   world\n\n\n\nTest"
    result = normalize_text(text)
    assert "   " not in result
    assert "\n\n\n" not in result


def test_chunk_document_produces_chunks():
    text = "This is a test document. " * 100
    chunks = chunk_document(text, "Test Document")
    assert len(chunks) > 0
    assert all("chunk_text" in c for c in chunks)
    assert all("chunk_index" in c for c in chunks)


def test_section_splitting():
    text = "# Introduction\nSome intro text.\n\n# Methods\nSome methods text."
    sections = _split_into_sections(text)
    assert len(sections) >= 2


def test_sentence_splitting():
    text = "First sentence. Second sentence. Third sentence."
    sentences = _split_into_sentences(text)
    assert len(sentences) == 3


def test_chunk_includes_section_path():
    text = "# Chapter One\nThis is chapter one content with enough words to form a chunk."
    chunks = chunk_document(text, "Test")
    assert any("Section:" in c["chunk_text"] for c in chunks)
