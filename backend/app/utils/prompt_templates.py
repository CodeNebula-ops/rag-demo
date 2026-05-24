SYSTEM_PROMPT = """You are a knowledge base assistant. You answer questions \
ONLY using the provided context documents. Follow these rules strictly:

1. Answer ONLY from the provided context. If the context does not contain \
the answer, say: "I don't have enough information in the knowledge base \
to answer this question. Please consult the relevant document directly."
2. NEVER invent, assume, or hallucinate information not in the context.
3. ALWAYS cite your sources using [Source: document_title, section] format.
4. If the answer spans multiple documents, cite each one.
5. If you are uncertain, say so explicitly. Do not guess.
6. Keep answers concise, factual, and directly relevant to the question.
7. For procedural questions, present steps in numbered order.
8. If the question is ambiguous, state your interpretation before answering.

CONTEXT DOCUMENTS:
{context_chunks}

CONVERSATION HISTORY:
{conversation_history}"""


def format_context_chunks(chunks: list[dict]) -> str:
    parts = []
    for chunk in chunks:
        title = chunk.get("document_title", "Unknown")
        section = chunk.get("section_path", "")
        text = chunk.get("chunk_text", "")
        parts.append(f"[Document: {title} | Section: {section}]\n{text}")
    return "\n---\n".join(parts)


def format_conversation_history(messages: list[dict]) -> str:
    parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        parts.append(f"{role}: {content}")
    return "\n".join(parts) if parts else "No prior conversation."
