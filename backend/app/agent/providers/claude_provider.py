"""Claude AI Provider — 타임아웃 + 에러 핸들링 강화"""

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
                system=system_prompt + "\n\n반드시 유효한 JSON만 응답하세요. 다른 텍스트는 포함하지 마세요.",
                messages=[{"role": "user", "content": user_message}],
            )
            text = response.content[0].text

            logger.info(f"[Claude] 토큰: {response.usage.input_tokens}→{response.usage.output_tokens}")

            return self.extract_json(text)
        except ImportError:
            logger.warning("[Claude] anthropic 패키지 미설치")
            return None
        except Exception as e:
            logger.warning(f"[Claude 에러] {type(e).__name__}: {str(e)[:150]}")
            return None
