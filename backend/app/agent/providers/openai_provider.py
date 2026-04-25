"""OpenAI Provider — JSON mode 지원"""

import logging
from typing import Any

from app.agent.providers.base import DEFAULT_TIMEOUT_SECONDS, BaseProvider

logger = logging.getLogger("notionforge.providers.openai")


class OpenAIProvider(BaseProvider):
    name = "openai"
    supports_json_mode = True

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.default_model = model or "gpt-4o-mini"

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        try:
            import httpx

            async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT_SECONDS) as client:
                resp = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json={
                        "model": model or self.default_model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_message},
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.3,
                        "max_tokens": 4096,
                    },
                )
                if resp.status_code != 200:
                    logger.warning(f"[OpenAI] HTTP {resp.status_code}: {resp.text[:200]}")
                    return None

                data = resp.json()
                text = data["choices"][0]["message"]["content"] or ""

                usage = data.get("usage")
                if usage:
                    logger.info(f"[OpenAI] 토큰: {usage.get('prompt_tokens', 0)}→{usage.get('completion_tokens', 0)}")

                return self.extract_json(text)
        except Exception as e:
            logger.warning(f"[OpenAI 에러] {type(e).__name__}: {str(e)[:150]}")
            return None
