"""Claude AI Provider"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.claude")


class ClaudeProvider(BaseProvider):
    name = "claude"

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.default_model = model or "claude-sonnet-4-6"

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        try:
            import anthropic

            from app.config import settings

            client = anthropic.AsyncAnthropic(api_key=self.api_key or settings.anthropic_api_key)
            response = await client.messages.create(
                model=model or self.default_model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return self.extract_json(response.content[0].text)
        except Exception as e:
            logger.warning(f"[Claude 에러] {e}")
            return None
