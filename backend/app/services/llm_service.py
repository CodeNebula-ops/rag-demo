import json
from collections.abc import AsyncGenerator

import httpx
import structlog

from app.config import settings
from app.core.exceptions import LLMError

logger = structlog.get_logger()


async def generate_stream(
    messages: list[dict],
) -> AsyncGenerator[str, None]:
    if not settings.groq_api_key:
        raise LLMError("GROQ_API_KEY is not set. Get a free key at https://console.groq.com")

    url = f"{settings.groq_base_url}/chat/completions"

    payload = {
        "model": settings.groq_model_name,
        "messages": messages,
        "stream": True,
        "temperature": settings.llm_temperature,
        "max_tokens": settings.max_tokens,
        "top_p": 0.9,
    }

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(120.0)) as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                if response.status_code != 200:
                    text = await response.aread()
                    raise LLMError(f"Groq API returned {response.status_code}: {text.decode()}")

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue

                    data_str = line[5:].strip()
                    if data_str == "[DONE]":
                        break

                    try:
                        data = json.loads(data_str)
                    except json.JSONDecodeError:
                        continue

                    choices = data.get("choices", [])
                    if choices:
                        delta = choices[0].get("delta", {})
                        token = delta.get("content", "")
                        if token:
                            yield token

    except httpx.TimeoutException:
        raise LLMError("Groq API request timed out")
    except httpx.ConnectError:
        raise LLMError("Cannot connect to Groq API. Check your internet connection.")


async def generate(messages: list[dict]) -> str:
    tokens = []
    async for token in generate_stream(messages):
        tokens.append(token)
    return "".join(tokens)


async def check_groq_health() -> bool:
    if not settings.groq_api_key:
        return False
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(5.0)) as client:
            resp = await client.get(
                f"{settings.groq_base_url}/models",
                headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            )
            return resp.status_code == 200
    except Exception:
        return False
