import structlog

from app.services.llm_service import generate

logger = structlog.get_logger()

REWRITE_PROMPT = """You are a query preprocessor for a RAG system. Given the user's query and conversation history, produce a JSON object with these fields:

- "rewritten_query": A clear, standalone search query (resolve pronouns, add context from history). If the query is already clear, return it unchanged.
- "expanded_terms": A list of 2-4 synonyms or related terms to broaden the search.
- "intent": One of: "factual", "procedural", "comparative", "exploratory", "clarification"
- "is_greeting": true if the query is just a greeting/small-talk with no information need, false otherwise.

Respond with ONLY valid JSON, no explanation.

Conversation history:
{history}

User query: {query}"""


async def understand_query(query: str, history: list[dict] | None = None) -> dict:
    history_text = ""
    if history:
        history_text = "\n".join(
            f"{m['role']}: {m['content']}" for m in history[-6:]
        )

    prompt = REWRITE_PROMPT.format(history=history_text or "None", query=query)

    try:
        raw = await generate([
            {"role": "system", "content": "You are a precise JSON-only query analyzer."},
            {"role": "user", "content": prompt},
        ])

        import json
        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0]
        result = json.loads(raw)

        logger.info(
            "query_understood",
            intent=result.get("intent"),
            is_greeting=result.get("is_greeting"),
            rewritten=result.get("rewritten_query", query)[:80],
        )
        return {
            "rewritten_query": result.get("rewritten_query", query),
            "expanded_terms": result.get("expanded_terms", []),
            "intent": result.get("intent", "factual"),
            "is_greeting": result.get("is_greeting", False),
        }
    except Exception as e:
        logger.warning("query_understanding_failed", error=str(e))
        return {
            "rewritten_query": query,
            "expanded_terms": [],
            "intent": "factual",
            "is_greeting": False,
        }
