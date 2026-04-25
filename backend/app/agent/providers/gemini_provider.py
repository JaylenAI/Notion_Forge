"""Gemini AI Provider — JSON mode + system_instruction 지원"""

import logging
from typing import Any

from app.agent.providers.base import BaseProvider

logger = logging.getLogger("notionforge.providers.gemini")


class GeminiProvider(BaseProvider):
    name = "gemini"
    supports_json_mode = True

    def __init__(self, api_key: str = "", model: str = ""):
        self.api_key = api_key
        self.default_model = model or "gemini-2.5-flash"

    async def call(self, system_prompt: str, user_message: str, model: str = "") -> dict[str, Any] | None:
        try:
            from google import genai
            from google.genai import types

            from app.config import settings

            client = genai.Client(api_key=self.api_key or settings.gemini_api_key)
            response = await client.aio.models.generate_content(
                model=model or self.default_model,
                contents=user_message,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    response_mime_type="application/json",
                    temperature=0.3,
                ),
            )
            text = response.text or ""
            if not text:
                logger.warning("[Gemini] 빈 응답 반환")
                return None

            result = self.extract_json(text)
            if result is None:
                logger.warning(f"[Gemini] JSON 파싱 실패: {text[:200]}")
            return result
        except ImportError:
            logger.warning("[Gemini] google-genai 패키지 미설치")
            return None
        except Exception as e:
            logger.warning(f"[Gemini 에러] {type(e).__name__}: {str(e)[:150]}")
            return None
