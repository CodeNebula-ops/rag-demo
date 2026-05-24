import pytest
from app.utils.prompt_templates import format_context_chunks, format_conversation_history, SYSTEM_PROMPT


def test_format_context_chunks():
    chunks = [
        {"document_title": "Doc A", "section_path": "Intro", "chunk_text": "Hello world"},
        {"document_title": "Doc B", "section_path": "Methods", "chunk_text": "Test content"},
    ]
    result = format_context_chunks(chunks)
    assert "Doc A" in result
    assert "Doc B" in result
    assert "Hello world" in result


def test_format_conversation_history_empty():
    result = format_conversation_history([])
    assert "No prior conversation" in result


def test_format_conversation_history():
    history = [
        {"role": "user", "content": "What is X?"},
        {"role": "assistant", "content": "X is Y."},
    ]
    result = format_conversation_history(history)
    assert "What is X?" in result
    assert "X is Y." in result


def test_system_prompt_has_placeholders():
    assert "{context_chunks}" in SYSTEM_PROMPT
    assert "{conversation_history}" in SYSTEM_PROMPT


def test_system_prompt_has_grounding_rules():
    assert "ONLY" in SYSTEM_PROMPT
    assert "NEVER" in SYSTEM_PROMPT
    assert "cite" in SYSTEM_PROMPT.lower()
