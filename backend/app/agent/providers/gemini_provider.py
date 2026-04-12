"""Gemini AI Provider"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.gemini")


class GeminiProvider(BaseProvider):
    name = "gemini"

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.default_model = model or "gemini-2.5-flash"

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        try:
            from google import genai

            from app.config import settings

            client = genai.Client(api_key=self.api_key or settings.gemini_api_key)
            response = await client.aio.models.generate_content(
                model=model or self.default_model,
                contents=f"{system_prompt}\n\nUser request: {user_message}",
            )
            return self.extract_json(response.text or "")
        except Exception as e:
            logger.warning(f"[Gemini 에러] {e}")
            return None
